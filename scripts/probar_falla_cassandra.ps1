$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$metricQuery = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22cassandra%22%7D"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("falla-cassandra-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Wait-CassandraMetric {
    param([double]$Expected, [int]$Attempts = 25)
    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5 | Out-Null
            $result = Invoke-RestMethod -Uri $metricQuery -TimeoutSec 5
            if (@($result.data.result).Count -gt 0) {
                $value = [double]$result.data.result[0].value[1]
                if ($value -eq $Expected) { return $value }
            }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

function Wait-CassandraAlert {
    for ($attempt = 1; $attempt -le 25; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts" -TimeoutSec 10
            $alert = @($response.data.alerts) | Where-Object {
                $_.labels.alertname -eq "Fixture2030CassandraDown" -and $_.state -eq "firing"
            } | Select-Object -First 1
            if ($null -ne $alert) { return $alert.state }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

$before = Wait-CassandraMetric -Expected 1
if ($null -eq $before) { throw "Cassandra debe estar UP en Prometheus antes de la prueba." }
$commit = (& git rev-parse HEAD).Trim()
$branch = (& git branch --show-current).Trim()
$stopped = $false
$capturedError = $null
$during = $null
$after = $null
$alertDuring = $null
$degradedObserved = $false
$officialReadAvailable = $false
$startedAt = (Get-Date).ToUniversalTime().ToString("o")

try {
    Write-Host "Deteniendo solamente fixture2030-cassandra..."
    & docker stop fixture2030-cassandra | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener Cassandra." }
    $stopped = $true

    $during = Wait-CassandraMetric -Expected 0
    if ($null -eq $during) { throw "Prometheus no observo Cassandra DOWN." }

    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    $degradedObserved = $health.status -eq "DEGRADED" -and $health.cassandra -eq "DOWN"
    if (-not $degradedObserved) { throw "La API no detecto Cassandra DOWN." }

    $match = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
    $officialReadAvailable = $match.StatusCode -eq 200
    if (-not $officialReadAvailable) { throw "La consulta de partido debio continuar operativa." }

    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001/comentarios?bucket=203006132000&limite=10" -TimeoutSec 5 | Out-Null
        throw "Comentarios debio responder 503 con Cassandra caida."
    } catch {
        if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 503) { throw }
    }

    $alertDuring = Wait-CassandraAlert
    if ($alertDuring -ne "firing") { throw "La alerta Fixture2030CassandraDown no llego a firing." }
    Write-Host "OK: Cassandra DOWN, alerta firing, comentarios 503 y partido disponible."
} catch {
    $capturedError = $_.Exception.Message
} finally {
    if ($stopped) {
        Write-Host "Recuperando fixture2030-cassandra..."
        & docker start fixture2030-cassandra | Out-Null
        if ($LASTEXITCODE -ne 0 -and $null -eq $capturedError) {
            $capturedError = "No se pudo reiniciar Cassandra."
        }
    }
    $after = Wait-CassandraMetric -Expected 1 -Attempts 40
    if ($null -eq $after -and $null -eq $capturedError) {
        $capturedError = "Cassandra no se recupero en la API y Prometheus."
    }

    $record = [ordered]@{
        runId = "falla-cassandra-$runId"
        sourceCommit = $commit
        branch = $branch
        scenario = "falla-controlada-cassandra"
        classification = "medido"
        startedAtUtc = $startedAt
        finishedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        dependencyUpBefore = $before
        dependencyUpDuring = $during
        cassandraDownAlertDuring = $alertDuring
        apiDegradedObserved = $degradedObserved
        officialReadAvailable = $officialReadAvailable
        dependencyUpAfter = $after
        result = $(if ($null -eq $capturedError) { "OK" } else { "ERROR" })
        error = $capturedError
        safety = "Solo se detuvo y reinicio fixture2030-cassandra; no se eliminaron volumenes."
    }
    $record | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "resultado.json")
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: Cassandra recuperada y API nuevamente UP. Evidencia: $outputDir"

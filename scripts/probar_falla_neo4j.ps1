$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$metricQuery = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22neo4j%22%7D"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("falla-neo4j-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Wait-Neo4jMetric {
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

function Wait-Neo4jAlert {
    for ($attempt = 1; $attempt -le 25; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts" -TimeoutSec 10
            $alert = @($response.data.alerts) | Where-Object {
                $_.labels.alertname -eq "Fixture2030Neo4jDown" -and $_.state -eq "firing"
            } | Select-Object -First 1
            if ($null -ne $alert) { return $alert.state }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

$before = Wait-Neo4jMetric -Expected 1
if ($null -eq $before) { throw "Neo4j debe estar UP en Prometheus antes de la prueba." }
$commit = (& git rev-parse HEAD).Trim()
$branch = (& git branch --show-current).Trim()
$stopped = $false
$capturedError = $null
$during = $null
$after = $null
$alertDuring = $null
$degradedObserved = $false
$officialReadAvailable = $false
$graphUnavailable = $false
$startedAt = (Get-Date).ToUniversalTime().ToString("o")

try {
    Write-Host "Deteniendo solamente fixture2030-neo4j..."
    & docker stop fixture2030-neo4j | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener Neo4j." }
    $stopped = $true

    $during = Wait-Neo4jMetric -Expected 0
    if ($null -eq $during) { throw "Prometheus no observo Neo4j DOWN." }

    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    $degradedObserved = $health.status -eq "DEGRADED" -and $health.neo4j -eq "DOWN"
    if (-not $degradedObserved) { throw "La API no detecto Neo4j DOWN." }

    $match = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
    $officialReadAvailable = $match.StatusCode -eq 200
    if (-not $officialReadAvailable) { throw "La consulta oficial de partido debio continuar operativa." }

    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/grafo/resumen" -TimeoutSec 5 | Out-Null
        throw "El grafo debio responder 503 con Neo4j caido."
    } catch {
        if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 503) { throw }
        $graphUnavailable = $true
    }

    $alertDuring = Wait-Neo4jAlert
    if ($alertDuring -ne "firing") { throw "La alerta Fixture2030Neo4jDown no llego a firing." }
    Write-Host "OK: Neo4j DOWN, alerta firing, grafo 503 y partido disponible."
} catch {
    $capturedError = $_.Exception.Message
} finally {
    if ($stopped) {
        Write-Host "Recuperando fixture2030-neo4j..."
        & docker start fixture2030-neo4j | Out-Null
        if ($LASTEXITCODE -ne 0 -and $null -eq $capturedError) {
            $capturedError = "No se pudo reiniciar Neo4j."
        }
    }
    $after = Wait-Neo4jMetric -Expected 1 -Attempts 40
    if ($null -eq $after -and $null -eq $capturedError) {
        $capturedError = "Neo4j no se recupero en la API y Prometheus."
    }

    $record = [ordered]@{
        runId = "falla-neo4j-$runId"
        sourceCommit = $commit
        branch = $branch
        scenario = "falla-controlada-neo4j"
        classification = "medido"
        startedAtUtc = $startedAt
        finishedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        dependencyUpBefore = $before
        dependencyUpDuring = $during
        neo4jDownAlertDuring = $alertDuring
        apiDegradedObserved = $degradedObserved
        officialReadAvailable = $officialReadAvailable
        graphUnavailable = $graphUnavailable
        dependencyUpAfter = $after
        result = $(if ($null -eq $capturedError) { "OK" } else { "ERROR" })
        error = $capturedError
        safety = "Solo se detuvo y reinicio fixture2030-neo4j; no se eliminaron volumenes ni secretos."
    }
    $record | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "resultado.json")
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: Neo4j recuperado y API nuevamente UP. Evidencia: $outputDir"

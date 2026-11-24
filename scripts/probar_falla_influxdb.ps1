$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$metricQuery = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22influxdb%22%7D"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("falla-influxdb-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Wait-InfluxMetric {
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

function Wait-InfluxAlert {
    for ($attempt = 1; $attempt -le 25; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts" -TimeoutSec 10
            $alert = @($response.data.alerts) | Where-Object {
                $_.labels.alertname -eq "Fixture2030InfluxDown" -and $_.state -eq "firing"
            } | Select-Object -First 1
            if ($null -ne $alert) { return $alert.state }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

$before = Wait-InfluxMetric -Expected 1
if ($null -eq $before) { throw "InfluxDB debe estar UP en Prometheus antes de la prueba." }
$commit = (& git rev-parse HEAD).Trim()
$branch = (& git branch --show-current).Trim()
$stopped = $false
$capturedError = $null
$during = $null
$after = $null
$alertDuring = $null
$degradedObserved = $false
$officialReadAvailable = $false
$telemetryUnavailable = $false
$startedAt = (Get-Date).ToUniversalTime().ToString("o")

try {
    Write-Host "Deteniendo solamente fixture2030-influxdb..."
    & docker stop fixture2030-influxdb | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener InfluxDB." }
    $stopped = $true

    $during = Wait-InfluxMetric -Expected 0
    if ($null -eq $during) { throw "Prometheus no observo InfluxDB DOWN." }

    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    $degradedObserved = $health.status -eq "DEGRADED" -and $health.influxdb -eq "DOWN"
    if (-not $degradedObserved) { throw "La API no detecto InfluxDB DOWN." }

    $match = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
    $officialReadAvailable = $match.StatusCode -eq 200
    if (-not $officialReadAvailable) { throw "La consulta oficial de partido debio continuar operativa." }

    $body = @{ muestras=@([ordered]@{ equipoId="EQ-01"; jugadorId="JUG-0001"; x=1.0; y=1.0; periodo=1; segundoPartido=1; capturadoEn="2030-06-13T20:00:01Z" }) } | ConvertTo-Json -Depth 6 -Compress
    try {
        Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$baseUrl/api/v1/partidos/PAR-0001/telemetria/posiciones" -ContentType "application/json" -Body $body -TimeoutSec 5 | Out-Null
        throw "La telemetria debio responder 503 con InfluxDB caido."
    } catch {
        if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 503) { throw }
        $telemetryUnavailable = $true
    }

    $alertDuring = Wait-InfluxAlert
    if ($alertDuring -ne "firing") { throw "La alerta Fixture2030InfluxDown no llego a firing." }
    Write-Host "OK: InfluxDB DOWN, alerta firing, telemetria 503 y partido disponible."
} catch {
    $capturedError = $_.Exception.Message
} finally {
    if ($stopped) {
        Write-Host "Recuperando fixture2030-influxdb..."
        & docker start fixture2030-influxdb | Out-Null
        if ($LASTEXITCODE -ne 0 -and $null -eq $capturedError) {
            $capturedError = "No se pudo reiniciar InfluxDB."
        }
    }
    $after = Wait-InfluxMetric -Expected 1 -Attempts 40
    if ($null -eq $after -and $null -eq $capturedError) {
        $capturedError = "InfluxDB no se recupero en la API y Prometheus."
    }

    $record = [ordered]@{
        runId = "falla-influxdb-$runId"
        sourceCommit = $commit
        branch = $branch
        scenario = "falla-controlada-influxdb"
        classification = "medido"
        startedAtUtc = $startedAt
        finishedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        dependencyUpBefore = $before
        dependencyUpDuring = $during
        influxdbDownAlertDuring = $alertDuring
        apiDegradedObserved = $degradedObserved
        officialReadAvailable = $officialReadAvailable
        telemetryUnavailable = $telemetryUnavailable
        dependencyUpAfter = $after
        result = $(if ($null -eq $capturedError) { "OK" } else { "ERROR" })
        error = $capturedError
        safety = "Solo se detuvo y reinicio fixture2030-influxdb; no se eliminaron volumenes ni secretos."
    }
    $record | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "resultado.json")
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: InfluxDB recuperado y API nuevamente UP. Evidencia: $outputDir"

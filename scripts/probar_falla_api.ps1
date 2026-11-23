$ErrorActionPreference = "Stop"

$prometheusQuery = "http://localhost:9090/api/v1/query?query=up%7Bjob%3D%22fixture2030-api%22%7D"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("falla-api-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Get-ApiUp {
    $response = Invoke-RestMethod -Uri $prometheusQuery -TimeoutSec 10
    if ($response.status -ne "success" -or $response.data.result.Count -eq 0) {
        return $null
    }
    return [double]$response.data.result[0].value[1]
}

function Wait-ApiHealth {
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
            if ($health.status -eq "UP") { return $true }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    return $false
}

function Wait-PrometheusValue {
    param([double]$Expected, [int]$Attempts = 20)
    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            $value = Get-ApiUp
            if ($null -ne $value -and $value -eq $Expected) { return $value }
        } catch {
            # Prometheus puede tardar un scrape en reflejar el cambio.
        }
        Start-Sleep -Seconds 3
    }
    return $null
}

function Wait-AlertFiring {
    for ($attempt = 1; $attempt -le 20; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts" -TimeoutSec 10
            $alert = @($response.data.alerts) | Where-Object {
                $_.labels.alertname -eq "Fixture2030ApiDown" -and $_.state -eq "firing"
            } | Select-Object -First 1
            if ($null -ne $alert) { return $alert.state }
        } catch {
            # La evaluacion de reglas puede tardar varios intervalos.
        }
        Start-Sleep -Seconds 3
    }
    return $null
}

$commit = (& git rev-parse HEAD).Trim()
$before = Get-ApiUp
if ($null -eq $before -or $before -ne 1) {
    throw "La API debe estar UP en Prometheus antes de iniciar la prueba."
}

$apiStopped = $false
$during = $null
$after = $null
$alertStateDuring = $null
$capturedError = $null
$startedAt = (Get-Date).ToUniversalTime().ToString("o")

try {
    Write-Host "Deteniendo solamente fixture2030-api..."
    & docker stop fixture2030-api | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener fixture2030-api." }
    $apiStopped = $true

    $during = Wait-PrometheusValue -Expected 0
    if ($null -eq $during) {
        throw "Prometheus no observo up=0 dentro del tiempo esperado."
    }
    Write-Host "OK: Prometheus detecto la indisponibilidad."

    $alertStateDuring = Wait-AlertFiring
    if ($alertStateDuring -ne "firing") {
        throw "La alerta Fixture2030ApiDown no llego a estado firing."
    }
    Write-Host "OK: la alerta Fixture2030ApiDown esta firing."
} catch {
    $capturedError = $_.Exception.Message
} finally {
    if ($apiStopped) {
        Write-Host "Recuperando fixture2030-api..."
        & docker start fixture2030-api | Out-Null
        if ($LASTEXITCODE -ne 0 -and $null -eq $capturedError) {
            $capturedError = "No se pudo reiniciar fixture2030-api."
        }
    }

    $healthRecovered = Wait-ApiHealth
    if ($healthRecovered) {
        $after = Wait-PrometheusValue -Expected 1
    }
    if ((-not $healthRecovered -or $null -eq $after) -and $null -eq $capturedError) {
        $capturedError = "La API no quedo recuperada en la API y Prometheus."
    }

    $record = [ordered]@{
        runId = "falla-api-$runId"
        commit = $commit
        scenario = "falla-controlada-api"
        classification = "medido"
        startedAtUtc = $startedAt
        finishedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        prometheusUpBefore = $before
        prometheusUpDuring = $during
        apiDownAlertDuring = $alertStateDuring
        prometheusUpAfter = $after
        apiHealthRecovered = $healthRecovered
        result = $(if ($null -eq $capturedError) { "OK" } else { "ERROR" })
        error = $capturedError
        safety = "Solo se detuvo y reinicio fixture2030-api; no se eliminaron volumenes."
    }
    $record | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "resultado.json")
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: falla detectada y servicio recuperado. Evidencia: $outputDir"

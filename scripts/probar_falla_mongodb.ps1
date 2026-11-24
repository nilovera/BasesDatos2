$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$metricQuery = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22mongodb%22%7D"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("falla-mongodb-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Get-MongoMetric {
    $result = Invoke-RestMethod -Uri $metricQuery -TimeoutSec 10
    if ($result.status -ne "success" -or @($result.data.result).Count -eq 0) {
        return $null
    }
    return [double]$result.data.result[0].value[1]
}

function Wait-MongoMetric {
    param([double]$Expected, [int]$Attempts = 25)
    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
            $value = Get-MongoMetric
            if ($null -ne $value -and $value -eq $Expected) { return $value }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

function Wait-MongoAlert {
    for ($attempt = 1; $attempt -le 25; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts" -TimeoutSec 10
            $alert = @($response.data.alerts) | Where-Object {
                $_.labels.alertname -eq "Fixture2030MongoDown" -and $_.state -eq "firing"
            } | Select-Object -First 1
            if ($null -ne $alert) { return $alert.state }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

$commit = (& git rev-parse HEAD).Trim()
$branch = (& git branch --show-current).Trim()
Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5 | Out-Null
$before = Get-MongoMetric
if ($null -eq $before -or $before -ne 1) {
    throw "MongoDB debe estar PRIMARY y su metrica debe valer 1 antes de la prueba."
}

$sessionBody = @{ usuarioId = "USR-0003"; rol = "FAN"; ttlSegundos = 600 } | ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/sesiones" `
    -ContentType "application/json" -Body $sessionBody -TimeoutSec 5

$stopped = $false
$capturedError = $null
$during = $null
$after = $null
$alertDuring = $null
$degradedObserved = $false
$isolatedRedisRead = $false
$startedAt = (Get-Date).ToUniversalTime().ToString("o")

try {
    Write-Host "Deteniendo solamente fixture2030-mongo..."
    & docker stop fixture2030-mongo | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener MongoDB." }
    $stopped = $true

    $during = Wait-MongoMetric -Expected 0
    if ($null -eq $during) { throw "Prometheus no observo MongoDB DOWN." }

    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    $degradedObserved = $health.status -eq "DEGRADED" -and $health.mongodb -eq "DOWN"
    if (-not $degradedObserved) { throw "La API no informo MongoDB DOWN en modo degradado." }

    $redisRead = Invoke-RestMethod -Uri "$baseUrl/api/v1/sesiones/$($session.sesionId)" -TimeoutSec 5
    $isolatedRedisRead = $redisRead.sesionId -eq $session.sesionId
    if (-not $isolatedRedisRead) { throw "La sesion Redis no continuo disponible." }

    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-9999" -TimeoutSec 5 | Out-Null
        throw "La lectura oficial sin cache debio responder 503."
    } catch {
        if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 503) { throw }
    }

    $alertDuring = Wait-MongoAlert
    if ($alertDuring -ne "firing") { throw "La alerta Fixture2030MongoDown no llego a firing." }
    Write-Host "OK: MongoDB DOWN, metrica=0, alerta firing y Redis continuo disponible."
} catch {
    $capturedError = $_.Exception.Message
} finally {
    if ($stopped) {
        Write-Host "Recuperando fixture2030-mongo..."
        & docker start fixture2030-mongo | Out-Null
        if ($LASTEXITCODE -ne 0 -and $null -eq $capturedError) {
            $capturedError = "No se pudo reiniciar MongoDB."
        }
    }
    $after = Wait-MongoMetric -Expected 1 -Attempts 40
    if ($null -eq $after -and $null -eq $capturedError) {
        $capturedError = "MongoDB no se recupero como PRIMARY en la API y Prometheus."
    }

    $record = [ordered]@{
        runId = "falla-mongodb-$runId"
        sourceCommit = $commit
        branch = $branch
        scenario = "falla-controlada-mongodb"
        classification = "medido"
        startedAtUtc = $startedAt
        finishedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        dependencyUpBefore = $before
        dependencyUpDuring = $during
        mongoDownAlertDuring = $alertDuring
        apiDegradedObserved = $degradedObserved
        redisSessionAvailable = $isolatedRedisRead
        dependencyUpAfter = $after
        result = $(if ($null -eq $capturedError) { "OK" } else { "ERROR" })
        error = $capturedError
        safety = "Solo se detuvo y reinicio fixture2030-mongo; no se eliminaron volumenes."
    }
    $record | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "resultado.json")
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: MongoDB recuperado como PRIMARY. Evidencia: $outputDir"

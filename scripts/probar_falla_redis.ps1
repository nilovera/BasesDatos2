$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$prometheusQuery = "http://localhost:9090/api/v1/query?query=redis_up%7Bjob%3D%22fixture2030-redis%22%7D"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("falla-redis-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Wait-RedisMetric {
    param([double]$Expected, [int]$Attempts = 25)
    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            $result = Invoke-RestMethod -Uri $prometheusQuery -TimeoutSec 5
            if (@($result.data.result).Count -gt 0) {
                $value = [double]$result.data.result[0].value[1]
                if ($value -eq $Expected) { return $value }
            }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

function Wait-RedisAlert {
    for ($attempt = 1; $attempt -le 25; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts" -TimeoutSec 10
            $alert = @($response.data.alerts) | Where-Object {
                $_.labels.alertname -eq "Fixture2030RedisDown" -and $_.state -eq "firing"
            } | Select-Object -First 1
            if ($null -ne $alert) { return $alert.state }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

$before = Wait-RedisMetric -Expected 1
if ($null -eq $before) { throw "Redis debe estar UP en Prometheus antes de la prueba." }
$commit = (& git rev-parse HEAD).Trim()
$branch = (& git branch --show-current).Trim()
$body = @{ usuarioId = "USR-0003"; rol = "FAN"; ttlSegundos = 600 } | ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/sesiones" `
    -ContentType "application/json" -Body $body -TimeoutSec 5
$redisStopped = $false
$capturedError = $null
$during = $null
$after = $null
$alertDuring = $null
$degradedObserved = $false
$cacheBypassObserved = $false
$startedAt = (Get-Date).ToUniversalTime().ToString("o")

try {
    Write-Host "Deteniendo solamente fixture2030-redis..."
    & docker stop fixture2030-redis | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener Redis." }
    $redisStopped = $true

    $during = Wait-RedisMetric -Expected 0
    if ($null -eq $during) { throw "Prometheus no observo redis_up=0." }

    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    $degradedObserved = $health.status -eq "DEGRADED" -and $health.redis -eq "DOWN"
    if (-not $degradedObserved) { throw "La API no distinguio la dependencia Redis caida." }

    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/sesiones/$($session.sesionId)" `
            -TimeoutSec 5 | Out-Null
        throw "La consulta de sesion debio responder 503."
    } catch {
        $response = $_.Exception.Response
        if ($null -eq $response -or [int]$response.StatusCode -ne 503) { throw }
    }

    $match = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
    $cacheBypassObserved = $match.StatusCode -eq 200 -and $match.Headers["X-Cache"] -eq "BYPASS"
    if (-not $cacheBypassObserved) { throw "Cache-Aside no uso MongoDB como fallback." }

    $alertDuring = Wait-RedisAlert
    if ($alertDuring -ne "firing") { throw "La alerta Fixture2030RedisDown no llego a firing." }
    Write-Host "OK: Redis DOWN, alerta firing, sesion 503 y partido BYPASS desde MongoDB."
} catch {
    $capturedError = $_.Exception.Message
} finally {
    if ($redisStopped) {
        Write-Host "Recuperando fixture2030-redis..."
        & docker start fixture2030-redis | Out-Null
        if ($LASTEXITCODE -ne 0 -and $null -eq $capturedError) {
            $capturedError = "No se pudo reiniciar Redis."
        }
    }

    $recovered = $false
    for ($attempt = 1; $attempt -le 30; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
            if ($health.redis -eq "UP") { $recovered = $true; break }
        } catch { }
        Start-Sleep -Seconds 2
    }
    if ($recovered) { $after = Wait-RedisMetric -Expected 1 }
    if ((-not $recovered -or $null -eq $after) -and $null -eq $capturedError) {
        $capturedError = "Redis no se recupero en la API y Prometheus."
    }

    $record = [ordered]@{
        runId = "falla-redis-$runId"
        sourceCommit = $commit
        branch = $branch
        scenario = "falla-controlada-redis"
        classification = "medido"
        startedAtUtc = $startedAt
        finishedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        redisUpBefore = $before
        redisUpDuring = $during
        redisDownAlertDuring = $alertDuring
        apiDegradedObserved = $degradedObserved
        cacheBypassObserved = $cacheBypassObserved
        redisUpAfter = $after
        result = $(if ($null -eq $capturedError) { "OK" } else { "ERROR" })
        error = $capturedError
        safety = "Solo se detuvo y reinicio fixture2030-redis; no se eliminaron volumenes."
    }
    $record | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "resultado.json")
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: Redis recuperado y API nuevamente UP. Evidencia: $outputDir"

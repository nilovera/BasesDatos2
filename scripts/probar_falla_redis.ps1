$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$prometheusQuery = "http://localhost:9090/api/v1/query?query=redis_up%7Bjob%3D%22fixture2030-redis%22%7D"

function Wait-RedisMetric {
    param([double]$Expected)
    for ($attempt = 1; $attempt -le 20; $attempt++) {
        try {
            $result = Invoke-RestMethod -Uri $prometheusQuery -TimeoutSec 5
            if ($result.data.result.Count -gt 0) {
                $value = [double]$result.data.result[0].value[1]
                if ($value -eq $Expected) { return $value }
            }
        } catch {
            # Esperar el siguiente scrape.
        }
        Start-Sleep -Seconds 3
    }
    return $null
}

$body = @{ usuarioId = "USR-0003"; rol = "FAN"; ttlSegundos = 600 } | ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/sesiones" `
    -ContentType "application/json" -Body $body -TimeoutSec 5
$redisStopped = $false
$capturedError = $null

try {
    Write-Host "Deteniendo solamente fixture2030-redis..."
    & docker stop fixture2030-redis | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener Redis." }
    $redisStopped = $true

    $metricDown = Wait-RedisMetric -Expected 0
    if ($null -eq $metricDown) { throw "Prometheus no observo redis_up=0." }

    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
    if ($health.status -ne "DEGRADED" -or $health.redis -ne "DOWN") {
        throw "La API no distinguio la dependencia Redis caida."
    }

    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/sesiones/$($session.sesionId)" `
            -TimeoutSec 5 | Out-Null
        throw "La consulta de sesion debio responder 503."
    } catch {
        $response = $_.Exception.Response
        if ($null -eq $response -or [int]$response.StatusCode -ne 503) { throw }
    }

    $match = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
    if ($match.StatusCode -ne 200 -or $match.Headers["X-Cache"] -ne "BYPASS") {
        throw "Cache-Aside no uso MongoDB como fallback."
    }
    Write-Host "OK: Redis DOWN, sesion 503 y partido BYPASS desde MongoDB."
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
        } catch {
            # La API puede seguir UP mientras Redis inicia.
        }
        Start-Sleep -Seconds 2
    }
    if (-not $recovered -and $null -eq $capturedError) {
        $capturedError = "Redis no se recupero en la API."
    }
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: Redis recuperado y API nuevamente UP."

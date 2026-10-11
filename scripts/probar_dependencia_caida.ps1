$ErrorActionPreference = "Stop"

$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot

$evidencePath = Join-Path `
    $projectRoot `
    "docs\evidencia\10_dependencia_redis_caida.txt"

$redisContainer = "fixture2030-redis"
$redisAvailable = $false

Start-Transcript `
    -Path $evidencePath `
    -Force

try {
    Write-Host "=== HITO 10 - DEPENDENCIA CAIDA ==="
    Write-Host (
        "Fecha de ejecucion: " +
        (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
    )
    Write-Host "Dependencia seleccionada: Redis"
    Write-Host ""

    try {
        Write-Host "=== 1. DETENER REDIS TEMPORALMENTE ==="

        docker stop $redisContainer

        Start-Sleep -Seconds 2

        Write-Host ""
        Write-Host "=== 2. ENDPOINT REDIS - ESPERADO 503 ==="

        curl.exe -s -i `
            "http://127.0.0.1:8000/api/v1/sesiones/SES-DEPENDENCIA-CAIDA"

        Write-Host ""
        Write-Host ""
        Write-Host "=== 3. MONGODB CONTINUA DISPONIBLE - ESPERADO 200 ==="

        curl.exe -s -i `
            "http://127.0.0.1:8000/api/v1/equipos/EQ-01"

        Write-Host ""
    }
    finally {
        Write-Host ""
        Write-Host "=== 4. REINICIAR REDIS ==="

        docker start $redisContainer |
            Out-Host

        for ($attempt = 1; $attempt -le 30; $attempt++) {
            Start-Sleep -Seconds 1

            $ping = docker exec `
                $redisContainer `
                redis-cli PING `
                2>$null

            if (
                $LASTEXITCODE -eq 0 -and
                $ping -match "PONG"
            ) {
                $redisAvailable = $true
                break
            }
        }

        if ($redisAvailable) {
            Write-Host "Redis recuperado: PONG"
        } else {
            Write-Host "Redis no se recupero dentro del plazo."
        }
    }

    if (-not $redisAvailable) {
        throw "Redis no pudo reiniciarse correctamente."
    }

    Write-Host ""
    Write-Host "=== 5. PREPARAR SESION POSTERIOR A LA RECUPERACION ==="

    $lastAccess = [DateTime]::UtcNow.ToString(
        "yyyy-MM-ddTHH:mm:ssZ"
    )

    docker exec `
        $redisContainer `
        redis-cli HSET `
        "sesion:SES-API-RECUPERADA" `
        sesion_id "SES-API-RECUPERADA" `
        usuario_id "USR-TEST" `
        rol "fan" `
        ultimo_acceso $lastAccess `
        estado "activa" `
        partido_actual "PAR-0001" `
        acciones "1"

    docker exec `
        $redisContainer `
        redis-cli EXPIRE `
        "sesion:SES-API-RECUPERADA" `
        300

    Write-Host ""
    Write-Host "=== 6. ENDPOINT REDIS RECUPERADO - ESPERADO 200 ==="

    curl.exe -s -i `
        "http://127.0.0.1:8000/api/v1/sesiones/SES-API-RECUPERADA"

    Write-Host ""
    Write-Host ""
    Write-Host "=== 7. LIMPIEZA DE LA SESION DE PRUEBA ==="

    docker exec `
        $redisContainer `
        redis-cli DEL `
        "sesion:SES-API-RECUPERADA"

    Write-Host ""
    Write-Host "=== PRUEBA FINALIZADA ==="
    Write-Host "Redis caido: 503 esperado"
    Write-Host "MongoDB durante la falla: 200 esperado"
    Write-Host "Redis recuperado: 200 esperado"
}
finally {
    Stop-Transcript
}
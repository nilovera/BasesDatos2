$ErrorActionPreference = "Stop"

$projectRoot = "C:\fixture2030-api"
$python = "$projectRoot\.venv\Scripts\python.exe"
$postmanDirectory = "$projectRoot\postman"
$evidenceDirectory = "$projectRoot\docs\evidencia"
$transcriptPath = (
    "$evidenceDirectory\13_postman_newman.txt"
)
$jsonReportPath = (
    "$evidenceDirectory\13_postman_newman.json"
)

$newmanExitCode = 1
$temporaryApi = $null

New-Item `
    -ItemType Directory `
    -Force `
    $evidenceDirectory |
    Out-Null

Start-Transcript `
    -Path $transcriptPath `
    -Force

try {
    Write-Host "=== HITO 10 - POSTMAN CON NEWMAN ==="

    $executionDate = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"

    Write-Host "Fecha de ejecucion: $executionDate"
    Write-Host "Coleccion: Fixture2030"
    Write-Host "Ejecucion: Newman dentro de Docker"

    Write-Host "`n=== 1. DETENER API ACTUAL ==="

    if (Test-Path "$projectRoot\.api.pid") {
        $previousPid = [int](
            Get-Content `
                "$projectRoot\.api.pid" `
                -Raw
        )

        Stop-Process `
            -Id $previousPid `
            -Force `
            -ErrorAction SilentlyContinue
    }

    Start-Sleep -Seconds 2

    Get-NetTCPConnection `
        -LocalPort 8000 `
        -State Listen `
        -ErrorAction SilentlyContinue |
        Select-Object `
            -ExpandProperty OwningProcess `
            -Unique |
        ForEach-Object {
            Stop-Process `
                -Id $_ `
                -Force `
                -ErrorAction SilentlyContinue
        }

    Start-Sleep -Seconds 2

    Write-Host "`n=== 2. INICIAR API PARA DOCKER ==="

    $temporaryApi = Start-Process `
        -FilePath $python `
        -ArgumentList @(
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000"
        ) `
        -WorkingDirectory $projectRoot `
        -RedirectStandardOutput (
            "$projectRoot\logs\postman.stdout.log"
        ) `
        -RedirectStandardError (
            "$projectRoot\logs\postman.stderr.log"
        ) `
        -PassThru

    $temporaryApi.Id |
        Set-Content "$projectRoot\.api.pid"

    $apiAvailable = $false

    for ($attempt = 1; $attempt -le 30; $attempt++) {
        Start-Sleep -Seconds 1

        try {
            Invoke-WebRequest `
                -Uri "http://127.0.0.1:8000/health" `
                -UseBasicParsing |
                Out-Null

            $apiAvailable = $true
            break
        } catch {
            # Continúa esperando.
        }
    }

    if (-not $apiAvailable) {
        Get-Content `
            "$projectRoot\logs\postman.stderr.log" `
            -Tail 120

        throw "La API temporal no quedo disponible."
    }

    Write-Host "API temporal disponible."

    Write-Host "`n=== 3. PREPARAR SESION REDIS ==="

    $redisKey = "sesion:SES-POSTMAN-0001"
    $lastAccess = (
        Get-Date
    ).ToUniversalTime().ToString(
        "yyyy-MM-ddTHH:mm:ssZ"
    )

    docker exec fixture2030-redis `
        redis-cli DEL $redisKey

    docker exec fixture2030-redis `
        redis-cli HSET `
        $redisKey `
        sesion_id "SES-POSTMAN-0001" `
        usuario_id "USR-POSTMAN" `
        rol "fan" `
        ultimo_acceso $lastAccess `
        estado "activa" `
        partido_actual "PAR-0001" `
        acciones "1"

    docker exec fixture2030-redis `
        redis-cli EXPIRE $redisKey 600

    Write-Host "Sesion temporal preparada."

    Write-Host "`n=== 4. EJECUTAR COLECCION ==="

    docker run --rm `
        --add-host `
        "host.docker.internal:host-gateway" `
        --mount `
        "type=bind,source=$postmanDirectory,target=/etc/newman,readonly" `
        --mount `
        "type=bind,source=$evidenceDirectory,target=/newman-results" `
        postman/newman:alpine `
        run `
        "/etc/newman/Fixture2030.postman_collection.json" `
        --environment `
        "/etc/newman/Fixture2030.postman_environment.json" `
        --env-var `
        "base_url=http://host.docker.internal:8000" `
        --reporters "cli,json" `
        --reporter-json-export `
        "/newman-results/13_postman_newman.json"

    $newmanExitCode = $LASTEXITCODE

    Write-Host "`nCodigo de salida Newman: $newmanExitCode"

    if ($newmanExitCode -ne 0) {
        throw "Newman encontro pruebas fallidas."
    }

    Write-Host "`n=== RESULTADO: POSTMAN APROBADO ==="
}
finally {
    Write-Host "`n=== 5. LIMPIEZA ==="

    docker exec fixture2030-redis `
        redis-cli DEL `
        "sesion:SES-POSTMAN-0001" `
        2>$null |
        Out-Null

    if ($null -ne $temporaryApi) {
        Stop-Process `
            -Id $temporaryApi.Id `
            -Force `
            -ErrorAction SilentlyContinue
    }

    Start-Sleep -Seconds 2

    Write-Host "Restableciendo API local."

    powershell.exe `
        -NoProfile `
        -ExecutionPolicy Bypass `
        -File "$projectRoot\scripts\reiniciar_api.ps1"

    Stop-Transcript
}

if ($newmanExitCode -ne 0) {
    exit $newmanExitCode
}

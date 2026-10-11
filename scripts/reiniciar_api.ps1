$ErrorActionPreference = "Stop"

$projectRoot = Split-Path $PSScriptRoot -Parent
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pidFile = Join-Path $projectRoot ".api.pid"
$logs = Join-Path $projectRoot "logs"

Set-Location $projectRoot
New-Item -ItemType Directory -Force $logs |
    Out-Null

if (Test-Path $pidFile) {
    $apiPidAnterior = [int](
        Get-Content $pidFile -Raw
    )

    Stop-Process `
        -Id $apiPidAnterior `
        -Force `
        -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2

Get-NetTCPConnection `
    -LocalPort 8000 `
    -State Listen `
    -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object {
        Stop-Process `
            -Id $_ `
            -Force `
            -ErrorAction SilentlyContinue
    }

Start-Sleep -Seconds 2

$apiProcess = Start-Process `
    -FilePath $python `
    -ArgumentList @(
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
    ) `
    -WorkingDirectory $projectRoot `
    -RedirectStandardOutput `
        (Join-Path $logs "api.stdout.log") `
    -RedirectStandardError `
        (Join-Path $logs "api.stderr.log") `
    -PassThru

$apiProcess.Id | Set-Content $pidFile

$disponible = $false

for ($intento = 1; $intento -le 30; $intento++) {
    Start-Sleep -Seconds 1

    try {
        Invoke-WebRequest `
            -Uri "http://127.0.0.1:8000/health" `
            -UseBasicParsing |
            Out-Null

        $disponible = $true
        break
    } catch {
        # Continúa esperando.
    }
}

if (-not $disponible) {
    Get-Content `
        (Join-Path $logs "api.stderr.log") `
        -Tail 120

    throw "La API no quedó disponible."
}

Write-Host "API disponible en http://127.0.0.1:8000"
Write-Host "Swagger: http://127.0.0.1:8000/docs"
Write-Host "PID: $($apiProcess.Id)"
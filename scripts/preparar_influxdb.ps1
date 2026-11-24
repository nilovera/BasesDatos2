$ErrorActionPreference = "Stop"

$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$secretDir = Join-Path $projectRoot ".secretos"
$tokenJson = Join-Path $secretDir "influxdb-admin-token.json"
$tokenRaw = Join-Path $secretDir "influxdb-admin-token.txt"
$image = "influxdb:3.12.3-core"

function Read-ValidToken {
    if (-not (Test-Path $tokenJson)) { return $null }
    try {
        $document = Get-Content -Raw -Path $tokenJson | ConvertFrom-Json
        $token = [string]$document.token
        if ($token -match '^apiv3_[A-Za-z0-9_-]{16,}$') { return $token }
    } catch {
        return $null
    }
    return $null
}

New-Item -ItemType Directory -Force -Path $secretDir | Out-Null
$token = Read-ValidToken

if ($null -eq $token) {
    if (Test-Path $tokenJson) {
        throw "El token JSON de InfluxDB existe pero es invalido. Revise $tokenJson; no se reemplaza automaticamente."
    }

    Write-Host "Generando token administrativo local de InfluxDB..."
    # La CLI muestra la credencial en stdout aunque también use --output-file.
    # Se descarta toda la salida para que el token nunca quede en consola,
    # historial, CI ni evidencia. El código de salida sigue siendo verificado.
    & docker run --rm `
        --mount "type=bind,source=$secretDir,target=/secrets" `
        $image `
        influxdb3 create token --admin `
        --name fixture2030-local `
        --offline `
        --output-file /secrets/influxdb-admin-token.json *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo generar el token local de InfluxDB (codigo $LASTEXITCODE)."
    }
    $token = Read-ValidToken
    if ($null -eq $token) {
        throw "InfluxDB genero un archivo de token que no cumple el formato esperado."
    }
}

[System.IO.File]::WriteAllText(
    $tokenRaw,
    $token,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "OK: secretos locales de InfluxDB preparados y excluidos de Git/Docker build."

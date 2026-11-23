$ErrorActionPreference = "Stop"

Write-Host "Deteniendo la plataforma sin borrar volumenes..."
docker compose down
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo detener la plataforma (codigo $LASTEXITCODE)."
}

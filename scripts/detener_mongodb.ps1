$ErrorActionPreference = "Stop"

Write-Host "Deteniendo el entorno sin borrar el volumen de MongoDB..."
docker compose down

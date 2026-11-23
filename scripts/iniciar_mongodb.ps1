$ErrorActionPreference = "Stop"

Write-Host "Iniciando MongoDB de Fixture2030..."
docker compose up -d mongo
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo iniciar el servicio mongo (codigo $LASTEXITCODE)."
}

Write-Host "Inicializando replica set, esquema y catalogo..."
docker compose run --rm mongo-init
if ($LASTEXITCODE -ne 0) {
    throw "Fallo la inicializacion de MongoDB (codigo $LASTEXITCODE)."
}

Write-Host "Estado del servicio:"
docker compose ps mongo
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo consultar el estado de MongoDB (codigo $LASTEXITCODE)."
}

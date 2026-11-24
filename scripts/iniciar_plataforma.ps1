$ErrorActionPreference = "Stop"

Write-Host "Construyendo e iniciando API, MongoDB, Redis, Cassandra, Prometheus y Grafana..."
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo iniciar la plataforma (codigo $LASTEXITCODE)."
}

Write-Host "Estado de los servicios:"
docker compose ps
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo consultar el estado (codigo $LASTEXITCODE)."
}

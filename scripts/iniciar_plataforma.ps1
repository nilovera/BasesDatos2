$ErrorActionPreference = "Stop"

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "preparar_influxdb.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron preparar los secretos de InfluxDB (codigo $LASTEXITCODE)."
}

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "preparar_neo4j.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron preparar los secretos de Neo4j (codigo $LASTEXITCODE)."
}

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "preparar_datamart.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo preparar el secreto del Data Mart (codigo $LASTEXITCODE)."
}

Write-Host "Construyendo e iniciando plataforma operacional, Data Mart, Prometheus y Grafana..."
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo iniciar la plataforma (codigo $LASTEXITCODE)."
}

# Prometheus admite recarga por SIGHUP. Esto evita conservar reglas antiguas
# cuando el contenedor ya existia antes de actualizar el repositorio.
docker kill --signal=SIGHUP fixture2030-prometheus | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo recargar la configuracion de Prometheus."
}

Write-Host "Estado de los servicios:"
docker compose ps
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo consultar el estado (codigo $LASTEXITCODE)."
}

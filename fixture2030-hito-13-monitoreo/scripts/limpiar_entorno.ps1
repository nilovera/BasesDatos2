# HITO 13 - LIMPIAR ENTORNO
# Detiene el stack de monitoreo SIN tocar las bases del Fixture ni sus volumenes (RNF11).
#   - Vuelve a iniciar cualquiera de las seis bases que haya quedado detenida (prueba interrumpida).
#   - docker compose down del proyecto fixture2030-monitoreo (conserva el historial de Prometheus/Grafana).
# Uso (desde la carpeta raiz de la API):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\limpiar_entorno.ps1
#   ... -BorrarHistorial   borra ADEMAS los volumenes prometheus_data y grafana_data de ESTE proyecto
#   ... -DetenerApi        detiene tambien la API (uvicorn)
param([switch]$BorrarHistorial, [switch]$DetenerApi)
$hito = Split-Path $PSScriptRoot -Parent
$api  = Split-Path $hito -Parent
Set-Location $api
$ErrorActionPreference = "Continue"
Write-Host "=== HITO 13 - LIMPIAR ENTORNO ===" -ForegroundColor Cyan

Write-Host "1) Bases del Fixture: se aseguran iniciadas (nunca se borran)..."
foreach ($c in @("fixture2030-mongodb", "fixture2030-neo4j", "fixture2030-cassandra",
                 "fixture2030-redis", "fixture2030-influxdb", "fixture2030-iris")) {
    $estado = (docker inspect -f "{{.State.Running}}" $c 2>$null) -join ""
    if ($estado -eq "false") { docker start $c | Out-Null; Write-Host "   $c estaba detenida: iniciada" }
    elseif ($estado -eq "true") { Write-Host "   $c corriendo" }
}

Write-Host "2) Stack de monitoreo..."
$compose = @("compose", "-f", (Join-Path $hito "docker-compose.yml"), "--project-directory", $hito, "--profile", "contenedores")
if ($BorrarHistorial) {
    Write-Host "   down -v: se borran SOLO los volumenes del proyecto fixture2030-monitoreo (historial de metricas y Grafana)"
    docker @compose down -v
} else {
    docker @compose down
}

if ($DetenerApi) {
    Write-Host "3) Deteniendo la API..."
    $pidFile = Join-Path $api ".api.pid"
    if (Test-Path $pidFile) { Stop-Process -Id ([int](Get-Content $pidFile -Raw)) -Force -ErrorAction SilentlyContinue }
}

Write-Host ""
Write-Host "Listo. No se borraron datos de MongoDB, Neo4j, Cassandra, Redis, InfluxDB ni IRIS."
Write-Host "Las sesiones sinteticas SES-H12-* de Redis vencen solas (TTL 4 h); los .env y .secretos locales se conservan."

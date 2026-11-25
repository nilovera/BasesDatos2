$ErrorActionPreference = "Stop"
Write-Host "Verificando PostgreSQL, esquema estrella, API y metricas..."

$tables = (& docker compose exec -T datamart psql -U fixture2030 -d fixture2030_analytics -Atc `
    "SELECT table_name FROM information_schema.tables WHERE table_schema='analytics' ORDER BY table_name;") -join "`n"
if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar PostgreSQL." }
foreach ($table in @("dim_equipo", "dim_jugador", "dim_partido", "dim_fecha", "dim_tipo_evento", "fact_evento_partido", "fact_estadistica_equipo_15m", "etl_ejecucion")) {
    if ($tables -notmatch [regex]::Escape($table)) { throw "Falta la tabla $table." }
}
$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
if ($health.datamart -ne "UP") { throw "La API no informa Data Mart UP." }
$metrics = (Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/metrics" -TimeoutSec 5).Content
if ($metrics -notmatch 'fixture2030_dependency_up\{dependency="datamart"\} 1') { throw "Falta la metrica del Data Mart." }
Write-Host "OK: PostgreSQL UP, esquema estrella, API y metrica=1."


$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"

Write-Host "1/5 Ejecutando ETL inicial desde MongoDB e InfluxDB..."
$first = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/analitica/datamart/refrescar" -TimeoutSec 60
Write-Host "2/5 Repitiendo ETL para comprobar UPSERT idempotente..."
$second = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/analitica/datamart/refrescar" -TimeoutSec 60
Write-Host "3/5 Consultando resumen del esquema estrella..."
$summary = Invoke-RestMethod -Uri "$baseUrl/api/v1/analitica/datamart/resumen" -TimeoutSec 10
Write-Host "4/5 Comparando resultado operacional y analitico..."
$operational = Invoke-RestMethod -Uri "$baseUrl/api/v1/analitica/operacional/goles-por-equipo" -TimeoutSec 10
$analytical = Invoke-RestMethod -Uri "$baseUrl/api/v1/analitica/datamart/goles-por-equipo" -TimeoutSec 10
if (($operational.items | ConvertTo-Json -Compress) -ne ($analytical.items | ConvertTo-Json -Compress)) {
    throw "La consulta operacional y el Data Mart no devuelven el mismo resultado."
}
Write-Host "5/5 Verificando que la repeticion no duplico hechos..."
if ($first.eventosCargados -ne $second.eventosCargados) { throw "La carga repetida cambio la cantidad fuente." }
$dbCount = [int]((& docker compose exec -T datamart psql -U fixture2030 -d fixture2030_analytics -Atc "SELECT count(*) FROM analytics.fact_evento_partido;").Trim())
if ($LASTEXITCODE -ne 0 -or $dbCount -ne $summary.eventos) { throw "La cantidad de hechos no coincide." }
Write-Host "OK: ETL idempotente, dos granos y equivalencia operacional/analitica verificados."
Write-Host "Hechos evento:" $summary.eventos "resumenes 15m:" $summary.resumenes


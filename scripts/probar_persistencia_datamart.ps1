$ErrorActionPreference = "Stop"
Write-Host "1/3 Refrescando y registrando cantidad de hechos..."
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/analitica/datamart/refrescar" -TimeoutSec 60 | Out-Null
$before = [int]((& docker compose exec -T datamart psql -U fixture2030 -d fixture2030_analytics -Atc "SELECT count(*) FROM analytics.fact_evento_partido;").Trim())
Write-Host "2/3 Reiniciando solamente el Data Mart..."
docker compose restart datamart
if ($LASTEXITCODE -ne 0) { throw "No se pudo reiniciar el Data Mart." }
for ($i=0; $i -lt 30; $i++) {
    $state = (& docker inspect fixture2030-datamart --format "{{.State.Health.Status}}" 2>$null)
    if ($state -eq "healthy") { break }
    Start-Sleep -Seconds 2
}
Write-Host "3/3 Verificando el volumen nombrado..."
$after = [int]((& docker compose exec -T datamart psql -U fixture2030 -d fixture2030_analytics -Atc "SELECT count(*) FROM analytics.fact_evento_partido;").Trim())
if ($before -ne $after) { throw "La cantidad de hechos cambio despues del reinicio." }
Write-Host "OK: el volumen nombrado conservo $after hechos despues del reinicio."


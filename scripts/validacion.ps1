$TokenPath = Join-Path $PSScriptRoot "..\.influxdb3-token"

if (-not (Test-Path $TokenPath)) {
    throw "No se encontro .influxdb3-token."
}

$env:INFLUXDB3_AUTH_TOKEN = Get-Content -Raw $TokenPath

Write-Host "=== VALIDACION DE BASES ==="

docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 show databases

Write-Host ""
Write-Host "=== VALIDACION DE DATOS DETALLADOS ==="

docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 query `
    --database fixture2030_detalle `
    "SELECT COUNT(*) AS puntos, COUNT(DISTINCT equipo_id) AS equipos, MIN(time) AS inicio, MAX(time) AS fin FROM estadisticas_equipo WHERE partido_id = 'PAR-0001'"

Write-Host ""
Write-Host "=== DISTRIBUCION POR EQUIPO ==="

docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 query `
    --database fixture2030_detalle `
    "SELECT equipo_id, COUNT(*) AS puntos FROM estadisticas_equipo WHERE partido_id = 'PAR-0001' GROUP BY equipo_id ORDER BY equipo_id"

Write-Host ""
Write-Host "=== VALIDACION HISTORICA ==="

docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 query `
    --database fixture2030_historico `
    "SELECT COUNT(*) AS resumenes, COUNT(DISTINCT equipo_id) AS equipos, MIN(time) AS inicio, MAX(time) AS fin FROM resumen_equipo_minuto"

Write-Host ""
Write-Host "=== VALIDACION FINALIZADA ==="

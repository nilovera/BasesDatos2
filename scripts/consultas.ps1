$TokenPath = Join-Path $PSScriptRoot "..\.influxdb3-token"

if (-not (Test-Path $TokenPath)) {
    throw "No se encontro .influxdb3-token."
}

$env:INFLUXDB3_AUTH_TOKEN = Get-Content -Raw $TokenPath

function Ejecutar-Consulta {
    param(
        [string]$Titulo,
        [string]$Sql
    )

    Write-Host ""
    Write-Host "=== $Titulo ==="

    docker exec --env INFLUXDB3_AUTH_TOKEN `
        fixture2030-influxdb `
        influxdb3 query `
        --database fixture2030_detalle `
        $Sql

    if ($LASTEXITCODE -ne 0) {
        throw "Fallo la consulta: $Titulo"
    }
}

Ejecutar-Consulta "1. VENTANA TEMPORAL DE ARGENTINA" @"
SELECT time, equipo_id, posesion_pct, pases_intervalo, tiros_acumulados
FROM estadisticas_equipo
WHERE partido_id = 'PAR-0001'
  AND equipo_id = 'ARG'
  AND time >= '2030-06-13T20:40:00Z'
  AND time <  '2030-06-13T20:41:00Z'
ORDER BY time
"@

Ejecutar-Consulta "2. COMPARACION ENTRE EQUIPOS" @"
SELECT equipo_id,
       ROUND(AVG(posesion_pct), 2) AS posesion_promedio,
       SUM(pases_intervalo) AS pases_totales,
       MAX(tiros_acumulados) AS tiros_finales,
       COUNT(*) AS muestras
FROM estadisticas_equipo
WHERE partido_id = 'PAR-0001'
  AND time >= '2030-06-13T20:00:00Z'
  AND time <  '2030-06-13T21:30:00Z'
GROUP BY equipo_id
ORDER BY equipo_id
"@

Ejecutar-Consulta "3. AGREGACION TEMPORAL CADA 15 MINUTOS" @"
SELECT date_bin(INTERVAL '15 minutes', time) AS ventana,
       equipo_id,
       ROUND(AVG(posesion_pct), 2) AS posesion_promedio,
       SUM(pases_intervalo) AS pases_ventana,
       MAX(tiros_acumulados) AS tiros_acumulados
FROM estadisticas_equipo
WHERE partido_id = 'PAR-0001'
  AND time >= '2030-06-13T20:00:00Z'
  AND time <  '2030-06-13T21:30:00Z'
GROUP BY ventana, equipo_id
ORDER BY ventana, equipo_id
"@

Write-Host ""
Write-Host "=== CONSULTAS FINALIZADAS ==="

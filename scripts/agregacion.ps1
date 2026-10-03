$TokenPath = Join-Path $PSScriptRoot "..\.influxdb3-token"
$ArchivoResumen = Join-Path $PSScriptRoot "..\datos\resumen_15m.lp"

if (-not (Test-Path $TokenPath)) {
    throw "No se encontro .influxdb3-token."
}

$env:INFLUXDB3_AUTH_TOKEN = Get-Content -Raw $TokenPath

$Sql = @"
SELECT date_bin(INTERVAL '15 minutes', time) AS ventana,
       equipo_id,
       ROUND(AVG(posesion_pct), 2) AS posesion_promedio,
       SUM(pases_intervalo) AS pases_total,
       COUNT(*) AS muestras
FROM estadisticas_equipo
WHERE partido_id = 'PAR-0001'
  AND time >= '2030-06-13T20:00:00Z'
  AND time <  '2030-06-13T21:30:00Z'
GROUP BY ventana, equipo_id
ORDER BY ventana, equipo_id
"@

$SalidaJson = docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 query `
    --database fixture2030_detalle `
    --format json `
    $Sql

if ($LASTEXITCODE -ne 0) {
    throw "No se pudo obtener la agregacion."
}

$Resultados = ($SalidaJson -join "`n") | ConvertFrom-Json
$Lineas = [System.Collections.Generic.List[string]]::new()
$Cultura = [System.Globalization.CultureInfo]::InvariantCulture

foreach ($Fila in $Resultados) {
    $TextoFecha = ([string]$Fila.ventana).TrimEnd("Z")

    $Inicio = [DateTimeOffset]::ParseExact(
        $TextoFecha,
        "yyyy-MM-ddTHH:mm:ss",
        $Cultura,
        [System.Globalization.DateTimeStyles]::AssumeUniversal
    )

    $Fin = $Inicio.AddMinutes(15)
    $Posesion = ([double]$Fila.posesion_promedio).ToString($Cultura)
    $Pases = [long]$Fila.pases_total
    $Muestras = [long]$Fila.muestras

    $Lineas.Add(
        "resumen_equipo_minuto,partido_id=PAR-0001,equipo_id=$($Fila.equipo_id) posesion_promedio=$Posesion,pases_total=${Pases}i,muestras=${Muestras}i,ventana_inicio_ms=$($Inicio.ToUnixTimeMilliseconds())i,ventana_fin_ms=$($Fin.ToUnixTimeMilliseconds())i $($Inicio.ToUnixTimeSeconds())"
    )
}

$Utf8SinBom = New-Object System.Text.UTF8Encoding($false)
$Contenido = ($Lineas -join "`n") + "`n"

[System.IO.File]::WriteAllText(
    $ArchivoResumen,
    $Contenido,
    $Utf8SinBom
)

docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 write `
    --database fixture2030_historico `
    --precision s `
    --file /datos/resumen_15m.lp

if ($LASTEXITCODE -ne 0) {
    throw "No se pudo cargar el resumen historico."
}

Write-Host "=== DOWNSAMPLING FINALIZADO ==="
Write-Host "Puntos originales: 1080"
Write-Host "Resumenes historicos: $($Lineas.Count)"
Write-Host "Granularidad historica: 15 minutos"

docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 query `
    --database fixture2030_historico `
    "SELECT time, equipo_id, posesion_promedio, pases_total, muestras FROM resumen_equipo_minuto ORDER BY time, equipo_id"


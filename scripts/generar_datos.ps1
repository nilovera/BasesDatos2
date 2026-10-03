$CarpetaDatos = Join-Path $PSScriptRoot "..\datos"
$ArchivoSalida = Join-Path $CarpetaDatos "estadisticas_equipo.lp"

New-Item -ItemType Directory -Force $CarpetaDatos | Out-Null

$Inicio = [DateTimeOffset]::Parse("2030-06-13T20:00:00Z")
$Lineas = [System.Collections.Generic.List[string]]::new()

for ($i = 0; $i -lt 540; $i++) {
    $Timestamp = $Inicio.AddSeconds($i * 10).ToUnixTimeSeconds()

    $PosesionArgentina = 50 + [math]::Round(8 * [math]::Sin($i / 35), 2)
    $PosesionMexico = [math]::Round(100 - $PosesionArgentina, 2)

    $PasesArgentina = 1 + ($i % 4)
    $PasesMexico = 1 + (($i + 2) % 4)

    $TirosArgentina = [math]::Floor($i / 45)
    $TirosMexico = [math]::Floor($i / 60)

    $Lineas.Add("estadisticas_equipo,partido_id=PAR-0001,equipo_id=ARG posesion_pct=$PosesionArgentina,pases_intervalo=${PasesArgentina}i,tiros_acumulados=${TirosArgentina}i $Timestamp")
    $Lineas.Add("estadisticas_equipo,partido_id=PAR-0001,equipo_id=MEX posesion_pct=$PosesionMexico,pases_intervalo=${PasesMexico}i,tiros_acumulados=${TirosMexico}i $Timestamp")
}

$Lineas | Set-Content -Encoding utf8 $ArchivoSalida

Write-Host "=== GENERACION FINALIZADA ==="
Write-Host "Archivo: $ArchivoSalida"
Write-Host "Puntos generados: $($Lineas.Count)"
Write-Host "Frecuencia: 1 punto cada 10 segundos por equipo"
Write-Host "Precision temporal: segundos"

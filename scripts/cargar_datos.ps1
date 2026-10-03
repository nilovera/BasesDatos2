$TokenPath = Join-Path $PSScriptRoot "..\.influxdb3-token"
$ArchivoDatos = Join-Path $PSScriptRoot "..\datos\estadisticas_equipo.lp"
$CarpetaLotes = Join-Path $PSScriptRoot "..\datos\lotes"
$TamanoLote = 250

if (-not (Test-Path $TokenPath)) {
    throw "No se encontro .influxdb3-token."
}

if (-not (Test-Path $ArchivoDatos)) {
    throw "No se encontro el archivo generado."
}

$env:INFLUXDB3_AUTH_TOKEN = Get-Content -Raw $TokenPath
$Lineas = @(Get-Content $ArchivoDatos)

New-Item -ItemType Directory -Force $CarpetaLotes | Out-Null

$Utf8SinBom = New-Object System.Text.UTF8Encoding($false)
$Cronometro = [System.Diagnostics.Stopwatch]::StartNew()
$LotesProcesados = 0

for ($Inicio = 0; $Inicio -lt $Lineas.Count; $Inicio += $TamanoLote) {
    $Fin = [Math]::Min($Inicio + $TamanoLote - 1, $Lineas.Count - 1)
    $Lote = $Lineas[$Inicio..$Fin]
    $LotesProcesados++

    $NombreLote = "lote-$LotesProcesados.lp"
    $RutaLoteWindows = Join-Path $CarpetaLotes $NombreLote
    $RutaLoteContenedor = "/datos/lotes/$NombreLote"

    $ContenidoLote = ($Lote -join "`n") + "`n"
    [System.IO.File]::WriteAllText(
        $RutaLoteWindows,
        $ContenidoLote,
        $Utf8SinBom
    )

    docker exec --env INFLUXDB3_AUTH_TOKEN `
        fixture2030-influxdb `
        influxdb3 write `
        --database fixture2030_detalle `
        --precision s `
        --file $RutaLoteContenedor

    if ($LASTEXITCODE -ne 0) {
        throw "Fallo la carga del lote $LotesProcesados."
    }

    Write-Host "Lote $LotesProcesados cargado: $($Lote.Count) puntos"
}

$Cronometro.Stop()

Write-Host "=== CARGA FINALIZADA ==="
Write-Host "Puntos enviados: $($Lineas.Count)"
Write-Host "Lotes procesados: $LotesProcesados"
Write-Host "Tamano maximo de lote: $TamanoLote"
Write-Host "Tiempo total ms: $($Cronometro.ElapsedMilliseconds)"

docker exec --env INFLUXDB3_AUTH_TOKEN `
    fixture2030-influxdb `
    influxdb3 query `
    --database fixture2030_detalle `
    "SELECT COUNT(*) AS puntos_cargados FROM estadisticas_equipo"

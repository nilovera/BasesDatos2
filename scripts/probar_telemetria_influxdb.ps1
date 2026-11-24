$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$from = "2030-06-13T20:10:00Z"
$to = "2030-06-13T20:10:20Z"

Write-Host "1/8 Cargando posiciones con timestamps compartidos..."
$positionSamples = @(
    [ordered]@{ equipoId="EQ-01"; jugadorId="JUG-0001"; x=12.5; y=48.0; periodo=1; segundoPartido=600; capturadoEn="2030-06-13T20:10:00Z" },
    [ordered]@{ equipoId="EQ-33"; jugadorId="JUG-0513"; x=87.5; y=52.0; periodo=1; segundoPartido=600; capturadoEn="2030-06-13T20:10:00Z" },
    [ordered]@{ equipoId="EQ-01"; jugadorId="JUG-0001"; x=14.0; y=50.0; periodo=1; segundoPartido=610; capturadoEn="2030-06-13T20:10:10Z" },
    [ordered]@{ equipoId="EQ-33"; jugadorId="JUG-0513"; x=86.0; y=50.0; periodo=1; segundoPartido=610; capturadoEn="2030-06-13T20:10:10Z" }
)
$positionsBody = @{ muestras=$positionSamples } | ConvertTo-Json -Depth 6 -Compress
$write = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/partidos/PAR-0001/telemetria/posiciones" -ContentType "application/json" -Body $positionsBody -TimeoutSec 10
if ($write.muestrasAceptadas -ne 4) { throw "InfluxDB no acepto las cuatro posiciones." }

Write-Host "2/8 Repitiendo el lote para comprobar la clave natural serie+timestamp..."
$replay = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/partidos/PAR-0001/telemetria/posiciones" -ContentType "application/json" -Body $positionsBody -TimeoutSec 10
if (-not $replay.repetible) { throw "La API no declara la escritura repetible." }

Write-Host "3/8 Recorriendo dos paginas con cursor estable (timestamp, jugadorId)..."
$positionsUrl = "$baseUrl/api/v1/partidos/PAR-0001/telemetria/posiciones"
$page1 = Invoke-RestMethod -Uri "$($positionsUrl)?desde=$from&hasta=$to&limite=2" -TimeoutSec 10
if (@($page1.items).Count -ne 2 -or [string]::IsNullOrWhiteSpace($page1.siguienteCursor)) {
    throw "La primera pagina no contiene dos puntos y cursor."
}
$encodedCursor = [System.Uri]::EscapeDataString($page1.siguienteCursor)
$page2 = Invoke-RestMethod -Uri "$($positionsUrl)?desde=$from&hasta=$to&limite=2&cursor=$encodedCursor" -TimeoutSec 10
$allIds = @($page1.items + $page2.items | ForEach-Object { "$($_.capturadoEn)|$($_.jugadorId)" })
if ($allIds.Count -ne 4 -or @($allIds | Select-Object -Unique).Count -ne 4) {
    throw "El cursor omitio o repitio posiciones con timestamps compartidos."
}

Write-Host "4/8 Reconstruyendo el mapa de calor de JUG-0001..."
$heatmap = Invoke-RestMethod -Uri "$baseUrl/api/v1/partidos/PAR-0001/jugadores/JUG-0001/mapa-calor?desde=$from&hasta=$to&resolucion=10" -TimeoutSec 10
if ($heatmap.totalMuestras -ne 2 -or @($heatmap.celdas).Count -lt 1) {
    throw "El mapa de calor no se reconstruyo desde los dos puntos."
}

Write-Host "5/8 Generando 1.080 estadisticas reproducibles (90 minutos, dos equipos)..."
$start = [DateTimeOffset]::Parse("2030-06-13T20:00:00Z")
$samples = [System.Collections.Generic.List[object]]::new()
for ($i = 0; $i -lt 540; $i++) {
    $capturedAt = $start.AddSeconds($i * 10).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $homePossession = 50 + [math]::Round(8 * [math]::Sin($i / 35), 2)
    $awayPossession = [math]::Round(100 - $homePossession, 2)
    $period = if (($i * 10) -lt 2700) { 1 } else { 2 }
    $samples.Add([ordered]@{ equipoId="EQ-01"; posesionPct=$homePossession; pasesIntervalo=(1 + ($i % 4)); tirosAcumulados=[math]::Floor($i / 45); golesAcumulados=[math]::Floor($i / 180); periodo=$period; segundoPartido=($i * 10); capturadoEn=$capturedAt })
    $samples.Add([ordered]@{ equipoId="EQ-33"; posesionPct=$awayPossession; pasesIntervalo=(1 + (($i + 2) % 4)); tirosAcumulados=[math]::Floor($i / 60); golesAcumulados=[math]::Floor($i / 270); periodo=$period; segundoPartido=($i * 10); capturadoEn=$capturedAt })
}

Write-Host "6/8 Enviando estadisticas por la API en lotes de hasta 250..."
$accepted = 0
for ($offset = 0; $offset -lt $samples.Count; $offset += 250) {
    $end = [math]::Min($offset + 249, $samples.Count - 1)
    $batch = @($samples[$offset..$end])
    $body = @{ muestras=$batch } | ConvertTo-Json -Depth 6 -Compress
    $result = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/partidos/PAR-0001/telemetria/estadisticas-equipos" -ContentType "application/json" -Body $body -TimeoutSec 20
    $accepted += [int]$result.muestrasAceptadas
}
if ($accepted -ne 1080) { throw "Se esperaban 1.080 muestras aceptadas y se obtuvieron $accepted." }

Write-Host "7/8 Generando resumen historico de 15 minutos..."
$aggregation = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/partidos/PAR-0001/telemetria/agregaciones/15m" -TimeoutSec 30
if ($aggregation.resumenesGenerados -ne 12) {
    throw "Se esperaban 12 resumenes y se obtuvieron $($aggregation.resumenesGenerados)."
}

Write-Host "8/8 Consultando los resumenes historicos..."
$summaries = Invoke-RestMethod -Uri "$baseUrl/api/v1/partidos/PAR-0001/telemetria/resumenes-equipos/15m" -TimeoutSec 10
if (@($summaries.items).Count -ne 12) { throw "La base historica no contiene 12 resumenes." }
$teams = @($summaries.items | ForEach-Object { $_.equipoId } | Select-Object -Unique | Sort-Object)
if (($teams -join ",") -ne "EQ-01,EQ-33") { throw "Los resumenes no usan los IDs internos EQ-01/EQ-33." }

Write-Host "OK: posiciones, replay, cursor, mapa de calor, 1.080 puntos y 12 resumenes verificados."

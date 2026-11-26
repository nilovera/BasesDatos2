$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000"
Write-Host "Verificando pantalla y lecturas de la transmision..."
$page = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/directo" -TimeoutSec 15
if ($page.StatusCode -ne 200 -or $page.Content -notmatch 'id="pitch"') { throw "No se pudo abrir la cancha." }
foreach ($asset in @("style.css", "app.js")) {
    $response = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/directo/assets/$asset" -TimeoutSec 15
    if ($response.StatusCode -ne 200) { throw "No se pudo leer $asset." }
}
$snapshot = Invoke-RestMethod -Uri "$baseUrl/api/v1/directo" -TimeoutSec 15
$id = $snapshot.simulacion.simulacionId
if (@($snapshot.equipos).Count -ne 2 -or @($snapshot.jugadores).Count -lt 22) { throw "Faltan equipos o jugadores." }
if ($null -ne $snapshot.plan) { throw "La lectura publica no debe anticipar el plan." }
$pitch = Invoke-RestMethod -Uri "$baseUrl/api/v1/directo/cancha?simulacionId=$id" -TimeoutSec 20
$team = $snapshot.equipos[0].equipoId
$teamMap = Invoke-RestMethod -Uri "$baseUrl/api/v1/directo/cancha?simulacionId=$id&equipoId=$team" -TimeoutSec 20
$player = $snapshot.jugadores[0].jugadorId
$playerMap = Invoke-RestMethod -Uri "$baseUrl/api/v1/directo/cancha?simulacionId=$id&jugadorId=$player" -TimeoutSec 20
$comments = Invoke-RestMethod -Uri "$baseUrl/api/v1/directo/comentarios?simulacionId=$id" -TimeoutSec 20
if ($snapshot.simulacion.estado -eq "FINALIZADA" -and (@($pitch.posiciones).Count -ne 22 -or $null -eq $pitch.pelota -or @($teamMap.celdas).Count -eq 0 -or @($comments.items).Count -eq 0)) {
    throw "El partido finalizado no devolvio toda la informacion de la transmision."
}
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$evidenceDir = Join-Path "evidencia\ejecuciones" "frontend-$stamp"
$commit = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw "No se pudo identificar el commit." }
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
[ordered]@{
    scenario = "frontend-transmision"; result = "OK"; sourceCommit = $commit
    capturedAtUtc = [DateTime]::UtcNow.ToString("o"); simulationId = $id
    matchId = $snapshot.simulacion.partidoId; matchState = $snapshot.simulacion.estado
    positions = @($pitch.posiciones).Count; teamHeatmapCells = @($teamMap.celdas).Count
    playerHeatmapCells = @($playerMap.celdas).Count; comments = @($comments.items).Count
    note = "Verifica HTTP y datos; la comprobacion visual se realiza en el navegador."
} | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -Path (Join-Path $evidenceDir "resultado.json")
Write-Host "OK: pantalla, recursos, partido, cancha, filtros y comentarios. Evidencia: $evidenceDir"

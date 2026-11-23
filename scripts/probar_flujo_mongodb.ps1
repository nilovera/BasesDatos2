$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000/api/v1/partidos/PAR-0001/eventos"

function Send-Event([string]$key, [string]$body) {
    return Invoke-WebRequest -UseBasicParsing -Method Post -Uri $baseUrl `
        -Headers @{ "Idempotency-Key" = $key } `
        -ContentType "application/json" -Body $body -TimeoutSec 10
}

Write-Host "1/6 Inicio de partido..."
$startBody = '{"tipo":"INICIO_PARTIDO","ocurridoEn":"2030-06-13T20:00:00Z"}'
$start = Send-Event "fixture2030-demo-inicio-0001" $startBody
if ($start.StatusCode -notin @(200, 201)) { throw "Inicio inesperado: $($start.StatusCode)" }

Write-Host "2/6 Repeticion idempotente..."
$replay = Send-Event "fixture2030-demo-inicio-0001" $startBody
if ($replay.StatusCode -ne 200 -or $replay.Headers["Idempotency-Replayed"] -ne "true") {
    throw "La repeticion idempotente no devolvio 200/replayed=true."
}

Write-Host "3/6 Conflicto por reutilizar la clave con otro body..."
$conflictBody = '{"tipo":"INICIO_PARTIDO","ocurridoEn":"2030-06-13T20:01:00Z"}'
$conflictDetected = $false
try {
    Send-Event "fixture2030-demo-inicio-0001" $conflictBody | Out-Null
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 409) {
        $conflictDetected = $true
    } else {
        throw
    }
}
if (-not $conflictDetected) { throw "No se detecto el conflicto idempotente." }

Write-Host "4/6 Gol..."
$goalBody = '{"tipo":"GOL","ocurridoEn":"2030-06-13T20:23:00Z","periodo":1,"minuto":23,"equipoId":"EQ-01","jugadorId":"JUG-0013"}'
$goal = Send-Event "fixture2030-demo-gol-000001" $goalBody
$goalResult = $goal.Content | ConvertFrom-Json

Write-Host "5/6 Correccion auditable..."
$correctionBody = @{
    tipo = "CORRECCION_EVENTO"
    ocurridoEn = "2030-06-13T20:25:00Z"
    eventoOriginalId = $goalResult.eventoId
    motivo = "Jugador informado incorrectamente"
    reemplazo = @{
        tipo = "GOL"
        periodo = 1
        minuto = 23
        equipoId = "EQ-01"
        jugadorId = "JUG-0014"
    }
} | ConvertTo-Json -Depth 5 -Compress
Send-Event "fixture2030-demo-correccion-01" $correctionBody | Out-Null

Write-Host "6/6 Sustitucion y consulta..."
$substitutionBody = '{"tipo":"SUSTITUCION","ocurridoEn":"2030-06-13T21:05:00Z","periodo":2,"minuto":60,"equipoId":"EQ-01","saleJugadorId":"JUG-0009","entraJugadorId":"JUG-0010"}'
Send-Event "fixture2030-demo-sustitucion-1" $substitutionBody | Out-Null

$match = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/partidos/PAR-0001" -TimeoutSec 5
$events = Invoke-RestMethod -Uri "${baseUrl}?desdeSecuencia=0&limite=100" -TimeoutSec 5
if ($match.estado -ne "EN_CURSO" -or $match.marcador.local -ne 1) {
    throw "El agregado final no coincide con el flujo esperado."
}
if ($events.items.Count -lt 4) {
    throw "Se esperaban al menos cuatro eventos oficiales."
}

Write-Host "OK: idempotencia, conflicto, gol, correccion, sustitucion y consulta."
Write-Host "Partido" $match.partidoId "estado" $match.estado "marcador" $match.marcador.local "-" $match.marcador.visitante "version" $match.version
Write-Host "Eventos oficiales:" $events.items.Count

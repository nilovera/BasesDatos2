$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000/api/v1/partidos/PAR-0001/eventos"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" "outbox-$runId"
$workerStopped = $false
$capturedError = $null
$result = [ordered]@{
    scenario = "outbox-at-least-once"
    result = "ERROR"
    sourceCommit = (& git rev-parse HEAD).Trim()
    capturedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
}

function Get-AlertState {
    $alerts = Invoke-RestMethod -Uri "http://127.0.0.1:9090/api/v1/alerts" -TimeoutSec 5
    $match = @($alerts.data.alerts | Where-Object { $_.labels.alertname -eq "Fixture2030OutboxWorkerDown" })
    if ($match.Count -eq 0) { return "inactive" }
    return $match[0].state
}

function Get-OutboxState([string]$eventId) {
    $javascript = "const x=db.outbox.findOne({eventoId:'$eventId'},{estado:1,intentos:1,_id:0}); print(JSON.stringify(x));"
    $raw = (& docker compose exec -T mongo mongosh --quiet `
        'mongodb://mongo:27017/fixture2030?replicaSet=rs0' --eval $javascript) -join "`n"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar el mensaje $eventId." }
    return ($raw | ConvertFrom-Json)
}

function Wait-Published([string]$eventId) {
    for ($attempt = 1; $attempt -le 45; $attempt++) {
        $state = Get-OutboxState $eventId
        if ($state.estado -eq "PUBLICADO") { return $state }
        if ($state.estado -eq "FALLIDO") { throw "El mensaje $eventId termino FALLIDO." }
        Start-Sleep -Seconds 1
    }
    throw "La Outbox no convergio a PUBLICADO para $eventId."
}

function Count-StreamEvent([string]$eventId) {
    $rows = @(docker compose exec -T redis redis-cli --raw XRANGE eventos:partido:PAR-0001 - +)
    if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar el stream proyectado." }
    return @($rows | Where-Object { $_ -eq $eventId }).Count
}

try {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    Write-Host "1/7 Deteniendo solamente el worker de Outbox..."
    docker compose stop outbox-worker | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener el worker." }
    $workerStopped = $true

    Write-Host "2/7 Esperando la alerta del worker..."
    $alertState = "inactive"
    for ($attempt = 1; $attempt -le 60; $attempt++) {
        $alertState = Get-AlertState
        if ($alertState -eq "firing") { break }
        Start-Sleep -Seconds 1
    }
    if ($alertState -ne "firing") { throw "La alerta Fixture2030OutboxWorkerDown no llego a firing." }

    Write-Host "3/7 Confirmando un evento oficial mientras el worker esta detenido..."
    $body = @{
        tipo = "SUSTITUCION"
        ocurridoEn = (Get-Date).ToUniversalTime().ToString("o")
        periodo = 2
        minuto = 75
        equipoId = "EQ-01"
        saleJugadorId = "JUG-0002"
        entraJugadorId = "JUG-0003"
    } | ConvertTo-Json
    $headers = @{ "Idempotency-Key" = "outbox-$runId" }
    $event = Invoke-RestMethod -Method Post -Uri $baseUrl -Headers $headers `
        -ContentType "application/json" -Body $body -TimeoutSec 10
    if ($event.propagacion -ne "PENDIENTE") { throw "La API no devolvio propagacion PENDIENTE." }
    $during = Get-OutboxState $event.eventoId
    if ($during.estado -ne "PENDIENTE") { throw "El mensaje no quedo PENDIENTE con el worker detenido." }

    Write-Host "4/7 Recuperando el worker y esperando convergencia..."
    docker compose start outbox-worker | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo recuperar el worker." }
    $workerStopped = $false
    $first = Wait-Published $event.eventoId
    $firstCount = Count-StreamEvent $event.eventoId
    if ($firstCount -ne 1) { throw "La primera proyeccion no aparece exactamente una vez." }

    Write-Host "5/7 Simulando perdida del acuse despues de publicar..."
    docker compose stop outbox-worker | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener el worker para el replay." }
    $workerStopped = $true
    $javascript = "db.outbox.updateOne({eventoId:'$($event.eventoId)'},{`$set:{estado:'PENDIENTE',proximoIntentoEn:new Date(),publicadoEn:null,expiraEn:null,actualizadoEn:new Date()},`$unset:{bloqueo:''}})"
    docker compose exec -T mongo mongosh --quiet `
        'mongodb://mongo:27017/fixture2030?replicaSet=rs0' --eval $javascript | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo preparar el replay controlado." }

    Write-Host "6/7 Reprocesando y comprobando idempotencia..."
    docker compose start outbox-worker | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo iniciar el worker para el replay." }
    $workerStopped = $false
    $second = Wait-Published $event.eventoId
    $secondCount = Count-StreamEvent $event.eventoId
    if ($secondCount -ne 1) { throw "El replay duplico el evento en Redis." }

    Write-Host "7/7 Guardando evidencia..."
    $result.result = "OK"
    $result.eventId = $event.eventoId
    $result.alertDuring = $alertState
    $result.stateWhileStopped = $during.estado
    $result.stateAfterRecovery = $first.estado
    $result.attemptsAfterReplay = [int]$second.intentos
    $result.redisCopiesAfterReplay = $secondCount
    $result.converged = $true
} catch {
    $result.error = $_.Exception.Message
    $capturedError = $_
} finally {
    if ($workerStopped) {
        docker compose start outbox-worker | Out-Null
    }
    $result | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 `
        -Path (Join-Path $outputDir "resultado.json")
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: atraso, alerta, recuperacion y replay idempotente verificados. Evidencia: $outputDir"

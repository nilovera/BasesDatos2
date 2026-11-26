$ErrorActionPreference = "Stop"

Write-Host "Verificando worker, cola, proyeccion Redis y metricas..."

$services = @(docker compose ps --status running --services)
if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar Docker Compose." }
if ($services -notcontains "outbox-worker") { throw "El worker de Outbox no esta operativo." }

$pending = $null
for ($attempt = 1; $attempt -le 30; $attempt++) {
    $pending = (& docker compose exec -T mongo mongosh --quiet `
        'mongodb://mongo:27017/fixture2030?replicaSet=rs0' `
        --eval "db.outbox.countDocuments({estado: {`$in: ['PENDIENTE', 'PROCESANDO']}})").Trim()
    if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar la Outbox." }
    if ([int]$pending -eq 0) { break }
    Start-Sleep -Seconds 1
}
if ([int]$pending -ne 0) { throw "La Outbox no convergio a cero; pendientes=$pending." }

$failed = (& docker compose exec -T mongo mongosh --quiet `
    'mongodb://mongo:27017/fixture2030?replicaSet=rs0' `
    --eval "db.outbox.countDocuments({estado: 'FALLIDO'})").Trim()
if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar la cola fallida." }
if ([int]$failed -ne 0) { throw "Hay $failed mensajes FALLIDOS en la Outbox." }

$processed = (& docker compose exec -T redis redis-cli --raw HLEN outbox:procesados).Trim()
if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar la deduplicacion en Redis." }

$encoded = [System.Uri]::EscapeDataString('up{job="fixture2030-outbox"}')
$targetUp = $false
for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $target = Invoke-RestMethod `
            -Uri "http://127.0.0.1:9090/api/v1/query?query=$encoded" -TimeoutSec 5
        if ($target.data.result.Count -eq 1 -and $target.data.result[0].value[1] -eq "1") {
            $targetUp = $true
            break
        }
    } catch {
        # Prometheus puede estar entre scrapes durante el arranque del worker.
    }
    Start-Sleep -Seconds 1
}
if (-not $targetUp) {
    throw "Prometheus no informa el worker de Outbox UP."
}

$metricQuery = [System.Uri]::EscapeDataString('fixture2030_outbox_pending{consumer="redis"}')
$metrics = (Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:9090/api/v1/query?query=$metricQuery" -TimeoutSec 5).Content
if ($metrics -notmatch '"status":"success"') { throw "Faltan metricas de Outbox." }

Write-Host "OK: worker UP, pendientes=$pending, fallidos=0 y eventos deduplicados=$processed."

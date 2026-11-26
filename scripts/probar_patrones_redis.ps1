$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000"

Write-Host "1/7 Limpiando solamente la clave de cache de PAR-0001..."
& docker compose exec -T redis redis-cli DEL cache:partido:PAR-0001 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "No se pudo limpiar la clave de demostracion." }

Write-Host "2/7 Cache miss y carga desde MongoDB..."
$first = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
if ($first.Headers["X-Cache"] -ne "MISS") {
    throw "Se esperaba X-Cache=MISS y se obtuvo $($first.Headers['X-Cache'])."
}

Write-Host "3/7 Cache hit desde Redis..."
$second = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
if ($second.Headers["X-Cache"] -ne "HIT") {
    throw "Se esperaba X-Cache=HIT y se obtuvo $($second.Headers['X-Cache'])."
}

Write-Host "4/7 Creando sesion Hash con TTL..."
$sessionBody = @{ usuarioId = "USR-0001"; rol = "FAN"; ttlSegundos = 120 } | ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/sesiones" `
    -ContentType "application/json" -Body $sessionBody -TimeoutSec 5
if ($session.ttlSegundos -le 0 -or $session.renovaciones -ne 0) {
    throw "La sesion inicial no posee el TTL esperado."
}

Write-Host "5/7 Lectura sin renovacion automatica..."
$read = Invoke-RestMethod -Uri "$baseUrl/api/v1/sesiones/$($session.sesionId)" -TimeoutSec 5
if ($read.renovaciones -ne 0) { throw "GET no debe renovar la sesion." }

Write-Host "6/7 Renovacion explicita y atomica a 600 segundos..."
$renewBody = @{ ttlSegundos = 600 } | ConvertTo-Json
$renewed = Invoke-RestMethod -Method Post `
    -Uri "$baseUrl/api/v1/sesiones/$($session.sesionId)/renovacion" `
    -ContentType "application/json" -Body $renewBody -TimeoutSec 5
if ($renewed.renovaciones -ne 1 -or $renewed.ttlSegundos -lt 590) {
    throw "La renovacion explicita no actualizo contador y TTL."
}

Write-Host "7/7 Escritura oficial e invalidacion de cache..."
$eventBody = @{
    tipo = "SUSTITUCION"
    ocurridoEn = "2030-06-13T20:20:00Z"
    periodo = 1
    minuto = 20
    equipoId = "EQ-01"
    saleJugadorId = "JUG-0009"
    entraJugadorId = "JUG-0010"
} | ConvertTo-Json
$idempotencyKey = "redis-demo-" + [guid]::NewGuid().ToString()
Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/partidos/PAR-0001/eventos" `
    -Headers @{ "Idempotency-Key" = $idempotencyKey } `
    -ContentType "application/json" -Body $eventBody -TimeoutSec 10 | Out-Null

$invalidated = $false
for ($attempt = 1; $attempt -le 15; $attempt++) {
    $exists = (& docker compose exec -T redis redis-cli EXISTS cache:partido:PAR-0001).Trim()
    if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar la clave de cache." }
    if ($exists -eq "0") { $invalidated = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $invalidated) { throw "El worker de Outbox no invalido el cache." }

$afterWrite = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
if ($afterWrite.Headers["X-Cache"] -ne "MISS") {
    throw "La escritura no invalido el cache; se obtuvo $($afterWrite.Headers['X-Cache'])."
}

Write-Host "OK: MISS, HIT, sesion, renovacion explicita e invalidacion verificados."
Write-Host "Sesion de demostracion:" $session.sesionId

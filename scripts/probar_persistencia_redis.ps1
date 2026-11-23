$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"

Write-Host "1/5 Creando una sesion temporal para la prueba..."
$body = @{ usuarioId = "USR-0002"; rol = "OPERADOR"; ttlSegundos = 900 } | ConvertTo-Json
$session = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/sesiones" `
    -ContentType "application/json" -Body $body -TimeoutSec 5

Write-Host "2/5 Forzando snapshot RDB..."
& docker compose exec -T redis redis-cli BGSAVE | Out-Null
if ($LASTEXITCODE -ne 0) { throw "No se pudo solicitar BGSAVE." }
for ($attempt = 1; $attempt -le 20; $attempt++) {
    $info = (& docker compose exec -T redis redis-cli --raw INFO persistence) -join "`n"
    if ($info -match "rdb_bgsave_in_progress:0" -and $info -match "rdb_last_bgsave_status:ok") { break }
    Start-Sleep -Seconds 1
}
if ($info -notmatch "rdb_last_bgsave_status:ok") { throw "BGSAVE no termino correctamente." }

Write-Host "3/5 Verificando archivos RDB y AOF en el volumen..."
& docker compose exec -T redis sh -c "test -s /data/dump.rdb && test -d /data/appendonlydir"
if ($LASTEXITCODE -ne 0) { throw "No se encontraron RDB y AOF en /data." }

Write-Host "4/5 Reiniciando solamente Redis..."
& docker compose restart redis | Out-Null
if ($LASTEXITCODE -ne 0) { throw "No se pudo reiniciar Redis." }
for ($attempt = 1; $attempt -le 30; $attempt++) {
    $pong = (& docker compose exec -T redis redis-cli --raw PING 2>$null)
    if ($LASTEXITCODE -eq 0 -and $pong -eq "PONG") { break }
    Start-Sleep -Seconds 2
}
if ($pong -ne "PONG") { throw "Redis no se recupero despues del reinicio." }

Write-Host "5/5 Comprobando recuperacion de la sesion..."
$restored = Invoke-RestMethod -Uri "$baseUrl/api/v1/sesiones/$($session.sesionId)" -TimeoutSec 5
if ($restored.sesionId -ne $session.sesionId -or $restored.ttlSegundos -le 0) {
    throw "La sesion no fue recuperada desde la persistencia."
}

Write-Host "OK: snapshot RDB, AOF y recuperacion despues del reinicio verificados."

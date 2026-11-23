$ErrorActionPreference = "Stop"

Write-Host "Verificando Redis, persistencia, memoria y exporter..."

$pongOutput = @(& docker compose exec -T redis redis-cli --raw PING)
$pongExitCode = $LASTEXITCODE
$pong = if ($pongOutput.Count -gt 0) { ($pongOutput -join "").Trim() } else { "" }
if ($pongExitCode -ne 0 -or $pong -ne "PONG") {
    throw "Redis no respondio PONG."
}

$policy = (& docker compose exec -T redis redis-cli --raw CONFIG GET maxmemory-policy)
if ($LASTEXITCODE -ne 0 -or ($policy -join "`n") -notmatch "allkeys-lfu") {
    throw "Redis no usa la politica allkeys-lfu."
}

$maxmemory = (& docker compose exec -T redis redis-cli --raw CONFIG GET maxmemory)
if ($LASTEXITCODE -ne 0 -or ($maxmemory -join "`n") -notmatch "268435456") {
    throw "Redis no tiene maxmemory=256mb."
}

$persistence = (& docker compose exec -T redis redis-cli --raw INFO persistence)
if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar INFO persistence." }
$persistenceText = $persistence -join "`n"
if ($persistenceText -notmatch "aof_enabled:1") { throw "AOF no esta activo." }
if ($persistenceText -notmatch "rdb_last_bgsave_status:ok") {
    throw "El estado RDB no es OK."
}

$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
if ($health.redis -ne "UP") { throw "La API no informa Redis UP." }

$query = "http://localhost:9090/api/v1/query?query=redis_up%7Bjob%3D%22fixture2030-redis%22%7D"
$prometheus = Invoke-RestMethod -Uri $query -TimeoutSec 5
if ($prometheus.status -ne "success" -or $prometheus.data.result.Count -eq 0) {
    throw "Prometheus no posee la metrica redis_up."
}
if ([double]$prometheus.data.result[0].value[1] -ne 1) {
    throw "El exporter informa redis_up=0."
}

Write-Host "OK: Redis PONG, API UP y exporter redis_up=1."
Write-Host "OK: maxmemory 256mb, eviction allkeys-lfu, AOF activo y RDB OK."

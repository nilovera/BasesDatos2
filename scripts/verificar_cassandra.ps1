$ErrorActionPreference = "Stop"

Write-Host "Verificando Cassandra, esquema, API y metricas..."

$status = (& docker compose exec -T cassandra nodetool status) -join "`n"
if ($LASTEXITCODE -ne 0 -or $status -notmatch "(?m)^UN\s+") {
    throw "Cassandra no informa un nodo Up/Normal (UN)."
}

$tables = (& docker compose exec -T cassandra cqlsh -e "SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'fixture2030_comments';") -join "`n"
if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar system_schema.tables." }
foreach ($table in @("comments_by_match_bucket_shard", "comments_by_user_day", "comment_locator_by_id", "comment_write_requests")) {
    if ($tables -notmatch $table) { throw "Falta la tabla $table." }
}

$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
if ($health.cassandra -ne "UP") { throw "La API no informa Cassandra UP." }

$query = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22cassandra%22%7D"
$prometheus = Invoke-RestMethod -Uri $query -TimeoutSec 5
if ($prometheus.status -ne "success" -or $prometheus.data.result.Count -eq 0) {
    throw "Prometheus no posee la metrica de Cassandra."
}
if ([double]$prometheus.data.result[0].value[1] -ne 1) {
    throw "Prometheus informa Cassandra DOWN."
}

Write-Host "OK: Cassandra UN, cuatro tablas, API UP y metrica=1."
Write-Host "NOTA: RF=1 es laboratorio local; no demuestra quorum ni tolerancia real."


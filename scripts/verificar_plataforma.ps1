$ErrorActionPreference = "Stop"

Write-Host "Esperando la API..."
$health = $null
for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
        if (
            $health.status -eq "UP" -and
            $health.mongodb -eq "PRIMARY" -and
            $health.redis -eq "UP" -and
            $health.cassandra -eq "UP" -and
            $health.influxdb -eq "UP" -and
            $health.neo4j -eq "UP"
        ) { break }
    } catch {
        # La API puede estar iniciando o una dependencia puede estar temporalmente caída.
    }
    Start-Sleep -Seconds 2
}
if (
    $null -eq $health -or
    $health.status -ne "UP" -or
    $health.mongodb -ne "PRIMARY" -or
    $health.redis -ne "UP" -or
    $health.cassandra -ne "UP" -or
    $health.influxdb -ne "UP" -or
    $health.neo4j -ne "UP"
) {
    $mongoState = if ($null -ne $health) { $health.mongodb } else { "SIN_RESPUESTA" }
    $redisState = if ($null -ne $health) { $health.redis } else { "SIN_RESPUESTA" }
    $cassandraState = if ($null -ne $health) { $health.cassandra } else { "SIN_RESPUESTA" }
    $influxState = if ($null -ne $health) { $health.influxdb } else { "SIN_RESPUESTA" }
    $neo4jState = if ($null -ne $health) { $health.neo4j } else { "SIN_RESPUESTA" }
    throw "La API no quedo UP. MongoDB=$mongoState Redis=$redisState Cassandra=$cassandraState InfluxDB=$influxState Neo4j=$neo4jState."
}

$match = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/partidos/PAR-0001" -TimeoutSec 3
$metrics = (Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/metrics" -TimeoutSec 3).Content
if ($metrics -notmatch "fixture2030_http_requests_total") {
    throw "La API no expone las metricas esperadas."
}

$prometheus = $null
$grafana = $null
for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $prometheus = Invoke-RestMethod -Uri "http://localhost:9090/-/ready" -TimeoutSec 3
        $grafana = Invoke-RestMethod -Uri "http://localhost:3000/api/health" -TimeoutSec 3
        if ($grafana.database -eq "ok") { break }
    } catch {
        Start-Sleep -Seconds 2
    }
}
if ($null -eq $prometheus) { throw "Prometheus no esta operativo." }
if ($null -eq $grafana -or $grafana.database -ne "ok") {
    throw "Grafana no esta operativo."
}

Write-Host "OK: API" $health.status "MongoDB" $health.mongodb
Write-Host "OK: Redis" $health.redis
Write-Host "OK: Cassandra" $health.cassandra
Write-Host "OK: InfluxDB" $health.influxdb
Write-Host "OK: Neo4j" $health.neo4j
Write-Host "OK: partido" $match.partidoId "estado" $match.estado "version" $match.version
Write-Host "OK: Prometheus" $prometheus
Write-Host "OK: Grafana" $grafana.database

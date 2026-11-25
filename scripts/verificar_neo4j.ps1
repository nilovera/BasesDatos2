$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"

Write-Host "Verificando Neo4j, catalogo, recorridos, Browser y metricas..."
$health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
if ($health.neo4j -ne "UP") { throw "La API no informa Neo4j UP." }

$summary = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/resumen" -TimeoutSec 10
if ($summary.equipos -ne 64) { throw "Neo4j no contiene 64 equipos." }
if ($summary.jugadores -ne 1024) { throw "Neo4j no contiene 1.024 jugadores." }
if ($summary.partidos -ne 1) { throw "Neo4j no contiene el partido de demostracion." }
if ($summary.confederaciones -ne 6) { throw "Neo4j no contiene las seis confederaciones." }
if ($summary.relaciones -ne 1097) { throw "Neo4j no contiene las 1.097 relaciones esperadas." }

$browser = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:7474" -TimeoutSec 10
if ($browser.StatusCode -ne 200) { throw "Neo4j Browser no esta operativo." }

$metricQuery = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22neo4j%22%7D"
$metric = Invoke-RestMethod -Uri $metricQuery -TimeoutSec 10
if (@($metric.data.result).Count -ne 1 -or [double]$metric.data.result[0].value[1] -ne 1) {
    throw "Prometheus no registra Neo4j UP."
}

$metrics = (Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/metrics" -TimeoutSec 10).Content
if ($metrics -notmatch 'fixture2030_dependency_up\{dependency="neo4j"\} 1') {
    throw "La API no expone la metrica funcional de Neo4j."
}

Write-Host "OK: Neo4j UP, Browser, 64 equipos, 1.024 jugadores, 1 partido, 6 confederaciones y 1.097 relaciones."

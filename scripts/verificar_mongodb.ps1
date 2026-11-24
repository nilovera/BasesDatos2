$ErrorActionPreference = "Stop"

Write-Host "Verificando replica set, catalogo e indices..."
docker compose exec -T mongo mongosh --quiet `
  "mongodb://localhost:27017/?directConnection=true" `
  /opt/fixture2030/init/03_verify.js
if ($LASTEXITCODE -ne 0) {
    throw "La verificacion de MongoDB fallo (codigo $LASTEXITCODE)."
}

$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
if ($health.mongodb -ne "PRIMARY") { throw "La API no informa MongoDB PRIMARY." }

$query = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22mongodb%22%7D"
$prometheus = Invoke-RestMethod -Uri $query -TimeoutSec 5
if ($prometheus.status -ne "success" -or @($prometheus.data.result).Count -eq 0) {
    throw "Prometheus no posee la metrica de MongoDB."
}
if ([double]$prometheus.data.result[0].value[1] -ne 1) {
    throw "Prometheus informa MongoDB DOWN."
}

Write-Host "OK: MongoDB PRIMARY en replica set, API y Prometheus."

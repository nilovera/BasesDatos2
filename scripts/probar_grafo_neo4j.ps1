$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"

Write-Host "1/6 Verificando resumen del grafo..."
$before = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/resumen" -TimeoutSec 10
if ($before.equipos -ne 64 -or $before.jugadores -ne 1024 -or $before.relaciones -ne 1097) {
    throw "El resumen inicial del grafo no coincide con el catalogo."
}

Write-Host "2/6 Recorriendo partidos para recuperar rivales..."
$rivals = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/equipos/EQ-01/rivales" -TimeoutSec 10
$mexico = @($rivals.items | Where-Object { $_.equipoId -eq "EQ-33" -and $_.partidoId -eq "PAR-0001" })
if ($mexico.Count -ne 1) { throw "El recorrido de rivales no encontro EQ-33 exactamente una vez." }

Write-Host "3/6 Recomendando jugadores por posicion y confederacion..."
$recommendations = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/jugadores/JUG-0001/recomendaciones?limite=10" -TimeoutSec 10
if (@($recommendations.items).Count -ne 10) { throw "La consulta no devolvio diez recomendaciones." }
if (@($recommendations.items | Where-Object { $_.jugadorId -eq "JUG-0001" }).Count -ne 0) {
    throw "La recomendacion no debe incluir al jugador de origen."
}

Write-Host "4/6 Buscando un camino entre dos confederaciones..."
$path = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/equipos/EQ-01/camino/EQ-33" -TimeoutSec 10
if ($path.saltos -ne 4) { throw "El camino EQ-01 a EQ-33 debe recorrer cuatro relaciones." }
if ($path.nodos[0].id -ne "EQ-01" -or $path.nodos[-1].id -ne "EQ-33") {
    throw "El camino no conserva los extremos solicitados."
}

Write-Host "5/6 Repitiendo la carga para comprobar idempotencia..."
docker compose run --rm neo4j-init
if ($LASTEXITCODE -ne 0) { throw "La segunda carga idempotente de Neo4j fallo." }
$after = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/resumen" -TimeoutSec 10
if (($before | ConvertTo-Json -Compress) -ne ($after | ConvertTo-Json -Compress)) {
    throw "La segunda carga modifico las cantidades del grafo."
}

Write-Host "6/6 Ejecutando CRUD temporal sin alterar el catalogo..."
docker compose run --rm neo4j-init python /opt/fixture2030/neo4j-init/seed.py --demo-crud
if ($LASTEXITCODE -ne 0) { throw "La prueba CRUD temporal fallo." }

Write-Host "OK: carga idempotente, CRUD, filtros, rivales, recomendaciones y camino de cuatro saltos verificados."

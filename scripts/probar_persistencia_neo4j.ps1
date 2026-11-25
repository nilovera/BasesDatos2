$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"

Write-Host "1/4 Capturando las cantidades antes del reinicio..."
$before = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/resumen" -TimeoutSec 10

Write-Host "2/4 Reiniciando solamente Neo4j..."
docker restart fixture2030-neo4j | Out-Null
if ($LASTEXITCODE -ne 0) { throw "No se pudo reiniciar Neo4j." }

Write-Host "3/4 Esperando recuperacion..."
$recovered = $false
for ($attempt = 1; $attempt -le 40; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
        if ($health.neo4j -eq "UP") { $recovered = $true; break }
    } catch { }
    Start-Sleep -Seconds 2
}
if (-not $recovered) { throw "Neo4j no se recupero despues del reinicio." }

Write-Host "4/4 Comparando el grafo persistido..."
$after = Invoke-RestMethod -Uri "$baseUrl/api/v1/grafo/resumen" -TimeoutSec 10
if (($before | ConvertTo-Json -Compress) -ne ($after | ConvertTo-Json -Compress)) {
    throw "Las cantidades del grafo cambiaron despues del reinicio."
}

Write-Host "OK: los volumenes nombrados conservaron nodos y relaciones despues del reinicio."

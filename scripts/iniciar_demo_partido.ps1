param(
    [int]$Semilla = 2030,
    [ValidateRange(1,120)][double]$Velocidad = 25,
    [string]$PartidoBaseId = "PAR-0001"
)
$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000"
$body = @{ partidoBaseId = $PartidoBaseId; semilla = $Semilla; velocidad = $Velocidad } | ConvertTo-Json
$simulation = Invoke-RestMethod -Method POST -Uri "$baseUrl/api/v1/simulaciones" -ContentType "application/json" -Body $body -TimeoutSec 15
$id = $simulation.simulacionId
$null = Invoke-RestMethod -Method POST -Uri "$baseUrl/api/v1/simulaciones/$id/iniciar" -TimeoutSec 15
$url = "$baseUrl/directo?simulacion=$id"
Start-Process $url
Write-Host "Partido $($simulation.partidoId) iniciado. Semilla $Semilla, velocidad ${Velocidad}x."
Write-Host "Transmision: $url"
Write-Host "La simulacion sigue ejecutandose aunque cierre esta consola."

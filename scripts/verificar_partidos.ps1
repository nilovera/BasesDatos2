param([string]$BaseUrl = "http://127.0.0.1:8000")
$ErrorActionPreference = "Stop"
$teams = Invoke-RestMethod -Uri "${BaseUrl}/api/v1/directo/equipos" -TimeoutSec 15
if (@($teams.items).Count -lt 2) { throw "No hay suficientes equipos para preparar cruces." }
Write-Host "Equipos disponibles: $(@($teams.items).Count)"
foreach ($group in @("proximos", "en-curso", "finalizados")) {
    $page = Invoke-RestMethod -Uri "${BaseUrl}/api/v1/directo/partidos?grupo=$group&pagina=0" -TimeoutSec 15
    foreach ($item in @($page.items)) {
        if ($null -ne $item.plan) { throw "La cartelera no debe exponer eventos futuros." }
        if (@($item.equipos).Count -ne 2) { throw "El partido no tiene dos equipos." }
    }
    Write-Host "${group}: $(@($page.items).Count) partidos en la primera pagina; hayMas=$($page.hayMas)"
}
Write-Host "Lecturas de partidos y equipos verificadas. No se crearon ni iniciaron partidos."

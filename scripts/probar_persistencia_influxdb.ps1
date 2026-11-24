$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$from = "2030-06-13T20:20:30Z"
$to = "2030-06-13T20:20:31Z"

Write-Host "1/4 Escribiendo un punto identificable por la API..."
$body = @{
    muestras = @(
        [ordered]@{ equipoId="EQ-01"; jugadorId="JUG-0001"; x=20.3; y=30.6; periodo=1; segundoPartido=1230; capturadoEn=$from }
    )
} | ConvertTo-Json -Depth 6 -Compress
Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/partidos/PAR-0001/telemetria/posiciones" -ContentType "application/json" -Body $body -TimeoutSec 10 | Out-Null

Write-Host "2/4 Reiniciando solamente InfluxDB..."
& docker restart fixture2030-influxdb | Out-Null
if ($LASTEXITCODE -ne 0) { throw "No se pudo reiniciar InfluxDB." }

Write-Host "3/4 Esperando recuperacion..."
$recovered = $false
for ($attempt = 1; $attempt -le 40; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
        if ($health.influxdb -eq "UP") { $recovered = $true; break }
    } catch { }
    Start-Sleep -Seconds 2
}
if (-not $recovered) { throw "InfluxDB no se recupero despues del reinicio." }

Write-Host "4/4 Consultando el punto despues del reinicio..."
$url = "$baseUrl/api/v1/partidos/PAR-0001/telemetria/posiciones?jugadorId=JUG-0001&desde=$from&hasta=$to&limite=10"
$page = Invoke-RestMethod -Uri $url -TimeoutSec 10
$matches = @($page.items | Where-Object { $_.capturadoEn -like "2030-06-13T20:20:30*" -and $_.x -eq 20.3 -and $_.y -eq 30.6 })
if ($matches.Count -ne 1) { throw "El punto no sobrevivio exactamente una vez al reinicio." }

Write-Host "OK: el volumen nombrado conservo la telemetria despues del reinicio."

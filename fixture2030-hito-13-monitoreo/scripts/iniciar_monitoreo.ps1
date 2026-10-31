# HITO 13 - INICIAR MONITOREO
# Levanta Prometheus, Grafana y los exporters, y reinicia la API instrumentada (/metrics).
# Uso (desde la carpeta raiz de la API):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\iniciar_monitoreo.ps1
#   ... -Contenedores      agrega cAdvisor (CPU/memoria por contenedor, opcional)
#   ... -PoolIris 5        tamano del pool de IRIS (decision del Hito 12; 0 = sin pool)
#   ... -SinReiniciarApi   no toca la API si ya esta corriendo con /metrics
param(
    [switch]$Contenedores,
    [int]$PoolIris = 5,
    [switch]$SinReiniciarApi
)
$ErrorActionPreference = "Stop"
$hito = Split-Path $PSScriptRoot -Parent
$api  = Split-Path $hito -Parent
$py   = Join-Path $api ".venv\Scripts\python.exe"
Set-Location $api

# En Windows PowerShell 5.1 un comando nativo que escribe en stderr corta el script si
# ErrorActionPreference = Stop. Los comandos de docker se ejecutan con esta funcion.
function Nativo([scriptblock]$bloque) {
    $anterior = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $bloque 2>&1 | ForEach-Object { "$_" } } finally { $ErrorActionPreference = $anterior }
}

Write-Host "=== HITO 13 - INICIAR MONITOREO ===" -ForegroundColor Cyan

Write-Host "1) Docker Desktop..."
Nativo { docker info --format "{{.ServerVersion}}" } | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop no responde. Abrirlo y volver a ejecutar." }

Write-Host "2) Las seis bases del Fixture (no se crean ni se borran, solo se inician si estaban detenidas)..."
$bases = @("fixture2030-mongodb", "fixture2030-neo4j", "fixture2030-cassandra",
           "fixture2030-redis", "fixture2030-influxdb", "fixture2030-iris")
foreach ($c in $bases) {
    $estado = (Nativo { docker inspect -f "{{.State.Running}}" $c }) -join ""
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [FALTA] $c no existe: levantarla con su compose del hito o con entorno-local\preparar_entorno.ps1" -ForegroundColor Yellow
    } elseif ($estado -ne "true") {
        Nativo { docker start $c } | Out-Null
        Write-Host "   $c iniciada"
    } else {
        Write-Host "   $c corriendo"
    }
}

Write-Host "3) Dependencias de Python del hito en el .venv de la API..."
& $py -m pip install -q -r (Join-Path $hito "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias" }

Write-Host "4) Secretos locales para los exporters y Grafana (.env y .secretos, fuera de Git)..."
& $py (Join-Path $PSScriptRoot "preparar_secretos.py")
if ($LASTEXITCODE -ne 0) { throw "No se pudieron generar los secretos locales" }

if (-not $SinReiniciarApi) {
    Write-Host "5) Reiniciando la API instrumentada (IRIS_POOL_SIZE=$PoolIris)..."
    $env:IRIS_POOL_SIZE = "$PoolIris"
    # Igual que en el Hito 12: se llama sin tuberia para que la consola no quede esperando a uvicorn.
    & (Join-Path $api "scripts\reiniciar_api.ps1")
    Set-Location $api
} else {
    Write-Host "5) API: se mantiene la instancia actual"
}
try {
    $m = Invoke-WebRequest -Uri "http://127.0.0.1:8000/metrics" -UseBasicParsing -TimeoutSec 15
    $lineas = ($m.Content -split "`n" | Where-Object { $_ -like "fixture_*" }).Count
    Write-Host "   /metrics responde ($lineas lineas fixture_*)"
} catch {
    throw "La API no expone /metrics. Verificar que la rama tenga app\routes\metrics.py y reiniciar la API."
}

Write-Host "6) Prometheus, Grafana y exporters (docker compose)..."
$compose = @("compose", "-f", (Join-Path $hito "docker-compose.yml"), "--project-directory", $hito)
if ($Contenedores) { $compose += @("--profile", "contenedores") }
Nativo { docker @compose up -d } | ForEach-Object { Write-Host "   $_" }
if ($LASTEXITCODE -ne 0) { throw "docker compose up fallo" }

Write-Host "7) Esperando a Prometheus y Grafana..."
$listos = @{ "Prometheus" = "http://localhost:9090/-/ready"; "Grafana" = "http://localhost:3000/api/health" }
foreach ($nombre in $listos.Keys) {
    $ok = $false
    for ($i = 1; $i -le 60; $i++) {
        try { Invoke-WebRequest -Uri $listos[$nombre] -UseBasicParsing -TimeoutSec 3 | Out-Null; $ok = $true; break }
        catch { Start-Sleep -Seconds 2 }
    }
    if ($ok) { Write-Host "   $nombre listo" } else { Write-Host "   [AVISO] $nombre no respondio en 2 minutos" -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Prometheus : http://localhost:9090   (Status > Targets, Alerts)" -ForegroundColor Green
Write-Host "Grafana    : http://localhost:3000   (dashboard 'Fixture 2030 - Monitoreo de la plataforma')" -ForegroundColor Green
Write-Host "             lectura sin login; usuario admin y contrasena en fixture2030-hito-13-monitoreo\.env"
Write-Host "API        : http://127.0.0.1:8000/metrics"
Write-Host ""
Write-Host "Siguiente paso (esperar ~30 s al primer scraping):"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\verificar_targets.ps1"

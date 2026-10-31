# HITO 13 - INICIAR MONITOREO
# Levanta Prometheus, Grafana y los exporters, y reinicia la API instrumentada (/metrics).
# Uso (desde la carpeta raiz de la API):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\iniciar_monitoreo.ps1
#   ... -Contenedores      agrega cAdvisor (CPU/memoria por contenedor, opcional)
#   ... -PoolIris 5        tamano del pool de IRIS (decision del Hito 12; 0 = sin pool)
#   ... -SinReiniciarApi   no toca la API si ya esta corriendo con /metrics
#   ... -DistroWsl ""      no despertar ninguna distro de WSL (por defecto "Ubuntu")
param(
    [switch]$Contenedores,
    [int]$PoolIris = 5,
    [switch]$SinReiniciarApi,
    [string]$DistroWsl = "Ubuntu"
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

# Los compose de los hitos 6 a 9 se levantaron desde el Ubuntu de WSL y guardan los datos en
# ~/docker/data/... de esa distro. Si la distro esta apagada cuando arranca un contenedor, Docker
# monta una carpeta vacia (en IRIS: "/durable/mgr: No such file or directory"). Se la despierta antes.
if ($DistroWsl) {
    Write-Host "2) Despertando la distro WSL '$DistroWsl' (carpetas de datos de los hitos 6-9)..."
    Nativo { wsl -d $DistroWsl -e true } | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "   [AVISO] No se pudo iniciar '$DistroWsl' (si las bases usan volumenes Docker, ignorar)" -ForegroundColor Yellow }
}

Write-Host "3) Las seis bases del Fixture (no se crean ni se borran; se inician o reinician si hace falta)..."
$bases = @("fixture2030-mongodb", "fixture2030-neo4j", "fixture2030-cassandra",
           "fixture2030-redis", "fixture2030-influxdb", "fixture2030-iris")
foreach ($c in $bases) {
    $estado = (Nativo { docker inspect -f "{{.State.Running}} {{if .State.Health}}{{.State.Health.Status}}{{end}}" $c }) -join ""
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   [FALTA] $c no existe: levantarla con su compose del hito o con entorno-local\preparar_entorno.ps1" -ForegroundColor Yellow
    } elseif ($estado -like "false*") {
        Nativo { docker start $c } | Out-Null
        Write-Host "   $c estaba detenida: iniciada"
    } elseif ($estado -like "*unhealthy*") {
        Nativo { docker restart $c } | Out-Null
        Write-Host "   $c estaba unhealthy: reiniciada (revisar 'docker logs $c' si se repite)" -ForegroundColor Yellow
    } else {
        Write-Host "   $c corriendo ($estado)"
    }
}

Write-Host "4) Dependencias de Python del hito en el .venv de la API..."
& $py -m pip install -q -r (Join-Path $hito "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias" }

Write-Host "5) Secretos locales para los exporters y Grafana (.env y .secretos, fuera de Git)..."
& $py (Join-Path $PSScriptRoot "preparar_secretos.py")
if ($LASTEXITCODE -ne 0) { throw "No se pudieron generar los secretos locales" }

if (-not $SinReiniciarApi) {
    Write-Host "6) Reiniciando la API instrumentada (IRIS_POOL_SIZE=$PoolIris)..."
    $env:IRIS_POOL_SIZE = "$PoolIris"
    # Igual que en el Hito 12: se llama sin tuberia para que la consola no quede esperando a uvicorn.
    & (Join-Path $api "scripts\reiniciar_api.ps1")
    Set-Location $api
} else {
    Write-Host "6) API: se mantiene la instancia actual"
}
try {
    $m = Invoke-WebRequest -Uri "http://127.0.0.1:8000/metrics" -UseBasicParsing -TimeoutSec 15
    $lineas = ($m.Content -split "`n" | Where-Object { $_ -like "fixture_*" }).Count
    Write-Host "   /metrics responde ($lineas lineas fixture_*)"
} catch {
    throw "La API no expone /metrics. Verificar que la rama tenga app\routes\metrics.py y reiniciar la API."
}

Write-Host "7) Prometheus, Grafana y exporters (docker compose)..."
$compose = @("compose", "-f", (Join-Path $hito "docker-compose.yml"), "--project-directory", $hito)
if ($Contenedores) { $compose += @("--profile", "contenedores") }
Nativo { docker @compose up -d } | ForEach-Object { Write-Host "   $_" }
if ($LASTEXITCODE -ne 0) { throw "docker compose up fallo" }

Write-Host "8) Esperando a Prometheus y Grafana..."
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

# HITO 13 - PRUEBA CONTROLADA (carga + falla + recuperacion observadas en Prometheus/Grafana)
# Por defecto: 20 usuarios, 60 s normales, Redis detenido 120 s (docker stop), 90 s de recuperacion.
# No borra datos ni volumenes: solo docker stop / docker start del contenedor de laboratorio.
# Uso (desde la carpeta raiz de la API, con iniciar_monitoreo.ps1 ya ejecutado):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\ejecutar_prueba_controlada.ps1
#   ... -Producto mongodb            otra base (mongodb, neo4j, cassandra, redis, influxdb, iris)
#   ... -Producto ninguno -Usuarios 40 -Normal 180    solo carga, sin falla
param(
    [string]$Producto = "redis",
    [int]$Usuarios = 20,
    [int]$Normal = 60,
    [int]$Falla = 120,
    [int]$Recuperacion = 90
)
$hito = Split-Path $PSScriptRoot -Parent
$api  = Split-Path $hito -Parent
$py   = Join-Path $api ".venv\Scripts\python.exe"
Set-Location $api
Write-Host "=== HITO 13 - PRUEBA CONTROLADA ($Producto) ===" -ForegroundColor Cyan
Write-Host "1) Integridad de los datos ANTES de la prueba (huellas del catalogo del Hito 12)..."
& $py (Join-Path $PSScriptRoot "verificar_datos.py") --momento antes
if ($LASTEXITCODE -ne 0) { Write-Host "[AVISO] Hay bases con datos distintos al catalogo: revisar antes de seguir" -ForegroundColor Yellow }

Write-Host ""
Write-Host "2) Prueba. Abrir Grafana (http://localhost:3000) con rango 'Last 15 minutes' para verla en vivo."
& $py (Join-Path $PSScriptRoot "ejecutar_prueba_controlada.py") --producto $Producto --usuarios $Usuarios `
    --normal $Normal --falla $Falla --recuperacion $Recuperacion
$codigo = $LASTEXITCODE

Write-Host ""
Write-Host "3) Integridad de los datos DESPUES de la prueba (la falla no debe alterar datos)..."
& $py (Join-Path $PSScriptRoot "verificar_datos.py") --momento despues
exit $codigo

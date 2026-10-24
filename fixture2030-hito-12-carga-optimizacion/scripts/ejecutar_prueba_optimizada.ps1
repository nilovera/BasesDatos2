# HITO 12 - PRUEBA OPTIMIZADA: mismo escenario, mismos datos y misma semilla que la linea base,
# pero con la API optimizada (pool de conexiones de IRIS). Luego valida y compara.
# PoolIris=5: IRIS Community acepta 8 conexiones simultaneas en total (diagnostico_iris.py);
# se dejan 3 libres para /health/ready, el diagnostico y el portal de administracion.
# Uso (desde la carpeta de la API):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-12-carga-optimizacion\scripts\ejecutar_prueba_optimizada.ps1
param([string]$Escenario = "completo", [int]$PoolIris = 5)
$ErrorActionPreference = "Stop"
$hito = Split-Path $PSScriptRoot -Parent
$api  = Split-Path $hito -Parent
$py   = Join-Path $api ".venv\Scripts\python.exe"
Set-Location $api

Write-Host "=== HITO 12 - optimizada (IRIS_POOL_SIZE=$PoolIris) ===" -ForegroundColor Cyan
$env:IRIS_POOL_SIZE = "$PoolIris"
# Se llama en la misma sesion y SIN tuberia: si se canaliza la salida (| Out-Null) PowerShell queda
# esperando a uvicorn, que hereda el handle de la tuberia, y la consola se cuelga.
& (Join-Path $api "scripts\reiniciar_api.ps1")
Set-Location $api
Start-Sleep -Seconds 3

& $py (Join-Path $PSScriptRoot "ejecutar_carga.py") --escenario $Escenario --etiqueta optimizada
if ($LASTEXITCODE -ne 0) { throw "La carga termino con error" }
& $py (Join-Path $PSScriptRoot "validar_integridad.py") optimizada
& $py (Join-Path $PSScriptRoot "comparar_resultados.py")
& $py (Join-Path $PSScriptRoot "resumir_evidencia.py")

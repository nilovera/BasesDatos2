# HITO 12 - LINEA BASE: reinicia la API con el codigo ORIGINAL (IRIS sin pool), corre la carga y valida.
# Uso (desde la carpeta de la API):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-12-carga-optimizacion\scripts\ejecutar_linea_base.ps1
#   ... -Escenario humo     (prueba de humo de 20 s)
param([string]$Escenario = "completo")
$ErrorActionPreference = "Stop"
$hito = Split-Path $PSScriptRoot -Parent
$api  = Split-Path $hito -Parent
$py   = Join-Path $api ".venv\Scripts\python.exe"
$etiqueta = if ($Escenario -eq "humo") { "humo" } else { "linea_base" }
Set-Location $api

Write-Host "=== HITO 12 - $etiqueta ===" -ForegroundColor Cyan
$env:IRIS_POOL_SIZE = "0"          # 0 = comportamiento original (una conexion por request)
Write-Host "1) Reiniciando la API (logs nuevos, mismo punto de partida)..."
# Se llama en la misma sesion y SIN tuberia: si se canaliza la salida (| Out-Null) PowerShell queda
# esperando a uvicorn, que hereda el handle de la tuberia, y la consola se cuelga.
& (Join-Path $api "scripts\reiniciar_api.ps1")
Set-Location $api
Start-Sleep -Seconds 3

Write-Host "2) Ejecutando la carga..."
& $py (Join-Path $PSScriptRoot "ejecutar_carga.py") --escenario $Escenario --etiqueta $etiqueta
if ($LASTEXITCODE -ne 0) { throw "La carga termino con error" }

Write-Host "3) Validando integridad..."
& $py (Join-Path $PSScriptRoot "validar_integridad.py") $etiqueta

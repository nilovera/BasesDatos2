# HITO 13 - VERIFICAR TARGETS
# Muestra el estado de cada target de Prometheus y la disponibilidad de las bases en tres capas.
# Guarda evidencia\prometheus_targets.json y .md. Codigo de salida 2 si falta algun job esperado.
# Uso (desde la carpeta raiz de la API):
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\verificar_targets.ps1
$hito = Split-Path $PSScriptRoot -Parent
$api  = Split-Path $hito -Parent
$py   = Join-Path $api ".venv\Scripts\python.exe"
& $py (Join-Path $PSScriptRoot "verificar_targets.py")
exit $LASTEXITCODE

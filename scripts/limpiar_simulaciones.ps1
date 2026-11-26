param([switch]$Aplicar, [string]$RestaurarLote)
$ErrorActionPreference = "Stop"
if ($Aplicar -and $RestaurarLote) { throw "Elegir limpiar o restaurar." }
Push-Location (Join-Path $PSScriptRoot "..")
try {
    if ($RestaurarLote) {
        & docker compose exec -T api python -m app.cleanup_simulations --restore $RestaurarLote
    } elseif ($Aplicar) {
        & docker compose exec -T api python -m app.cleanup_simulations --apply
    } else {
        & docker compose exec -T api python -m app.cleanup_simulations
    }
    if ($LASTEXITCODE -ne 0) { throw "La limpieza no se completo. Conservar el lote mostrado para recuperar lo ya respaldado." }
} finally {
    Pop-Location
}

param(
    [ValidateSet("humo", "normal", "estres", "todos")]
    [string]$Perfil = "humo",
    [int]$Repeticiones = 0
)

$ErrorActionPreference = "Stop"
$profiles = if ($Perfil -eq "todos") { @("humo", "normal", "estres") } else { @($Perfil) }

foreach ($profile in $profiles) {
    Write-Host "Ejecutando perfil de carga: $profile"
    $arguments = @("scripts/simulador_carga.py", "--profile", $profile)
    if ($Repeticiones -gt 0) { $arguments += @("--repetitions", $Repeticiones) }
    & python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "El perfil $profile no cumplio sus criterios o no pudo ejecutarse (codigo $LASTEXITCODE)."
    }
}

Write-Host "OK: perfiles solicitados ejecutados; revise evidencia\ejecuciones\carga-* antes de versionar."

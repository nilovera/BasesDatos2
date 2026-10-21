<#
.SYNOPSIS
    Hito 11 - Falla controlada y recuperación de una dependencia.

.DESCRIPTION
    Envoltorio de PowerShell para scripts\falla_controlada.py.

    Escenario "detenida" (por defecto): docker stop del contenedor del
    producto, pruebas durante la falla, docker start, pruebas después y
    comparación de datos/volúmenes. Nunca usa "docker compose down -v" ni
    "docker rm".

    Escenario "config": inicia una segunda instancia temporal de la API en
    otro puerto con una variable sobrescrita solo para ese proceso (database
    inexistente, puerto incorrecto, credencial inválida de laboratorio) y la
    detiene al terminar. El .env y la API principal no se modifican.

    Requisito: la API principal debe estar iniciada (scripts\reiniciar_api.ps1).

.EXAMPLE
    .\hito11-conectividad\scripts\falla_controlada.ps1 -Producto mongodb

.EXAMPLE
    .\hito11-conectividad\scripts\falla_controlada.ps1 -Escenario config -Producto neo4j -Set "NEO4J_DATABASE=noexiste"
#>
param(
    [ValidateSet("detenida", "config")]
    [string]$Escenario = "detenida",

    [ValidateSet("mongodb", "neo4j", "cassandra", "redis", "influxdb", "iris")]
    [string]$Producto = "mongodb",

    [string[]]$Set = @(),

    [int]$PuertoTemporal = 8001,

    [int]$LimiteRecuperacion = 180
)

$ErrorActionPreference = "Stop"

$hitoRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path $hitoRoot -Parent

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = Join-Path $repoRoot ".venv/bin/python"
}
if (-not (Test-Path $python)) {
    throw "No se encontró el Python del entorno virtual (.venv). Ver README: 'Preparación'."
}

$argumentos = @(
    (Join-Path $PSScriptRoot "falla_controlada.py"),
    "--escenario", $Escenario,
    "--producto", $Producto,
    "--puerto-temporal", $PuertoTemporal,
    "--limite-recuperacion", $LimiteRecuperacion
)
foreach ($item in $Set) { $argumentos += @("--set", $item) }

Set-Location $repoRoot
$env:PYTHONIOENCODING = "utf-8"

& $python @argumentos
exit $LASTEXITCODE

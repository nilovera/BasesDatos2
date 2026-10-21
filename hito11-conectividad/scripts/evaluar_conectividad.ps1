<#
.SYNOPSIS
    Hito 11 - Evaluación reproducible de la conectividad de la API con sus productos NoSQL.

.DESCRIPTION
    Envoltorio de PowerShell para scripts\evaluar_conectividad.py. Usa el
    Python del entorno virtual de la API (.venv), es decir, los mismos
    drivers y el mismo origen de red que la API del Hito 10.

    Modos:
      completo  configuración + proceso/resolución/TCP + clientes nativos + API
                y regeneración de docs\matriz_de_conectividad.md
      config    solo variables de configuración (sin mostrar secretos)
      tcp       estado del contenedor, resolución de host y conexión TCP
      nativos   protocolo, autenticación, autorización, contexto y lectura mínima
      api       rutas de la API (cadena cliente HTTP - API - adaptador - producto)

    SKIP significa "prueba no ejecutada por falta de herramienta o
    configuración", NO "producto caído".

.EXAMPLE
    .\hito11-conectividad\scripts\evaluar_conectividad.ps1

.EXAMPLE
    .\hito11-conectividad\scripts\evaluar_conectividad.ps1 -Modo tcp

.EXAMPLE
    .\hito11-conectividad\scripts\evaluar_conectividad.ps1 -Modo nativos -Producto cassandra

.EXAMPLE
    .\hito11-conectividad\scripts\evaluar_conectividad.ps1 -Modo nativos -Producto neo4j -Set "NEO4J_DATABASE=noexiste" -Etiqueta contexto_incorrecto
#>
param(
    [ValidateSet("completo", "config", "tcp", "nativos", "api")]
    [string]$Modo = "completo",

    [ValidateSet("todos", "mongodb", "neo4j", "cassandra", "redis", "influxdb", "iris")]
    [string]$Producto = "todos",

    [string]$Etiqueta = "",

    [string[]]$Set = @(),

    [switch]$Cli,

    [switch]$SinEscritura,

    [string]$DesdeContenedor = "",

    [switch]$SinMatriz
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
    (Join-Path $PSScriptRoot "evaluar_conectividad.py"),
    "--modo", $Modo,
    "--producto", $Producto
)

if ($Etiqueta) { $argumentos += @("--etiqueta", $Etiqueta) }
foreach ($item in $Set) { $argumentos += @("--set", $item) }
if ($Cli) { $argumentos += "--cli" }
if ($SinEscritura) { $argumentos += "--sin-escritura" }
if ($DesdeContenedor) { $argumentos += @("--desde-contenedor", $DesdeContenedor) }
if ($SinMatriz) { $argumentos += "--sin-matriz" }

Set-Location $repoRoot
$env:PYTHONIOENCODING = "utf-8"

& $python @argumentos
$codigo = $LASTEXITCODE

Write-Host ""
if ($codigo -eq 0) {
    Write-Host "Resultado: ninguna capa requerida terminó en FALLA."
} else {
    Write-Host "Resultado: hay capas requeridas en FALLA. Ver hito11-conectividad\docs\matriz_de_conectividad.md y docs\evidencia."
}

exit $codigo

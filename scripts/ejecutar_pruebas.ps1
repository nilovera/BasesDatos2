$ErrorActionPreference = "Stop"

$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot

$python = Join-Path `
    $projectRoot `
    ".venv\Scripts\python.exe"

$evidenceDirectory = Join-Path `
    $projectRoot `
    "docs\evidencia"

$textReport = Join-Path `
    $evidenceDirectory `
    "09_pruebas_integracion.txt"

$xmlReport = Join-Path `
    $evidenceDirectory `
    "09_pruebas_integracion.xml"

$executionDate = Get-Date `
    -Format "yyyy-MM-ddTHH:mm:sszzz"

Write-Host "=== HITO 10 - PRUEBAS AUTOMATIZADAS ==="
Write-Host "Fecha de ejecucion: $executionDate"
Write-Host "Tipo: integracion con dependencias reales"
Write-Host "Motores: MongoDB, Neo4j, Cassandra, Redis, InfluxDB e IRIS"
Write-Host ""

$pytestOutput = @(
    & $python `
        -m pytest `
        ".\tests\integration\test_api_live.py" `
        -v `
        "--junitxml=$xmlReport" `
        2>&1
)

$exitCode = $LASTEXITCODE

$pytestOutput |
    ForEach-Object {
        Write-Host ([string]$_)
    }

$status = if ($exitCode -eq 0) {
    "APROBADO"
} else {
    "FALLIDO"
}

$reportLines = @(
    "=== HITO 10 - PRUEBAS AUTOMATIZADAS ==="
    "Fecha de ejecucion: $executionDate"
    "Tipo: integracion con dependencias reales"
    "Motores: MongoDB, Neo4j, Cassandra, Redis, InfluxDB e IRIS"
    "Resultado: $status"
    "Codigo de salida: $exitCode"
    ""
)

$reportLines += $pytestOutput |
    ForEach-Object {
        [string]$_
    }

$utf8SinBom = New-Object `
    System.Text.UTF8Encoding($false)

[System.IO.File]::WriteAllLines(
    $textReport,
    $reportLines,
    $utf8SinBom
)

Write-Host ""
Write-Host "=== EVIDENCIAS GENERADAS ==="
Write-Host $textReport
Write-Host $xmlReport

if ($exitCode -ne 0) {
    throw "La suite automatizada presentó errores."
}
param([int]$Iteraciones = 100)
$ErrorActionPreference = "Stop"
if ($Iteraciones -lt 20 -or $Iteraciones -gt 5000) { throw "Iteraciones debe estar entre 20 y 5000." }

function Measure-Endpoint {
    param([string]$Uri)
    $values = @()
    for ($i=0; $i -lt $Iteraciones; $i++) {
        $watch = [System.Diagnostics.Stopwatch]::StartNew()
        Invoke-RestMethod -Uri $Uri -TimeoutSec 10 | Out-Null
        $watch.Stop()
        $values += $watch.Elapsed.TotalMilliseconds
    }
    $ordered = @($values | Sort-Object)
    [ordered]@{
        iterations = $Iteraciones
        p50Ms = [math]::Round($ordered[[math]::Floor(($ordered.Count - 1) * 0.50)], 3)
        p95Ms = [math]::Round($ordered[[math]::Floor(($ordered.Count - 1) * 0.95)], 3)
        p99Ms = [math]::Round($ordered[[math]::Floor(($ordered.Count - 1) * 0.99)], 3)
        errors = 0
        throughputReqS = [math]::Round(($Iteraciones * 1000.0) / (($values | Measure-Object -Sum).Sum), 3)
    }
}

$operationalUri = "http://localhost:8000/api/v1/analitica/operacional/goles-por-equipo"
$datamartUri = "http://localhost:8000/api/v1/analitica/datamart/goles-por-equipo"
$operationalResult = Invoke-RestMethod -Uri $operationalUri -TimeoutSec 10
$datamartResult = Invoke-RestMethod -Uri $datamartUri -TimeoutSec 10
if (($operationalResult.items | ConvertTo-Json -Compress) -ne ($datamartResult.items | ConvertTo-Json -Compress)) {
    throw "Los resultados no son equivalentes; no corresponde comparar rendimiento."
}
$operational = Measure-Endpoint $operationalUri
$datamart = Measure-Endpoint $datamartUri
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("rendimiento-datamart-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$result = [ordered]@{
    scenario = "comparacion-consulta-goles-por-equipo"
    classification = "medido"
    warning = "Con un solo partido esto es una linea base funcional; no demuestra por si sola la mejora exigida por Hito 12."
    sourceCommit = (& git rev-parse HEAD).Trim()
    capturedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    equivalentResults = $true
    operational = $operational
    datamart = $datamart
}
$json = $result | ConvertTo-Json -Depth 5
$json | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "resultado.json")
$json
Write-Host "Evidencia: $outputDir"


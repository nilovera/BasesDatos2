$ErrorActionPreference = "Stop"

$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" $runId

function Save-JsonResponse {
    param(
        [string]$Uri,
        [string]$Path
    )
    $response = Invoke-RestMethod -Uri $Uri -TimeoutSec 10
    $response | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -Path $Path
}

$commit = (& git rev-parse HEAD).Trim()
$branch = (& git branch --show-current).Trim()
$status = @(& git status --short)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$metadata = [ordered]@{
    runId = $runId
    capturedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    capturedAtLocal = (Get-Date).ToString("o")
    commit = $commit
    branch = $branch
    scenario = "verificacion-incremento-03"
    classification = "medido"
    workingTreeClean = ($status.Count -eq 0)
}
$metadata | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "metadata.json")
if ($status.Count -eq 0) {
    "CLEAN" | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "git-status.txt")
} else {
    $status | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "git-status.txt")
}

& docker compose ps 2>&1 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "docker-compose-ps.txt")
if ($LASTEXITCODE -ne 0) { throw "No se pudo capturar docker compose ps." }

Save-JsonResponse -Uri "http://localhost:8000/health" -Path (Join-Path $outputDir "api-health.json")
Save-JsonResponse -Uri "http://localhost:8000/api/v1/partidos/PAR-0001" -Path (Join-Path $outputDir "partido-PAR-0001.json")
Save-JsonResponse -Uri "http://localhost:9090/api/v1/targets" -Path (Join-Path $outputDir "prometheus-targets.json")
Save-JsonResponse -Uri "http://localhost:9090/api/v1/rules" -Path (Join-Path $outputDir "prometheus-rules.json")

& powershell -ExecutionPolicy Bypass -File scripts\verificar_mongodb.ps1 2>&1 |
    Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "mongodb-verificacion.txt")
if ($LASTEXITCODE -ne 0) { throw "Fallo la verificacion de MongoDB." }

& python -m unittest discover -s tests -v 2>&1 |
    Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "pruebas-unitarias.txt")
if ($LASTEXITCODE -ne 0) { throw "Fallaron las pruebas unitarias." }

Write-Host "OK: evidencia guardada en $outputDir"
Write-Host "Revise los archivos para confirmar que no contienen secretos antes del commit."

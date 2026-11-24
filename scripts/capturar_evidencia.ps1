param(
    [ValidatePattern("^[a-zA-Z0-9._-]{3,80}$")]
    [string]$Scenario = "verificacion-integrada",
    [switch]$AllowDirty
)

$ErrorActionPreference = "Stop"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" $runId

function Save-JsonResponse {
    param([string]$Uri, [string]$Path)
    $response = Invoke-RestMethod -Uri $Uri -TimeoutSec 10
    $response | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 -Path $Path
}

function Save-PrometheusQuery {
    param([string]$Query, [string]$Path)
    $encoded = [System.Uri]::EscapeDataString($Query)
    Save-JsonResponse -Uri "http://localhost:9090/api/v1/query?query=$encoded" -Path $Path
}

function Invoke-CapturedProcess {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$OutputPath,
        [string]$FailureMessage
    )
    $absoluteOutput = [System.IO.Path]::GetFullPath($OutputPath)
    $stdoutPath = "$absoluteOutput.stdout.tmp"
    $stderrPath = "$absoluteOutput.stderr.tmp"
    $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList `
        -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    $combined = @()
    if (Test-Path $stdoutPath) { $combined += @(Get-Content -Path $stdoutPath) }
    if (Test-Path $stderrPath) { $combined += @(Get-Content -Path $stderrPath) }
    $combined | Set-Content -Encoding UTF8 -Path $absoluteOutput
    Remove-Item -Force -ErrorAction SilentlyContinue $stdoutPath, $stderrPath
    if ($process.ExitCode -ne 0) {
        throw "$FailureMessage (codigo $($process.ExitCode))."
    }
}

$commit = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw "No se pudo identificar el commit actual." }
$branch = (& git branch --show-current).Trim()
$status = @(& git status --short)
if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar git status." }
if ($status.Count -gt 0 -and -not $AllowDirty) {
    throw "El arbol de trabajo debe estar limpio. Mueva o versiona evidencias anteriores, o use -AllowDirty de forma explicita."
}

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$metadata = [ordered]@{
    runId = $runId
    capturedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    capturedAtLocal = (Get-Date).ToString("o")
    sourceCommit = $commit
    branch = $branch
    scenario = $Scenario
    classification = "medido"
    workingTreeCleanBeforeCapture = ($status.Count -eq 0)
}
$metadata | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "metadata.json")
if ($status.Count -eq 0) {
    "CLEAN" | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "git-status-antes.txt")
} else {
    $status | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "git-status-antes.txt")
}

Invoke-CapturedProcess -FilePath "docker" -ArgumentList @("compose", "ps") `
    -OutputPath (Join-Path $outputDir "docker-compose-ps.txt") `
    -FailureMessage "No se pudo capturar docker compose ps"

Save-JsonResponse -Uri "http://localhost:8000/health" -Path (Join-Path $outputDir "api-health.json")
Save-JsonResponse -Uri "http://localhost:8000/api/v1/partidos/PAR-0001" -Path (Join-Path $outputDir "partido-PAR-0001.json")
Save-JsonResponse -Uri "http://localhost:3000/api/health" -Path (Join-Path $outputDir "grafana-health.json")
Save-JsonResponse -Uri "http://localhost:9090/api/v1/targets" -Path (Join-Path $outputDir "prometheus-targets.json")
Save-JsonResponse -Uri "http://localhost:9090/api/v1/rules" -Path (Join-Path $outputDir "prometheus-rules.json")
Save-PrometheusQuery -Query 'up{job="fixture2030-api"}' -Path (Join-Path $outputDir "prometheus-api-up.json")
Save-PrometheusQuery -Query 'fixture2030_dependency_up' -Path (Join-Path $outputDir "prometheus-dependencias.json")
Save-PrometheusQuery -Query 'histogram_quantile(0.95, sum by (le) (rate(fixture2030_http_request_duration_seconds_bucket[5m])))' -Path (Join-Path $outputDir "prometheus-latencia-p95.json")
Save-PrometheusQuery -Query 'sum(rate(fixture2030_http_requests_total{route!="/health"}[1m]))' -Path (Join-Path $outputDir "prometheus-throughput.json")
Save-PrometheusQuery -Query 'sum(increase(fixture2030_http_requests_total{route!="/health",status=~"5.."}[5m]))' -Path (Join-Path $outputDir "prometheus-errores-5m.json")

$powershellPrefix = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File")
Invoke-CapturedProcess -FilePath "powershell" `
    -ArgumentList ($powershellPrefix + @("scripts\verificar_plataforma.ps1")) `
    -OutputPath (Join-Path $outputDir "plataforma-verificacion.txt") `
    -FailureMessage "Fallo la verificacion de la plataforma"
Invoke-CapturedProcess -FilePath "powershell" `
    -ArgumentList ($powershellPrefix + @("scripts\verificar_mongodb.ps1")) `
    -OutputPath (Join-Path $outputDir "mongodb-verificacion.txt") `
    -FailureMessage "Fallo la verificacion de MongoDB"
Invoke-CapturedProcess -FilePath "powershell" `
    -ArgumentList ($powershellPrefix + @("scripts\verificar_redis.ps1")) `
    -OutputPath (Join-Path $outputDir "redis-verificacion.txt") `
    -FailureMessage "Fallo la verificacion de Redis"
Invoke-CapturedProcess -FilePath "powershell" `
    -ArgumentList ($powershellPrefix + @("scripts\verificar_cassandra.ps1")) `
    -OutputPath (Join-Path $outputDir "cassandra-verificacion.txt") `
    -FailureMessage "Fallo la verificacion de Cassandra"
Invoke-CapturedProcess -FilePath "python" `
    -ArgumentList @("-m", "unittest", "discover", "-s", "tests", "-v") `
    -OutputPath (Join-Path $outputDir "pruebas-unitarias.txt") `
    -FailureMessage "Fallaron las pruebas unitarias"

$manifest = Get-ChildItem -Path $outputDir -File | Sort-Object Name | ForEach-Object {
    $hash = Get-FileHash -Algorithm SHA256 -Path $_.FullName
    [ordered]@{ file = $_.Name; sha256 = $hash.Hash.ToLowerInvariant(); bytes = $_.Length }
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path (Join-Path $outputDir "manifest-sha256.json")

Write-Host "OK: evidencia guardada en $outputDir"
Write-Host "Revise los archivos, agregue una captura de Grafana con esta ventana temporal y confirme que no contienen secretos antes del commit."

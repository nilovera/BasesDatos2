$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$runId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputDir = Join-Path "evidencia\ejecuciones" ("falla-datamart-" + $runId)
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Wait-State([double]$Expected, [int]$Attempts=30) {
    $query = "http://localhost:9090/api/v1/query?query=fixture2030_dependency_up%7Bdependency%3D%22datamart%22%7D"
    for ($i=0; $i -lt $Attempts; $i++) {
        try {
            Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5 | Out-Null
            $result = Invoke-RestMethod -Uri $query -TimeoutSec 5
            if (@($result.data.result).Count -gt 0 -and [double]$result.data.result[0].value[1] -eq $Expected) { return $Expected }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

function Wait-Alert {
    for ($i=0; $i -lt 30; $i++) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/alerts" -TimeoutSec 5
            $alert = @($response.data.alerts) | Where-Object { $_.labels.alertname -eq "Fixture2030DataMartDown" -and $_.state -eq "firing" } | Select-Object -First 1
            if ($alert) { return "firing" }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $null
}

$before = Wait-State 1
if ($null -eq $before) { throw "El Data Mart debe estar UP antes de la prueba." }
$commit = (& git rev-parse HEAD).Trim()
$capturedError = $null
$during = $null
$after = $null
$alert = $null
$officialRead = $false
$analyticalUnavailable = $false
$stopped = $false
try {
    Write-Host "Deteniendo solamente fixture2030-datamart..."
    docker stop fixture2030-datamart | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener el Data Mart." }
    $stopped = $true
    $during = Wait-State 0
    if ($null -eq $during) { throw "Prometheus no observo Data Mart DOWN." }
    $officialRead = (Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5).StatusCode -eq 200
    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/analitica/datamart/resumen" -TimeoutSec 5 | Out-Null
        throw "La consulta analitica debio responder 503."
    } catch {
        if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 503) { throw }
        $analyticalUnavailable = $true
    }
    $alert = Wait-Alert
    if ($alert -ne "firing") { throw "La alerta Fixture2030DataMartDown no llego a firing." }
    Write-Host "OK: Data Mart DOWN, alerta firing, analitica 503 y partido disponible."
} catch { $capturedError = $_.Exception.Message } finally {
    if ($stopped) {
        Write-Host "Recuperando fixture2030-datamart..."
        docker start fixture2030-datamart | Out-Null
    }
    $after = Wait-State 1 40
    if ($null -eq $after -and $null -eq $capturedError) { $capturedError = "El Data Mart no se recupero." }
    [ordered]@{
        runId="falla-datamart-$runId"; sourceCommit=$commit; scenario="falla-controlada-datamart";
        classification="medido"; dependencyUpBefore=$before; dependencyUpDuring=$during;
        datamartDownAlertDuring=$alert; officialReadAvailable=$officialRead;
        analyticalReadUnavailable=$analyticalUnavailable; dependencyUpAfter=$after;
        result=$(if ($null -eq $capturedError) { "OK" } else { "ERROR" }); error=$capturedError;
        safety="Solo se detuvo y reinicio fixture2030-datamart; no se eliminaron volumenes ni secretos."
    } | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $outputDir "resultado.json")
}
if ($capturedError) { throw $capturedError }
Write-Host "OK: Data Mart recuperado. Evidencia: $outputDir"


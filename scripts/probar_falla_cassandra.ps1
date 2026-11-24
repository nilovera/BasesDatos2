$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"
$stopped = $false
$capturedError = $null

try {
    Write-Host "Deteniendo solamente fixture2030-cassandra..."
    & docker stop fixture2030-cassandra | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "No se pudo detener Cassandra." }
    $stopped = $true

    $degraded = $false
    for ($attempt = 1; $attempt -le 20; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
            if ($health.status -eq "DEGRADED" -and $health.cassandra -eq "DOWN") {
                $degraded = $true
                break
            }
        } catch { }
        Start-Sleep -Seconds 3
    }
    if (-not $degraded) { throw "La API no detecto Cassandra DOWN." }

    $match = Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001" -TimeoutSec 5
    if ($match.StatusCode -ne 200) { throw "La consulta de partido debio continuar operativa." }

    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$baseUrl/api/v1/partidos/PAR-0001/comentarios?bucket=203006132000&limite=10" -TimeoutSec 5 | Out-Null
        throw "Comentarios debio responder 503 con Cassandra caida."
    } catch {
        if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 503) { throw }
    }
    Write-Host "OK: Cassandra DOWN, comentarios 503 y partido disponible desde MongoDB/Redis."
} catch {
    $capturedError = $_.Exception.Message
} finally {
    if ($stopped) {
        Write-Host "Recuperando fixture2030-cassandra..."
        & docker start fixture2030-cassandra | Out-Null
        if ($LASTEXITCODE -ne 0 -and $null -eq $capturedError) {
            $capturedError = "No se pudo reiniciar Cassandra."
        }
    }
    $recovered = $false
    for ($attempt = 1; $attempt -le 40; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 5
            if ($health.cassandra -eq "UP") { $recovered = $true; break }
        } catch { }
        Start-Sleep -Seconds 3
    }
    if (-not $recovered -and $null -eq $capturedError) {
        $capturedError = "Cassandra no se recupero en la API."
    }
}

if ($null -ne $capturedError) { throw $capturedError }
Write-Host "OK: Cassandra recuperada y API nuevamente UP."


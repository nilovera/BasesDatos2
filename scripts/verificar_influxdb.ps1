$ErrorActionPreference = "Stop"

Write-Host "Verificando InfluxDB, bases, tablas, API y metricas..."

$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
if ($health.influxdb -ne "UP") { throw "La API no informa InfluxDB UP." }

$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$tokenPath = Join-Path $projectRoot ".secretos\influxdb-admin-token.txt"
if (-not (Test-Path $tokenPath)) { throw "No existe el secreto local de InfluxDB." }
$token = (Get-Content -Raw -Path $tokenPath).Trim()
if ($token -notmatch '^apiv3_[A-Za-z0-9_-]{16,}$') {
    throw "El secreto local de InfluxDB no tiene el formato esperado."
}
$headers = @{ Authorization = "Bearer $token" }

function Invoke-InfluxSql {
    param([string]$Database, [string]$Sql)
    $payload = @{ db=$Database; q=$Sql; format="jsonl" } | ConvertTo-Json -Compress
    try {
        $response = Invoke-WebRequest `
            -UseBasicParsing `
            -Method Post `
            -Uri "http://localhost:8181/api/v3/query_sql" `
            -Headers $headers `
            -ContentType "application/json" `
            -Body $payload `
            -TimeoutSec 10
        if ($response.Content -is [byte[]]) {
            return [System.Text.Encoding]::UTF8.GetString($response.Content)
        }
        return [string]$response.Content
    } catch {
        throw "No se pudo consultar la base $Database en InfluxDB."
    }
}

$detailTables = Invoke-InfluxSql -Database "fixture2030-detalle" -Sql "SHOW TABLES"
foreach ($table in ("posiciones_jugador", "estadisticas_equipo")) {
    if ($detailTables -notmatch [regex]::Escape($table)) { throw "Falta la tabla $table." }
}

$historicalTables = Invoke-InfluxSql -Database "fixture2030-historico" -Sql "SHOW TABLES"
if ($historicalTables -notmatch "resumen_equipo_15m") { throw "Falta resumen_equipo_15m." }

$metric = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=up%7Bjob%3D%22fixture2030-influxdb%22%7D" -TimeoutSec 5
if (@($metric.data.result).Count -eq 0 -or [double]$metric.data.result[0].value[1] -ne 1) {
    throw "Prometheus no informa el target de InfluxDB UP."
}

$apiMetrics = (Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/metrics" -TimeoutSec 5).Content
if ($apiMetrics -notmatch 'fixture2030_dependency_up\{dependency="influxdb"\} 1') {
    throw "La API no expone la metrica de dependencia de InfluxDB."
}

Write-Host "OK: InfluxDB UP, dos bases, tres tablas, API y target Prometheus operativos."
Write-Host "NOTA: las retenciones 7d/365d se fijan al crear las bases; este chequeo no las vuelve a inferir por nombre."
Write-Host "NOTA: el token se leyo como secreto y no se imprimio en esta verificacion."

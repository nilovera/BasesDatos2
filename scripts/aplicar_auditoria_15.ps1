$ErrorActionPreference = "Stop"
$auditProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
Push-Location -LiteralPath $auditProjectRoot
try {
    docker compose config --quiet
    if ($LASTEXITCODE -ne 0) { throw "Configuracion Compose invalida." }
    docker compose up -d mongo cassandra
    if ($LASTEXITCODE -ne 0) { throw "No se pudo iniciar MongoDB/Cassandra." }
    $auditReady = $false
    for ($auditAttempt = 0; $auditAttempt -lt 90; $auditAttempt++) {
        docker compose exec -T cassandra cqlsh localhost 9042 -e "SELECT release_version FROM system.local;" *> $null
        if ($LASTEXITCODE -eq 0) { $auditReady = $true; break }
        Start-Sleep -Seconds 2
    }
    if (-not $auditReady) { throw "Cassandra no estuvo disponible. No se eliminaron datos; repetir cuando este listo." }
    # Se ejecutan los esquemas idempotentes; no se recrea el keyspace ni se truncan tablas.
    docker compose exec -T cassandra cqlsh localhost 9042 -f /opt/fixture2030/init/01_schema.cql
    if ($LASTEXITCODE -ne 0) { throw "No se pudo verificar el keyspace existente." }
    docker compose exec -T cassandra cqlsh localhost 9042 -f /opt/fixture2030/init/03_audit_schema.cql
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el esquema de auditoria." }
    docker compose exec -T mongo mongosh --quiet "mongodb://localhost:27017/?replicaSet=rs0" /opt/fixture2030/init/04_audit_schema.js
    if ($LASTEXITCODE -ne 0) { throw "No se pudo preparar la cola de auditoria en MongoDB." }
    docker compose up -d --build --no-deps api
    if ($LASTEXITCODE -ne 0) { throw "No se pudo reconstruir la API." }
    $auditReady = $false
    for ($auditAttempt = 0; $auditAttempt -lt 30; $auditAttempt++) {
        try {
            $auditContract = Invoke-RestMethod -Uri "http://localhost:8000/openapi.json" -TimeoutSec 3
            if ($auditContract.info.version -eq "0.10.0" -and
                $null -ne $auditContract.paths.'/api/v1/auditoria/pendientes') {
                $auditReady = $true; break
            }
        } catch { }
        Start-Sleep -Seconds 2
    }
    if (-not $auditReady) { throw "Revisar docker compose logs api: no se detecto la API actualizada." }
    Write-Host "OK: API 0.10.0 y auditoria disponibles. Swagger: http://localhost:8000/docs"
} finally {
    Pop-Location
}

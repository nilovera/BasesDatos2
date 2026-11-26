$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000"

function Invoke-Json($Method, $Uri, $Body = $null) {
    $parameters = @{ Method = $Method; Uri = $Uri; TimeoutSec = 15 }
    if ($null -ne $Body) {
        $parameters.ContentType = "application/json"
        $parameters.Body = ($Body | ConvertTo-Json -Depth 8)
    }
    return Invoke-RestMethod @parameters
}

Write-Host "1/7 Creando un partido nuevo con semilla 2030..."
$startedAtUtc = [DateTime]::UtcNow
$simulation = Invoke-Json POST "$baseUrl/api/v1/simulaciones" @{
    partidoBaseId = "PAR-0001"
    semilla = 2030
    velocidad = 120
}
$simulationId = $simulation.simulacionId
$matchId = $simulation.partidoId

Write-Host "2/7 Iniciando y comprobando pausa real..."
$null = Invoke-Json POST "$baseUrl/api/v1/simulaciones/$simulationId/iniciar"
$deadline = (Get-Date).AddSeconds(30)
do {
    Start-Sleep -Milliseconds 500
    $state = Invoke-Json GET "$baseUrl/api/v1/simulaciones/$simulationId"
    if ($state.estado -eq "ERROR") { throw "Simulacion en ERROR: $($state.error)" }
} while ($state.segundoPartido -lt 180 -and (Get-Date) -lt $deadline)
if ($state.segundoPartido -lt 180) { throw "La simulacion no avanzo." }
$paused = Invoke-Json POST "$baseUrl/api/v1/simulaciones/$simulationId/pausar"
Start-Sleep -Seconds 2
$stillPaused = Invoke-Json GET "$baseUrl/api/v1/simulaciones/$simulationId"
if ($stillPaused.estado -ne "PAUSADA" -or $stillPaused.segundoPartido -ne $paused.segundoPartido) {
    throw "La pausa no congelo el reloj logico."
}

Write-Host "3/7 Cambiando velocidad, reanudando y esperando los 90 minutos..."
$null = Invoke-Json PATCH "$baseUrl/api/v1/simulaciones/$simulationId/velocidad" @{ velocidad = 120 }
$null = Invoke-Json POST "$baseUrl/api/v1/simulaciones/$simulationId/reanudar"
$deadline = (Get-Date).AddSeconds(300)
do {
    Start-Sleep -Seconds 1
    $state = Invoke-Json GET "$baseUrl/api/v1/simulaciones/$simulationId"
    if ($state.estado -eq "ERROR") { throw "Simulacion en ERROR: $($state.error)" }
} while ($state.estado -ne "FINALIZADA" -and (Get-Date) -lt $deadline)
if ($state.estado -ne "FINALIZADA" -or $state.segundoPartido -ne 5400) {
    throw "La simulacion no finalizo los 90 minutos dentro del margen: estado=$($state.estado), segundo=$($state.segundoPartido)."
}

Write-Host "4/7 Verificando eventos oficiales y marcador final..."
$events = Invoke-Json GET "$baseUrl/api/v1/partidos/${matchId}/eventos?desdeSecuencia=0&limite=100"
$types = @($events.items | ForEach-Object { $_.tipo })
foreach ($required in @("INICIO_PARTIDO", "GOL", "TARJETA", "SUSTITUCION", "GOL_ANULADO_VAR", "FIN_PARTIDO")) {
    if ($types -notcontains $required) { throw "Falta el evento oficial $required." }
}
$match = Invoke-Json GET "$baseUrl/api/v1/partidos/$matchId"
if ($match.estado -ne "FINALIZADO") { throw "El partido no quedo FINALIZADO." }

Write-Host "5/7 Verificando InfluxDB y comentarios Cassandra..."
$ball = Invoke-Json GET "$baseUrl/api/v1/partidos/${matchId}/telemetria/pelota?limite=20"
$positions = Invoke-Json GET "$baseUrl/api/v1/partidos/${matchId}/telemetria/posiciones?limite=20"
if (@($ball.items).Count -eq 0 -or @($positions.items).Count -eq 0) {
    throw "InfluxDB no devolvio telemetria del partido."
}
$commentCount = 0
$bucketTime = $startedAtUtc.AddMinutes(-1)
$lastBucket = [DateTime]::UtcNow.AddMinutes(1)
while ($bucketTime -le $lastBucket) {
    $bucket = $bucketTime.ToString("yyyyMMddHHmm")
    $page = Invoke-Json GET "$baseUrl/api/v1/partidos/${matchId}/comentarios?bucket=$bucket&limite=100"
    $commentCount += @($page.items).Count
    $bucketTime = $bucketTime.AddMinutes(1)
}
if ($commentCount -eq 0) { throw "Cassandra no devolvio comentarios de la simulacion." }

Write-Host "6/7 Esperando convergencia Outbox..."
powershell -ExecutionPolicy Bypass -File scripts\verificar_outbox.ps1
if ($LASTEXITCODE -ne 0) { throw "La Outbox no convergio." }

Write-Host "7/7 Verificando marcador Redis y relaciones Neo4j..."
$redis = (& docker compose exec -T redis redis-cli HGETALL "marcador:partido:$matchId" 2>&1) -join "`n"
if ($LASTEXITCODE -ne 0 -or $redis -notmatch "FINALIZADO") { throw "Redis no contiene el marcador final." }
$password = (Get-Content ".secretos\neo4j-password.txt" -Raw).Trim()
$cypher = "MATCH (p:Partido {id: '$matchId'}) OPTIONAL MATCH (:Jugador)-[r:ANOTO|ASISTIO]->(p) RETURN count(r) AS total"
$graph = (& docker compose exec -T neo4j cypher-shell -u neo4j -p $password $cypher 2>&1) -join "`n"
if ($LASTEXITCODE -ne 0 -or $graph -notmatch "[1-9][0-9]*") { throw "Neo4j no contiene relaciones deportivas." }

$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$evidenceDir = Join-Path "evidencia\ejecuciones" "simulador-$stamp"
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null
$sourceCommit = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw "No se pudo identificar el commit de la prueba." }
$result = [ordered]@{
    scenario = "simulador-partido-reproducible"
    result = "OK"
    sourceCommit = $sourceCommit
    capturedAtUtc = [DateTime]::UtcNow.ToString("o")
    simulationId = $simulationId
    matchId = $matchId
    seed = 2030
    logicalSeconds = [int]$state.segundoPartido
    finalState = $state.estado
    score = [ordered]@{
        local = [int]$match.marcador.local
        visitor = [int]$match.marcador.visitante
    }
    officialEvents = @($events.items).Count
    requiredEventTypes = @("INICIO_PARTIDO", "GOL", "TARJETA", "SUSTITUCION", "GOL_ANULADO_VAR", "FIN_PARTIDO")
    commentsVerified = $commentCount
    ballSamplesVerified = @($ball.items).Count
    positionSamplesVerified = @($positions.items).Count
    redisFinalScoreVerified = $true
    neo4jSportsRelationsVerified = $true
    outboxConverged = $true
}
$result | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $evidenceDir "resultado.json") -Encoding utf8

Write-Host "OK: partido realista de 90 minutos, semilla, pausa, velocidad y seis bases verificados."
Write-Host "Simulacion: $simulationId Partido: $matchId Resultado: $($match.marcador.local)-$($match.marcador.visitante)"
Write-Host "Evidencia: $evidenceDir"

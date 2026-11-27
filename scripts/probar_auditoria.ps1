param([string]$BaseUrl = "http://localhost:8000/api/v1")
$ErrorActionPreference = "Stop"
$auditRunId = [guid]::NewGuid().ToString()
$auditRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$auditOutput = Join-Path $auditRoot ("evidencia\ejecuciones\auditoria-" + [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ"))
$auditSession = $null
function Send-AuditJson([string]$Method, [string]$Path, [object]$Body, [hashtable]$Headers) {
    Invoke-RestMethod -Method $Method -Uri "$BaseUrl$Path" -Headers $Headers `
        -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 10) -TimeoutSec 15
}
try {
    $auditSession = Send-AuditJson "Post" "/sesiones" @{ usuarioId = "USR-0900"; rol = "ADMIN"; ttlSegundos = 600 } @{}
    $auditHeaders = @{ "X-Session-ID" = $auditSession.sesionId; "X-Request-ID" = "audit-$auditRunId"; "Idempotency-Key" = "audit-publish-$auditRunId" }
    $auditCommentBody = @{ usuarioId = "USR-0900"; contenido = "Prueba reproducible de auditoria" }
    $auditComment = Send-AuditJson "Post" "/partidos/PAR-0001/comentarios" $auditCommentBody $auditHeaders
    $auditReplay = Send-AuditJson "Post" "/partidos/PAR-0001/comentarios" $auditCommentBody $auditHeaders
    if (-not $auditReplay.repetido -or $auditReplay.comentarioId -ne $auditComment.comentarioId) { throw "Publicacion no idempotente." }
    $auditResource = "/comentarios/$($auditComment.comentarioId)/moderacion"
    $auditHidden = @{ estado = "OCULTO"; moderadorId = "USR-0900"; motivo = "Prueba de ocultamiento" }
    $auditVisible = @{ estado = "VISIBLE"; moderadorId = "USR-0900"; motivo = "Prueba de restauracion" }
    $auditHeaders['Idempotency-Key'] = "audit-hide-$auditRunId"
    Send-AuditJson "Patch" $auditResource $auditHidden $auditHeaders | Out-Null
    $auditHeaders['Idempotency-Key'] = "audit-show-$auditRunId"
    Send-AuditJson "Patch" $auditResource $auditVisible $auditHeaders | Out-Null
    $auditHeaders['Idempotency-Key'] = "audit-hide-$auditRunId"
    Send-AuditJson "Patch" $auditResource $auditHidden $auditHeaders | Out-Null
    $auditDay = ([DateTimeOffset]::Parse($auditComment.creadoEn).UtcDateTime).ToString("yyyyMMdd")
    $auditItems = @()
    $auditCursor = $null
    do {
        $auditPath = "$BaseUrl/auditoria/recursos/COMENTARIO/$($auditComment.comentarioId)?dia=$auditDay&limite=1"
        if ($auditCursor) { $auditPath += "&cursor=$([uri]::EscapeDataString($auditCursor))" }
        $auditPage = Invoke-RestMethod -Uri $auditPath -Headers $auditHeaders -TimeoutSec 15
        $auditItems += @($auditPage.items)
        $auditCursor = $auditPage.siguienteCursor
    } while ($auditCursor)
    if ($auditItems.Count -ne 3 -or @($auditItems.auditoriaId | Select-Object -Unique).Count -ne 3) {
        throw "Se esperaban publicacion y dos moderaciones, sin duplicados." }
    if (@($auditItems | Where-Object actorTipo -ne 'SESION_LAB').Count -ne 0) { throw "Actor de laboratorio incorrecto." }
    $auditFeed = Invoke-RestMethod -Uri "$BaseUrl/usuarios/USR-0900/comentarios?bucket=$auditDay&limite=100" -Headers $auditHeaders -TimeoutSec 15
    if (@($auditFeed.items | Where-Object comentarioId -eq $auditComment.comentarioId).Count -ne 1) {
        throw "El replay de la moderacion antigua revirtio el estado visible." }
    $auditByActor = Invoke-RestMethod -Uri "$BaseUrl/auditoria/actores/USR-0900?dia=$auditDay&limite=100" -Headers $auditHeaders -TimeoutSec 15
    if (@($auditByActor.items | Where-Object recursoId -eq $auditComment.comentarioId).Count -ne 3) { throw "La vista por actor no coincide." }
    try {
        Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/auditoria/actores/USR-0900?dia=$auditDay" -TimeoutSec 15 | Out-Null
        throw "La auditoria no deberia ser publica."
    } catch {
        if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 403) { throw }
    }
    # Verifica el reenvio MongoDB -> Cassandra sin iniciar ni detener partidos.
    $auditSimulation = Send-AuditJson "Post" "/simulaciones" @{ semilla = 2030; velocidad = 30 } $auditHeaders
    $auditCreated = $false
    for ($auditAttempt = 0; $auditAttempt -lt 30; $auditAttempt++) {
        $auditDayNow = [DateTime]::UtcNow.ToString("yyyyMMdd")
        $auditPage = Invoke-RestMethod -Uri "$BaseUrl/auditoria/recursos/SIMULACION/$($auditSimulation.simulacionId)?dia=$auditDayNow" -Headers $auditHeaders -TimeoutSec 15
        if (@($auditPage.items | Where-Object accion -eq 'CREAR_SIMULACION').Count -eq 1) { $auditCreated = $true; break }
        Start-Sleep -Seconds 1
    }
    if (-not $auditCreated) { throw "La auditoria de la simulacion no llego a Cassandra. Revisar /auditoria/pendientes." }
    New-Item -ItemType Directory -Force -Path $auditOutput | Out-Null
    @{ fechaUtc = [DateTime]::UtcNow.ToString('o'); estado = 'OK'; comentarioId = $auditComment.comentarioId;
       simulacionId = $auditSimulation.simulacionId; operacionesComentario = $auditItems;
       duplicados = 0; consultaPublica = '403'; reenvioMongoCassandra = 'OK' } |
        ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 -Path (Join-Path $auditOutput 'resultado.json')
    Write-Host "OK: historial, reintentos, paginacion, actor y reenvio comprobados. Evidencia: $auditOutput"
    Write-Host "Se conserva un comentario de prueba y un cruce programado; no se inicio ningun partido."
} finally {
    if ($auditSession) {
        try { Invoke-RestMethod -Method Delete -Uri "$BaseUrl/sesiones/$($auditSession.sesionId)" -TimeoutSec 10 | Out-Null }
        catch { Write-Warning "La sesion temporal de prueba vencera por TTL." }
    }
}

$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000/api/v1"
$key = "comentario-demo-$([guid]::NewGuid().ToString())"
$headers = @{ "Idempotency-Key" = $key }
$body = @{ usuarioId = "USR-0003"; contenido = "Fixture2030 comentario reproducible" } | ConvertTo-Json

Write-Host "1/7 Publicando comentario..."
$first = Invoke-RestMethod -Method Post -Uri "$baseUrl/partidos/PAR-0001/comentarios" `
    -Headers $headers -ContentType "application/json" -Body $body -TimeoutSec 10
if ($first.repetido -ne $false) { throw "La primera escritura no puede ser replay." }

Write-Host "2/7 Repitiendo la misma clave y body..."
$replay = Invoke-RestMethod -Method Post -Uri "$baseUrl/partidos/PAR-0001/comentarios" `
    -Headers $headers -ContentType "application/json" -Body $body -TimeoutSec 10
if ($replay.comentarioId -ne $first.comentarioId -or $replay.repetido -ne $true) {
    throw "La repeticion no fue idempotente."
}

Write-Host "3/7 Verificando conflicto controlado..."
$conflictBody = @{ usuarioId = "USR-0003"; contenido = "Otro contenido" } | ConvertTo-Json
try {
    Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$baseUrl/partidos/PAR-0001/comentarios" `
        -Headers $headers -ContentType "application/json" -Body $conflictBody -TimeoutSec 10 | Out-Null
    throw "La reutilizacion de la clave debio responder 409."
} catch {
    if ($null -eq $_.Exception.Response -or [int]$_.Exception.Response.StatusCode -ne 409) { throw }
}

Write-Host "4/7 Consultando feed por partido, bucket y shards..."
$feed = Invoke-RestMethod -Uri "$baseUrl/partidos/PAR-0001/comentarios?bucket=$($first.bucket)&limite=20" -TimeoutSec 10
if (@($feed.items | Where-Object comentarioId -eq $first.comentarioId).Count -ne 1) {
    throw "El comentario no aparece una sola vez en el feed."
}

Write-Host "5/7 Consultando vista por usuario y dia..."
$dayBucket = $first.bucket.Substring(0, 8)
$profile = Invoke-RestMethod -Uri "$baseUrl/usuarios/USR-0003/comentarios?bucket=$dayBucket&limite=20" -TimeoutSec 10
if (@($profile.items | Where-Object comentarioId -eq $first.comentarioId).Count -ne 1) {
    throw "La vista por usuario no converge."
}

Write-Host "6/7 Ocultando el comentario en ambas vistas..."
$moderation = @{ estado = "OCULTO"; moderadorId = "USR-0001"; motivo = "Prueba administrativa" } | ConvertTo-Json
Invoke-RestMethod -Method Patch -Uri "$baseUrl/comentarios/$($first.comentarioId)/moderacion" `
    -ContentType "application/json" -Body $moderation -TimeoutSec 10 | Out-Null

Write-Host "7/7 Verificando feed publico y vista administrativa..."
$publicFeed = Invoke-RestMethod -Uri "$baseUrl/partidos/PAR-0001/comentarios?bucket=$($first.bucket)&limite=20" -TimeoutSec 10
if (@($publicFeed.items | Where-Object comentarioId -eq $first.comentarioId).Count -ne 0) {
    throw "El comentario oculto sigue visible en el feed publico."
}
$adminFeed = Invoke-RestMethod -Uri "$baseUrl/partidos/PAR-0001/comentarios?bucket=$($first.bucket)&limite=20&incluirOcultos=true" -TimeoutSec 10
$hidden = @($adminFeed.items | Where-Object comentarioId -eq $first.comentarioId)
if ($hidden.Count -ne 1 -or $hidden.estado -ne "OCULTO") {
    throw "La vista administrativa no recupera el comentario oculto."
}

Write-Host "OK: idempotencia, conflicto, dos vistas, shards y moderacion verificados."
Write-Host "Comentario de demostracion:" $first.comentarioId "bucket:" $first.bucket "shard:" $first.shard


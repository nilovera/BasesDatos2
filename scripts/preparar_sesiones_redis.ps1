$ErrorActionPreference = "Stop"

$contenedor = "fixture2030-redis"
$ultimoAcceso = (
    Get-Date
).ToUniversalTime().ToString(
    "yyyy-MM-ddTHH:mm:ssZ"
)

$claves = @(
    "sesion:SES-API-0001",
    "sesion:SES-API-CIERRE",
    "sesion:SES-API-EXPIRA"
)

docker exec $contenedor redis-cli DEL @claves

docker exec $contenedor redis-cli HSET `
    "sesion:SES-API-0001" `
    sesion_id "SES-API-0001" `
    usuario_id "USR-0001" `
    rol "fan" `
    ultimo_acceso $ultimoAcceso `
    estado "activa" `
    partido_actual "PAR-0001" `
    acciones "2"

docker exec $contenedor redis-cli EXPIRE `
    "sesion:SES-API-0001" 1800

docker exec $contenedor redis-cli HSET `
    "sesion:SES-API-CIERRE" `
    sesion_id "SES-API-CIERRE" `
    usuario_id "USR-0002" `
    rol "moderador" `
    ultimo_acceso $ultimoAcceso `
    estado "activa" `
    partido_actual "PAR-0001" `
    acciones "5"

docker exec $contenedor redis-cli EXPIRE `
    "sesion:SES-API-CIERRE" 1800

docker exec $contenedor redis-cli HSET `
    "sesion:SES-API-EXPIRA" `
    sesion_id "SES-API-EXPIRA" `
    usuario_id "USR-0003" `
    rol "fan" `
    ultimo_acceso $ultimoAcceso `
    estado "activa" `
    partido_actual "PAR-0001" `
    acciones "0"

docker exec $contenedor redis-cli EXPIRE `
    "sesion:SES-API-EXPIRA" 5

Write-Host "=== SESIONES PREPARADAS ==="

docker exec $contenedor redis-cli TTL `
    "sesion:SES-API-0001"

docker exec $contenedor redis-cli TTL `
    "sesion:SES-API-CIERRE"

docker exec $contenedor redis-cli TTL `
    "sesion:SES-API-EXPIRA"
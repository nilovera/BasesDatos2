<#
.SYNOPSIS
    Levanta y carga en esta notebook los seis motores del Fixture 2030 (hitos 4 a 9),
    prepara la API del Hito 10 y deja todo listo para ejecutar el Hito 11.

.DESCRIPTION
    Pasos (cada uno se puede repetir sin duplicar datos):
      1. Verifica Docker y Python.
      2. Crea el entorno virtual de la API (.venv) e instala requirements.txt.
      3. docker compose up -d (la primera vez descarga ~4 GB de imágenes).
      4. Espera a que cada motor responda con su propio cliente.
      5. Carga los datos de cada hito con los scripts originales del grupo:
           MongoDB  - schemas/01_validaciones.js + init-scripts/02_carga_datos.js (Hito 4)
           Neo4j    - estructura.cypher + carga.cypher + segundacarga.cypher (Hito 5)
           Cassandra- esquema.cql + carga_muestra.cql (Hito 6)
           Redis    - scripts/preparar_sesiones_redis.ps1 (Hito 10)
           InfluxDB - bases, tablas, 1.080 puntos y 12 resúmenes (Hito 8)
           IRIS     - clases Fixture.* (Hito 9) + partido PAR-0001
      6. Genera el .env de la API y config\conectividad.env del Hito 11.
      7. Muestra un resumen con las cantidades cargadas.

    No borra contenedores, volúmenes ni datos.

.EXAMPLE
    .\entorno-local\preparar_entorno.ps1
#>
param(
    [switch]$SinVenv,
    [int]$EsperaMaximaSegundos = 300
)

$ErrorActionPreference = "Continue"
$entorno = $PSScriptRoot
$repo = Split-Path $entorno -Parent
$secretos = Join-Path $entorno ".secretos"
New-Item -ItemType Directory -Force $secretos | Out-Null
Set-Location $entorno

function Titulo([string]$texto) {
    Write-Host ""
    Write-Host ("=== " + $texto + " ===") -ForegroundColor Cyan
}

function Ok([string]$texto) { Write-Host ("[OK]    " + $texto) -ForegroundColor Green }
function Aviso([string]$texto) { Write-Host ("[AVISO] " + $texto) -ForegroundColor Yellow }

function Falla([string]$texto) {
    Write-Host ("[FALLA] " + $texto) -ForegroundColor Red
    Write-Host "Copiá todo lo que aparece en esta ventana y compartilo para revisarlo." -ForegroundColor Red
    exit 1
}

function Ejecutar([string]$descripcion, [scriptblock]$bloque) {
    $salida = & $bloque 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Host $salida
        Falla $descripcion
    }
    return $salida
}

function Esperar([string]$nombre, [scriptblock]$prueba) {
    $inicio = Get-Date
    while (((Get-Date) - $inicio).TotalSeconds -lt $EsperaMaximaSegundos) {
        $global:LASTEXITCODE = 1
        $null = & $prueba 2>&1
        if ($LASTEXITCODE -eq 0) {
            Ok ("{0} responde ({1:N0} s)" -f $nombre, ((Get-Date) - $inicio).TotalSeconds)
            return
        }
        Start-Sleep -Seconds 5
    }
    Falla ("{0} no respondió en {1} segundos. Revisar: docker logs {2}" -f $nombre, $EsperaMaximaSegundos, $nombre)
}

function Secreto([string]$archivo, [scriptblock]$generar) {
    $ruta = Join-Path $secretos $archivo
    if (Test-Path $ruta) { return (Get-Content -Raw $ruta).Trim() }
    $valor = & $generar
    if (-not $valor) { return $null }
    [System.IO.File]::WriteAllText($ruta, $valor)
    return $valor
}

# -----------------------------------------------------------------------------
Titulo "1/7 Verificando Docker y Python"
# -----------------------------------------------------------------------------
$null = docker version --format "{{.Server.Version}}" 2>&1
if ($LASTEXITCODE -ne 0) {
    Falla "Docker no responde. Abrí Docker Desktop, esperá 'Engine running' y volvé a ejecutar."
}
Ok "Docker Desktop en ejecución"

$pythonExe = $null
$pythonArgs = @()
# Los drivers fijados en requirements.txt publican binarios para Python 3.10 a 3.14.
foreach ($candidato in @(@("py", "-3.12"), @("py", "-3.13"), @("py", "-3.11"), @("py", "-3.10"), @("py", "-3.14"), @("py", "-3"), @("python"))) {
    if (-not (Get-Command $candidato[0] -ErrorAction SilentlyContinue)) { continue }
    $extra = @()
    if ($candidato.Count -gt 1) { $extra = @($candidato[1]) }
    $global:LASTEXITCODE = 1
    $null = & $candidato[0] @extra -c "import sys; assert (3, 10) <= sys.version_info[:2] <= (3, 14)" 2>&1
    if ($LASTEXITCODE -eq 0) { $pythonExe = $candidato[0]; $pythonArgs = $extra; break }
}
if (-not $pythonExe) {
    Falla "No se encontró Python entre 3.10 y 3.14 (los drivers de IRIS y Cassandra no publican binarios para versiones más nuevas). Instalar Python 3.12 desde https://www.python.org/downloads/ (marcar 'Add python.exe to PATH') y volver a ejecutar."
}
Ok ("Python encontrado: " + $pythonExe + " " + ($pythonArgs -join " "))

# -----------------------------------------------------------------------------
Titulo "2/7 Entorno virtual de la API (.venv)"
# -----------------------------------------------------------------------------
$python = Join-Path $repo ".venv\Scripts\python.exe"
if (-not $SinVenv) {
    if (Test-Path $python) {
        $global:LASTEXITCODE = 1
        $null = & $python -c "import sys; assert (3, 10) <= sys.version_info[:2] <= (3, 14)" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Aviso ".venv existente creado con una versión de Python no compatible: se vuelve a crear."
            Remove-Item -Recurse -Force (Join-Path $repo ".venv")
        }
    }
    if (-not (Test-Path $python)) {
        Ejecutar "No se pudo crear el entorno virtual" { & $pythonExe @pythonArgs -m venv (Join-Path $repo ".venv") } | Out-Null
    }
    Write-Host "Instalando dependencias (puede tardar unos minutos la primera vez)..."
    Ejecutar "No se pudieron instalar las dependencias de requirements.txt" { & $python -m pip install --disable-pip-version-check -q -r (Join-Path $repo "requirements.txt") } | Out-Null
    Ok ".venv listo"
}

# -----------------------------------------------------------------------------
Titulo "3/7 Iniciando contenedores (la primera vez descarga ~4 GB)"
# -----------------------------------------------------------------------------
docker compose up -d
if ($LASTEXITCODE -ne 0) { Falla "docker compose up -d terminó con error" }
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=fixture2030-"

# -----------------------------------------------------------------------------
Titulo "4/7 Esperando a que cada motor responda"
# -----------------------------------------------------------------------------
Esperar "fixture2030-mongodb" { docker exec fixture2030-mongodb mongosh --quiet -u admin -p password123 --authenticationDatabase admin --eval "db.runCommand({ping:1}).ok" }
Esperar "fixture2030-redis" { docker exec fixture2030-redis redis-cli PING }
Esperar "fixture2030-neo4j" { docker exec fixture2030-neo4j cypher-shell -u neo4j -p fixture2030 "RETURN 1" }
Esperar "fixture2030-influxdb" {
    # /health responde 200, o 401 si exige token: en ambos casos el servicio HTTP está activo.
    $global:LASTEXITCODE = 1
    try {
        Invoke-WebRequest -Uri "http://127.0.0.1:8181/health" -UseBasicParsing -TimeoutSec 5 | Out-Null
        $global:LASTEXITCODE = 0
    } catch {
        if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 401) { $global:LASTEXITCODE = 0 }
    }
}
Esperar "fixture2030-iris" {
    $estado = docker inspect -f "{{.State.Health.Status}}" fixture2030-iris
    if ($estado -eq "healthy") { $global:LASTEXITCODE = 0 } else { $global:LASTEXITCODE = 1 }
}
Write-Host "Cassandra es el más lento en iniciar (1 a 3 minutos)..."
Esperar "fixture2030-cassandra" { docker exec fixture2030-cassandra cqlsh -e "DESCRIBE KEYSPACES" }

# -----------------------------------------------------------------------------
Titulo "5/7 Cargando los datos de cada hito"
# -----------------------------------------------------------------------------

# --- MongoDB (Hito 4) ---
Ejecutar "Validaciones de MongoDB" { docker exec fixture2030-mongodb mongosh --quiet -u admin -p password123 --authenticationDatabase admin /scripts/01_validaciones.js } | Out-Null
Ejecutar "Carga de MongoDB" { docker exec fixture2030-mongodb mongosh --quiet -u admin -p password123 --authenticationDatabase admin /scripts/02_carga_datos.js } | Out-Null
Ok "MongoDB: validaciones y carga del Hito 4"

# --- Neo4j (Hito 5) ---
foreach ($archivo in @("estructura.cypher", "carga.cypher", "segundacarga.cypher")) {
    Write-Host ("Neo4j: ejecutando " + $archivo + "...")
    Ejecutar ("Neo4j " + $archivo) { docker exec fixture2030-neo4j cypher-shell -u neo4j -p fixture2030 -f ("/scripts/" + $archivo) } | Out-Null
}
Ok "Neo4j: estructura y cargas del Hito 5"

# --- Cassandra (Hito 6) ---
Ejecutar "Esquema de Cassandra" { docker exec fixture2030-cassandra cqlsh -f /scripts/esquema.cql } | Out-Null
Ejecutar "Carga de muestra de Cassandra" { docker exec fixture2030-cassandra cqlsh -f /scripts/carga_muestra.cql } | Out-Null
Ok "Cassandra: esquema y carga de muestra del Hito 6"

# --- Redis (sesiones del Hito 10) ---
Ejecutar "Sesiones de Redis" { & (Join-Path $repo "scripts\preparar_sesiones_redis.ps1") } | Out-Null
Ok "Redis: sesiones de demostración (SES-API-0001 vence en 30 minutos; se renueva con scripts\preparar_sesiones_redis.ps1)"

# --- InfluxDB (Hito 8) ---
$token = Secreto "influxdb.token" {
    $json = docker exec fixture2030-influxdb influxdb3 create token --admin --format json 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { return $null }
    try { return ($json | ConvertFrom-Json).token } catch { return $null }
}
if (-not $token) {
    Falla ("No se pudo crear el token de InfluxDB. Si ya se había creado y se perdió el archivo " +
           "entorno-local\.secretos\influxdb.token, recrear solo InfluxDB con: " +
           "docker compose rm -sf influxdb ; docker volume rm fixture2030_influxdb_data ; y volver a ejecutar este script.")
}
$env:INFLUXDB3_AUTH_TOKEN = $token

foreach ($db in @(@("fixture2030_detalle", "7d"), @("fixture2030_historico", "365d"))) {
    $salida = docker exec --env INFLUXDB3_AUTH_TOKEN fixture2030-influxdb influxdb3 create database --retention-period $db[1] $db[0] 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -and $salida -notmatch "already exists") { Write-Host $salida; Falla ("Crear database " + $db[0]) }
}
$tablas = @(
    @("fixture2030_detalle", "estadisticas_equipo", "posesion_pct:float64,pases_intervalo:int64,tiros_acumulados:int64"),
    @("fixture2030_historico", "resumen_equipo_minuto", "posesion_promedio:float64,pases_total:int64,muestras:int64,ventana_inicio_ms:int64,ventana_fin_ms:int64")
)
foreach ($t in $tablas) {
    $salida = docker exec --env INFLUXDB3_AUTH_TOKEN fixture2030-influxdb influxdb3 create table --database $t[0] --tags "partido_id,equipo_id" --fields $t[2] $t[1] 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -and $salida -notmatch "already exists") { Write-Host $salida; Falla ("Crear tabla " + $t[1]) }
}
Ejecutar "Generación de puntos de InfluxDB" { & $python (Join-Path $entorno "datos\influxdb\generar_influx.py") } | Out-Null
Ejecutar "Carga de puntos detallados" { docker exec --env INFLUXDB3_AUTH_TOKEN fixture2030-influxdb influxdb3 write --database fixture2030_detalle --precision s --file /datos/generado/estadisticas_equipo.lp } | Out-Null
Ejecutar "Carga del resumen de 15 minutos" { docker exec --env INFLUXDB3_AUTH_TOKEN fixture2030-influxdb influxdb3 write --database fixture2030_historico --precision s --file /datos/generado/resumen_15m.lp } | Out-Null
Ok "InfluxDB: databases, tablas, 1.080 puntos y 12 resúmenes del Hito 8"

# --- IRIS (Hito 9) ---
$irisPassword = Secreto "iris.password" {
    -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 20 | ForEach-Object { [char]$_ })
}
$comandosSistema = @(
    'Do ##class(Security.Users).UnExpireUserPasswords("*")',
    ('Set p("Password")="' + $irisPassword + '",p("ChangePassword")=0,p("PasswordNeverExpires")=1 Set sc=##class(Security.Users).Modify("_SYSTEM",.p) Write "password_ok=",sc,!'),
    'Halt'
)
$salida = $comandosSistema | docker exec -i fixture2030-iris iris session IRIS -U %SYS 2>&1 | Out-String
if ($salida -notmatch "password_ok=1") { Write-Host $salida; Falla "No se pudo configurar el usuario _SYSTEM de IRIS" }

$comandosClases = @(
    'Do $system.OBJ.Load("/scripts/Fixture.Persona.cls","ck")',
    'Do $system.OBJ.Load("/scripts/Fixture.Arbitro.cls","ck")',
    'Do $system.OBJ.Load("/scripts/Fixture.Tecnico.cls","ck")',
    'Do $system.OBJ.Load("/scripts/Fixture.Partido.cls","k")',
    'Do $system.OBJ.Load("/scripts/Fixture.EventoPartido.cls","ck")',
    'Do $system.OBJ.Load("/scripts/Fixture.Partido.cls","ck")',
    'Do $system.OBJ.Load("/scripts/semilla_hito11.mac","ck")',
    'Do Main^FixtureSemillaH11',
    'Halt'
)
$salida = $comandosClases | docker exec -i fixture2030-iris iris session IRIS -U USER 2>&1 | Out-String
if ($salida -notmatch "Partidos: [1-9]") { Write-Host $salida; Falla "No se pudieron compilar las clases o crear PAR-0001 en IRIS" }
Ok "IRIS: clases Fixture.* compiladas y partido PAR-0001"

# -----------------------------------------------------------------------------
Titulo "6/7 Configuración local (.env y config\conectividad.env)"
# -----------------------------------------------------------------------------
$envPath = Join-Path $repo ".env"
if (Test-Path $envPath) {
    $respaldo = Join-Path $repo (".env.respaldo-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
    Copy-Item $envPath $respaldo
    Aviso (".env existente respaldado en " + (Split-Path $respaldo -Leaf))
}
$contenidoEnv = @"
APP_NAME='Fixture 2030 API'
APP_VERSION='1.0.0'
APP_ENV='local'
API_HOST='127.0.0.1'
API_PORT='8000'
LOG_LEVEL='INFO'
DEPENDENCY_TIMEOUT_SECONDS='5'
DEFAULT_PAGE_SIZE='20'
MAX_PAGE_SIZE='100'

MONGODB_HOST='127.0.0.1'
MONGODB_PORT='27017'
MONGODB_DATABASE='fixture2030'
MONGODB_AUTH_SOURCE='admin'
MONGODB_USERNAME='admin'
MONGODB_PASSWORD='password123'

NEO4J_URI='bolt://127.0.0.1:7687'
NEO4J_DATABASE='neo4j'
NEO4J_USERNAME='neo4j'
NEO4J_PASSWORD='fixture2030'

CASSANDRA_HOSTS='127.0.0.1'
CASSANDRA_PORT='9042'
CASSANDRA_KEYSPACE='fixture2030_comentarios'

REDIS_HOST='127.0.0.1'
REDIS_PORT='6379'
REDIS_DATABASE='0'

INFLUXDB_URL='http://127.0.0.1:8181'
INFLUXDB_TOKEN='$token'
INFLUXDB_DETAIL_DATABASE='fixture2030_detalle'
INFLUXDB_HISTORICAL_DATABASE='fixture2030_historico'

IRIS_HOST='127.0.0.1'
IRIS_PORT='1972'
IRIS_NAMESPACE='USER'
IRIS_USERNAME='_SYSTEM'
IRIS_PASSWORD='$irisPassword'
"@
[System.IO.File]::WriteAllText($envPath, $contenidoEnv, (New-Object System.Text.UTF8Encoding($false)))
Ok ".env de la API generado (fuera de Git)"

$conectividad = Join-Path $repo "hito11-conectividad\config\conectividad.env"
$contenidoConectividad = @"
# Generado por entorno-local\preparar_entorno.ps1 (no se versiona).
DIAG_ENTORNO=notebook Windows de Valentino - entorno-local consolidado
# El entorno local carga la muestra del Hito 6; su partición con datos es PAR-0001 / 203006132000.
CASSANDRA_BUCKET_DEMO=203006132000
"@
[System.IO.File]::WriteAllText($conectividad, $contenidoConectividad, (New-Object System.Text.UTF8Encoding($false)))
Ok "hito11-conectividad\config\conectividad.env generado (fuera de Git)"

# -----------------------------------------------------------------------------
Titulo "7/7 Resumen de datos cargados"
# -----------------------------------------------------------------------------
$m = docker exec fixture2030-mongodb mongosh --quiet -u admin -p password123 --authenticationDatabase admin fixture2030 --eval "print(db.equipos.countDocuments() + ' equipos, ' + db.jugadores.countDocuments() + ' jugadores')" 2>&1 | Out-String
Write-Host ("MongoDB   : " + $m.Trim() + "   (esperado: 64 equipos, 1024 jugadores)")
$n = docker exec fixture2030-neo4j cypher-shell -u neo4j -p fixture2030 --format plain "MATCH (p:Partido) WITH count(p) AS partidos MATCH (e:Evento) RETURN partidos, count(e) AS eventos" 2>&1 | Out-String
Write-Host ("Neo4j     : " + ($n.Trim() -replace "\r?\n", " | ") + "   (esperado: 96 partidos, 192 eventos)")
$c = docker exec fixture2030-cassandra cqlsh -e "SELECT COUNT(*) FROM fixture2030_comentarios.comentarios_por_partido WHERE partido_id='PAR-0001' AND bucket_10min='203006132000';" 2>&1 | Out-String
Write-Host ("Cassandra : " + (($c -split "\r?\n" | Where-Object { $_ -match "^\s*\d+\s*$" }) -join "").Trim() + " comentarios en PAR-0001/203006132000   (esperado: 6)")
$r = docker exec fixture2030-redis redis-cli TTL sesion:SES-API-0001 2>&1 | Out-String
Write-Host ("Redis     : TTL de sesion:SES-API-0001 = " + $r.Trim() + " s")
$i = docker exec --env INFLUXDB3_AUTH_TOKEN fixture2030-influxdb influxdb3 query --database fixture2030_detalle --format csv "SELECT COUNT(*) AS puntos FROM estadisticas_equipo" 2>&1 | Out-String
Write-Host ("InfluxDB  : " + ($i.Trim() -replace "\r?\n", " ") + "   (esperado: 1080)")
Write-Host "IRIS      : PAR-0001 creado (ver detalle arriba)"

Write-Host ""
Write-Host "Entorno listo. Siguientes pasos:" -ForegroundColor Cyan
Write-Host "  1) .\scripts\reiniciar_api.ps1"
Write-Host "  2) .\hito11-conectividad\scripts\evaluar_conectividad.ps1"
Write-Host "  3) .\hito11-conectividad\scripts\falla_controlada.ps1 -Producto mongodb"
Write-Host ""
Write-Host "Para apagar sin perder datos: docker compose -f entorno-local\docker-compose.yml stop"
Write-Host "NO usar 'docker compose down -v': borra los volúmenes con los datos."

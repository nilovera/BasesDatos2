# Capas de evaluación

La evaluación avanza **de menor a mayor costo** (sección 5.2). Una capa requerida que falla **bloquea** las siguientes: no se ejecutan y se registran como `BLOQUEADA`, no como "caídas". Así cada falla queda asociada a una sola capa.

```
Configuración → (Proceso) → Resolución → TCP → Protocolo → Autenticación → Autorización → Contexto → Lectura mínima → Endpoint de la API
```

## 1. Qué responde cada capa y qué no permite concluir

| Capa | Pregunta que responde | Lo que **todavía no** permite concluir | Script |
|---|---|---|---|
| Configuración | ¿El entorno sabe a qué host, puerto y contexto conectarse y con qué identidad? | Que el host exista o que la credencial sea válida | `prueba_config.py` |
| Proceso (informativa) | ¿Docker informa el contenedor como `running` y qué puertos publica? | Que el producto acepte conexiones: **un contenedor activo no es una dependencia disponible** | `prueba_tcp.py` |
| Resolución | ¿El nombre se convierte en una IP **desde el entorno de la API**? | Que haya un proceso escuchando | `prueba_tcp.py` |
| TCP | ¿Hay un listener que acepta conexiones en host:puerto? | Que sea el producto correcto, que la identidad sea válida o que exista el contexto | `prueba_tcp.py` |
| Protocolo | ¿El listener habla el protocolo esperado (Wire, Bolt, CQL, RESP, HTTP, Superserver)? | Que la identidad sea aceptada | `prueba_clientes_nativos.py` |
| Autenticación | ¿El servidor acepta la identidad configurada? | Que tenga permisos o que exista el contexto | ídem |
| Autorización | ¿La identidad puede operar sobre el contexto/objeto? | Que existan los datos de demostración | ídem |
| Contexto | ¿Existe la database / keyspace / namespace / tabla configurada? | Que una consulta concreta devuelva datos | ídem |
| Lectura mínima | ¿Una operación acotada, de solo lectura, funciona con límite de tiempo? | Rendimiento con volumen o concurrencia (Hito 12) | ídem |
| Endpoint de API | ¿La cadena cliente HTTP → API → adaptador → producto responde según el contrato? | Capacidad bajo carga | `prueba_api.py` |

## 2. Pruebas por producto

Las pruebas marcadas **(N)** son pruebas **negativas controladas**: provocan a propósito un caso de ausencia o error y verifican que el diagnóstico lo distinga de una falla de conexión. No son requeridas para declarar disponible al producto.

### MongoDB — `pymongo`

| Capa | Prueba | Distingue |
|---|---|---|
| TCP | socket a `MONGODB_HOST:MONGODB_PORT` | listener presente / refused / timeout / host no resuelto |
| Protocolo | `hello` **sin credenciales** | MongoDB Wire Protocol vs. otro servicio en el puerto |
| Autenticación | `connectionStatus` con credenciales sobre `authSource` | `OperationFailure 18` = credencial inválida |
| Autorización | `listCollections` sobre `fixture2030` | `OperationFailure 13` = sin permiso |
| Contexto | la database existe y tiene `equipos` y `jugadores` | database inexistente (MongoDB no la rechaza) |
| Lectura | `find_one({_id:"EQ-01"})` con proyección y `maxTimeMS` + conteos estimados | documento presente |
| (N) | `find_one({_id:"EQ-99"})` | documento inexistente → `None`, **no** es un error |
| (N) | `list_collection_names()` en una database inexistente | MongoDB devuelve vacío **sin error**: el contexto mal escrito no se detecta solo |

**Cliente nativo funcionando, pero la API fallando:** si el modo `nativos` termina OK y `GET /api/v1/equipos/EQ-01` devuelve 503, la falla está en la configuración que leyó la API (`.env` distinto, API iniciada antes del cambio) o en el adaptador. El siguiente paso es reiniciar la API y comparar el bloque "configuración" de ambas evidencias.

### Neo4j — `neo4j` driver + handshake Bolt manual

| Capa | Prueba | Distingue |
|---|---|---|
| Protocolo (complementaria) | `GET` al Browser HTTP (7474) | portal accesible; **no prueba Bolt** |
| Protocolo | handshake Bolt real (`0x6060B017` + versiones) **sin credenciales** | Bolt vs. HTTP u otro servicio en el puerto |
| Autenticación | `verify_authentication()` + `get_server_info()` | credencial inválida (`AuthError`) |
| Contexto | `RETURN 1` en la database configurada | `DatabaseNotFound` |
| Autorización | `MATCH (e:Equipo) RETURN count(e)` en modo READ | `Forbidden` |
| Lectura | Cypher **parametrizado** `$codigo` con `timeout` | partido presente |
| (N) | mismo Cypher con `PAR-9999` | resultado vacío ≠ error de conexión |
| (N) | `RETURN 1` en una database inexistente | error identificable `DatabaseNotFound` |

### Cassandra — `cassandra-driver`

| Capa | Prueba | Distingue |
|---|---|---|
| Protocolo | sesión CQL sin keyspace + `system.local` | versión del protocolo nativo, versión de Cassandra |
| Autenticación | mecanismo configurado | `N/A` en el laboratorio (sin autenticador): se informa, no se inventa |
| Contexto | keyspace en `system_schema.keyspaces` + `set_keyspace` | keyspace inexistente |
| Contexto | columnas de la tabla en `system_schema.columns` | tabla inexistente; se registra la clave de partición real |
| Autorización | `SELECT ... LIMIT 1` sobre la tabla | `Unauthorized` |
| Lectura | partición `(partido_id, bucket_10min)` con `LIMIT 3` | filas presentes |
| (N) | partición `PAR-9999` | lista vacía ≠ timeout |
| (N) | keyspace y tabla inexistentes | `InvalidRequest` identificable |
| (N) | `SELEC ...` (CQL inválido) | `SyntaxException` inmediata ≠ timeout de conexión |

### Redis — RESP manual + `redis-py`

| Capa | Prueba | Distingue |
|---|---|---|
| Protocolo | `PING` en RESP crudo por socket | RESP válido vs. otro servicio (puerto incorrecto); `-NOAUTH` |
| Autenticación | `AUTH` si hay password; si no, `N/A` documentado | `NOAUTH` / credencial inválida |
| Contexto | db lógica configurada: `DBSIZE`, `INFO server` | base accesible |
| Lectura | `EXISTS` + `TTL` de `sesion:SES-API-0001` | vigente (TTL > 0) / sin expiración (TTL -1) / **ausente o expirada (TTL -2)** |
| (N) | clave `diag:hito11:*` con `EX 2`, se relee a los 2,5 s | clave expirada = `EXISTS 0`, igual que ausente; ambas ≠ Redis caído (`ConnectionError`) |

La clave `diag:hito11:*` es la **única escritura** del diagnóstico: no pertenece al dominio y expira sola a los 2 segundos. Se desactiva con `-SinEscritura`.

### InfluxDB 3 — HTTP API v3 con `httpx`

| Capa | Prueba | Distingue |
|---|---|---|
| Protocolo | `GET /health` sin token | 200 (health abierto) o 401 (responde y exige token): ambos prueban HTTP vivo |
| Autenticación | `GET /health` con token Bearer | 401 = token inválido |
| (N) | `GET /health` con un token falso | el servidor diferencia token válido de inválido |
| Contexto | `GET /api/v3/configure/database` | databases de detalle e histórico presentes |
| Autorización | `SELECT 1` sobre la database de detalle | 403 = token sin permiso |
| Lectura | `COUNT/MIN/MAX` en `estadisticas_equipo`, partido y ventana de 1 minuto parametrizados | puntos presentes; rango y agregación quedan registrados |
| Lectura (complementaria) | `COUNT` en `resumen_equipo_minuto` (31 minutos) | la database histórica (downsampling) responde |
| (N) | ventana de 2031 | 0 puntos con HTTP 200 = ausencia de puntos ≠ error |
| (N) | database inexistente | error de contexto ≠ token inválido ≠ servicio caído |

### InterSystems IRIS — DB-API

| Capa | Prueba | Distingue |
|---|---|---|
| Protocolo (complementaria) | `GET /csp/sys/UtilHome.csp` en el puerto 52773 | portal accesible; **no prueba el Superserver** |
| Protocolo / Autenticación / Contexto | un único `connect(host, 1972, namespace, usuario, password, timeout)` | el driver hace las tres cosas en una llamada: el error se descompone por capa (`COMMUNICATION LINK` → protocolo/TCP; `Access Denied` → autenticación; mensaje de namespace → contexto) |
| Autorización | `INFORMATION_SCHEMA.TABLES` del esquema `Fixture` | metadatos legibles y clases compiladas |
| Lectura | `Fixture.Partido WHERE Codigo = ?` | entidad presente |
| (N) | `PAR-9999` | objeto inexistente ≠ Superserver inaccesible |
| (N) | `connect` a un namespace inexistente | IRIS responde `Access Denied`, igual que ante una credencial inválida (no revela qué namespaces existen). Como las mismas credenciales funcionan en `USER`, el rechazo se atribuye al namespace; un Superserver inaccesible, en cambio, no llega a responder |

## 3. Clientes CLI dentro del contenedor (opcional)

Con `-Cli` se ejecuta además el cliente oficial de cada producto dentro de su contenedor (`mongosh`, `cypher-shell`, `cqlsh`, `redis-cli`, `influxdb3`, `iris list`). Si Docker o el CLI no están disponibles, el resultado es `SKIP` (no "caído").

Estas pruebas tienen **otro origen** (dentro del contenedor, puerto interno): sirven para separar "el producto no funciona" de "la API no lo alcanza", pero **no** reemplazan las pruebas desde la notebook.

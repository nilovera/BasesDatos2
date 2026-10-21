# Matriz de conectividad

> Archivo **generado** por `scripts/evaluar_conectividad.py --modo completo`. No editar a mano: volver a ejecutar el script para actualizarlo.

## Contexto de la ejecución

| Campo | Valor |
|---|---|
| fecha | 2026-10-21T19:05:03-03:00 |
| entorno | notebook Windows de Valentino - entorno-local consolidado |
| origen de las pruebas | notebook (mismo proceso/entorno desde el que corre la API) |
| sistema operativo | Windows-10 |
| python | 3.12.9 |
| rama | Conectividad |
| commit | d2bed7c (con cambios sin commit) |
| timeout por prueba s | 3.0 |
| api base url | http://127.0.0.1:8000 |
| modo | completo |

**Significado de OK:** la prueba concreta funcionó en este momento y desde este origen. No es garantía de rendimiento, escalabilidad ni disponibilidad permanente (RNF17).

## Estado por dependencia

| Producto | Módulo | Estado | Última capa superada | Latencia lectura mínima | Ruta principal de la API | Diagnóstico |
|---|---|---|---|---|---|---|
| MongoDB | Equipos y jugadores (Hito 4) | **disponible** | api | 2.0 ms | HTTP 200 (esperado [200]) (operacion_exitosa) | todas las capas requeridas probadas terminaron OK |
| Neo4j | Partidos, equipos, sedes y eventos (Hito 5) | **disponible** | api | 2.1 ms | HTTP 200 (esperado [200]) (operacion_exitosa) | todas las capas requeridas probadas terminaron OK |
| Cassandra | Comentarios por partido (Hito 6) | **disponible** | api | 15.0 ms | HTTP 200 (esperado [200]) (operacion_exitosa) | todas las capas requeridas probadas terminaron OK |
| Redis | Sesiones con expiración (Hito 7) | **disponible** | api | 0.6 ms | HTTP 200 (esperado [200, 404]) (operacion_exitosa) | todas las capas requeridas probadas terminaron OK |
| InfluxDB | Estadísticas temporales (Hito 8) | **disponible** | api | 4.5 ms | HTTP 200 (esperado [200]) (operacion_exitosa) | todas las capas requeridas probadas terminaron OK |
| InterSystems IRIS | Objetos persistentes de partido (Hito 9) | **disponible** | api | 2.3 ms | HTTP 200 (esperado [200]) (operacion_exitosa) | todas las capas requeridas probadas terminaron OK |
| API Fixture 2030 | API integrada (Hito 10) | **disponible** | api | - | - | todas las capas requeridas probadas terminaron OK |

## Resultado por capa

Se muestra el peor resultado de las pruebas **requeridas** de cada capa. OK = funcionó · FALLA = se intentó y falló · ADV = funcionó con observación · N/A = la capa no existe en este entorno · BLOQ = no se ejecutó por una falla anterior · SKIP = no se ejecutó por falta de herramienta o configuración (no significa producto caído).

| Producto | configuracion | proceso | resolucion | tcp | protocolo | autenticacion | autorizacion | contexto | operacion | api |
|---|---|---|---|---|---|---|---|---|---|---|
| MongoDB | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| Neo4j | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| Cassandra | OK | OK | OK | OK | OK | N/A | OK | OK | OK | OK |
| Redis | OK | OK | OK | OK | OK | N/A | - | OK | OK | OK |
| InfluxDB | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| InterSystems IRIS | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| API Fixture 2030 | - | - | OK | OK | - | - | - | - | - | OK |

## Detalle de pruebas

### MongoDB

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| configuracion | variables requeridas presentes | `127.0.0.1:27017` | lectura de configuración | OK | configuracion_completa | - | destino=127.0.0.1:27017; protocolo=MongoDB Wire Protocol (TCP); database=fixture2030; authSource=admin; autenticacion=SCRAM con usuario presente (valor oculto) y password presente (valor oculto); origen de valores=.env (API) |
| proceso | estado del contenedor (docker inspect) *(complementaria)* | `fixture2030-mongodb` | docker CLI | OK | contenedor_en_ejecucion | - | contenedor=fixture2030-mongodb; estado=running; health=sin healthcheck; iniciado=2026-10-21T21:59:16.866613884Z; puertos (interno->publicado)=27017/tcp->0.0.0.0:27017, 27017/tcp->:::27017 |
| resolucion | resolución de 127.0.0.1 | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 3.3 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | puerto MongoDB (MongoDB wire) | `127.0.0.1:27017` | socket TCP | OK | conexion_exitosa | 1.1 ms | listener aceptó la conexión en 127.0.0.1:27017 (origen 127.0.0.1) en 1.0 ms |
| protocolo | comando hello sin credenciales | `127.0.0.1:27017/fixture2030` | pymongo 4.18.3 | OK | handshake_ok | 4.7 ms | hello respondió: isWritablePrimary=True, maxWireVersion=21, version servidor=7.0.40 |
| autenticacion | connectionStatus con credenciales | `127.0.0.1:27017/fixture2030` | pymongo 4.18.3 | OK | autenticado | 23.4 ms | 1 identidad autenticada contra authSource=admin; roles=root (nombre de usuario omitido) |
| autorizacion | listCollections sobre fixture2030 | `127.0.0.1:27017/fixture2030` | pymongo 4.18.3 | OK | autorizado | 0.7 ms | listCollections permitido sobre 'fixture2030' (2 colecciones) |
| contexto | database y colecciones del módulo | `127.0.0.1:27017/fixture2030` | pymongo 4.18.3 | OK | contexto_ok | 1.1 ms | database 'fixture2030' existe con colecciones equipos y jugadores |
| operacion | find_one equipos {_id:EQ-01} con proyección | `127.0.0.1:27017/fixture2030` | pymongo 4.18.3 | OK | lectura_ok | 2.0 ms | find_one({_id:'EQ-01'}) devolvió campos ['_id', 'confederacion', 'nombre', 'ranking']; conteo estimado equipos=64, jugadores=1024 |
| operacion | prueba negativa controlada: documento inexistente EQ-99 *(complementaria)* | `127.0.0.1:27017/fixture2030` | pymongo 4.18.3 | OK | recurso_inexistente | 0.7 ms | EQ-99 devolvió None: ausencia válida, no es un error de conexión |
| contexto | prueba negativa controlada: database inexistente *(complementaria)* | `127.0.0.1:27017/fixture2030` | pymongo 4.18.3 | OK | contexto_inexistente_silencioso | 0.7 ms | database 'fixture2030_diag_inexistente': list_collection_names devolvió 0 colecciones sin error. MongoDB no falla ante una database o colección inexistente; por eso la API valida el contexto en /health/dependencias. |
| api | GET /api/v1/equipos/EQ-01 (operación exitosa) | `http://127.0.0.1:8000/api/v1/equipos/EQ-01` | httpx -> API -> adaptador MongoDB | OK | operacion_exitosa | 2.9 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: codigo=EQ-01; fuente_datos=MongoDB; X-Request-ID enviado=igual; X-Process-Time-Ms=1.76 |
| api | GET /api/v1/equipos/EQ-99 (recurso inexistente) | `http://127.0.0.1:8000/api/v1/equipos/EQ-99` | httpx -> API -> adaptador MongoDB | OK | recurso_inexistente | 2.5 ms | status=404 (esperado [404]); 404 RECURSO_NO_ENCONTRADO: la dependencia respondió y el recurso no existe; resumen: error.codigo=RECURSO_NO_ENCONTRADO; X-Request-ID enviado=igual; X-Process-Time-Ms=1.47 |
| api | GET /api/v1/equipos/ARG (error de validación) | `http://127.0.0.1:8000/api/v1/equipos/ARG` | httpx -> API -> adaptador MongoDB | OK | error_validacion | 1.5 ms | status=422 (esperado [422]); 422 DATOS_INVALIDOS: rechazado por la API antes de consultar la dependencia; resumen: error.codigo=DATOS_INVALIDOS; X-Request-ID enviado=igual; X-Process-Time-Ms=0.43 |
| api | GET /api/v1/jugadores (lectura paginada) | `http://127.0.0.1:8000/api/v1/jugadores?equipo_codigo=EQ-01&limit=3` | httpx -> API -> adaptador MongoDB | OK | operacion_exitosa | 4.9 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: fuente_datos=MongoDB; datos=3; X-Request-ID enviado=igual; X-Process-Time-Ms=3.81 |

### Neo4j

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| configuracion | variables requeridas presentes | `127.0.0.1:7687 (Bolt) / 127.0.0.1:7474 (HTTP Browser)` | lectura de configuración | OK | configuracion_completa | - | destino=127.0.0.1:7687 (Bolt) / 127.0.0.1:7474 (HTTP Browser); protocolo=Bolt (aplicación) y HTTP (portal); database=neo4j; autenticacion=basic auth Bolt con usuario presente (valor oculto) y password presente (valor oculto); origen de valores=.env (API) |
| proceso | estado del contenedor (docker inspect) *(complementaria)* | `fixture2030-neo4j` | docker CLI | OK | contenedor_en_ejecucion | - | contenedor=fixture2030-neo4j; estado=running; health=sin healthcheck; iniciado=2026-10-21T21:29:51.551610933Z; puertos (interno->publicado)=7474/tcp->0.0.0.0:7474, 7474/tcp->:::7474, 7687/tcp->0.0.0.0:7687, 7687/tcp->:::7687 |
| resolucion | resolución de 127.0.0.1 | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | puerto Bolt (usado por la API) (Bolt) | `127.0.0.1:7687` | socket TCP | OK | conexion_exitosa | 0.4 ms | listener aceptó la conexión en 127.0.0.1:7687 (origen 127.0.0.1) en 0.4 ms |
| resolucion | resolución de 127.0.0.1 *(complementaria)* | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | puerto HTTP Browser (no usado por la API) (HTTP) *(complementaria)* | `127.0.0.1:7474` | socket TCP | OK | conexion_exitosa | 0.3 ms | listener aceptó la conexión en 127.0.0.1:7474 (origen 127.0.0.1) en 0.3 ms |
| protocolo | portal HTTP / Browser *(complementaria)* | `http://127.0.0.1:7474` | httpx | OK | portal_http_ok | 338.1 ms | HTTP 200; neo4j_version=2026.10.0; bolt anunciado=bolt://127.0.0.1:7687 |
| protocolo | handshake Bolt (sin credenciales) | `127.0.0.1:7687/neo4j` | socket (handshake Bolt manual) | OK | handshake_ok | 3.1 ms | handshake Bolt aceptado; versión negociada 6.0 |
| autenticacion | verify_authentication | `127.0.0.1:7687/neo4j` | neo4j-python-driver 6.4.0 | OK | autenticado | 68.4 ms | credenciales aceptadas; agent=Neo4j/2026.10.0; protocolo Bolt=(6, 1) |
| contexto | selección de database neo4j | `127.0.0.1:7687/neo4j` | neo4j-python-driver 6.4.0 | OK | contexto_ok | 2.3 ms | database 'neo4j' seleccionada y operativa (RETURN 1) |
| autorizacion | lectura en modo READ sobre :Equipo | `127.0.0.1:7687/neo4j` | neo4j-python-driver 6.4.0 | OK | autorizado | 1.8 ms | lectura permitida; nodos :Equipo=64 |
| operacion | Cypher parametrizado partido PAR-0001 | `127.0.0.1:7687/neo4j` | neo4j-python-driver 6.4.0 | OK | lectura_ok | 2.1 ms | Cypher parametrizado ($codigo=PAR-0001): equipos=2, eventos=2 |
| operacion | prueba negativa controlada: partido inexistente PAR-9999 *(complementaria)* | `127.0.0.1:7687/neo4j` | neo4j-python-driver 6.4.0 | OK | recurso_inexistente | 3.8 ms | PAR-9999: resultado vacío sin error (ausencia válida ≠ error de conexión) |
| contexto | prueba negativa controlada: database inexistente *(complementaria)* | `127.0.0.1:7687/neo4j` | neo4j-python-driver 6.4.0 | OK | contexto_inexistente | 2.9 ms | error esperado: Neo.ClientError.Database.DatabaseNotFound |
| api | GET /api/v1/partidos/PAR-0001/eventos (operación exitosa) | `http://127.0.0.1:8000/api/v1/partidos/PAR-0001/eventos` | httpx -> API -> adaptador Neo4j | OK | operacion_exitosa | 5.7 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: codigo=PAR-0001; fuente_datos=Neo4j; eventos=2; X-Request-ID enviado=igual; X-Process-Time-Ms=4.40 |
| api | GET /api/v1/partidos/PAR-9999/eventos (recurso inexistente) | `http://127.0.0.1:8000/api/v1/partidos/PAR-9999/eventos` | httpx -> API -> adaptador Neo4j | OK | recurso_inexistente | 4.3 ms | status=404 (esperado [404]); 404 RECURSO_NO_ENCONTRADO: la dependencia respondió y el recurso no existe; resumen: error.codigo=RECURSO_NO_ENCONTRADO; X-Request-ID enviado=igual; X-Process-Time-Ms=3.07 |

### Cassandra

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| configuracion | variables requeridas presentes | `127.0.0.1:9042` | lectura de configuración | OK | configuracion_completa | - | destino=127.0.0.1:9042; protocolo=CQL native protocol (TCP); keyspace=fixture2030_comentarios; tabla=comentarios_por_partido; autenticacion=sin credenciales configuradas (el laboratorio usa AllowAllAuthenticator); origen de valores=.env (API) |
| proceso | estado del contenedor (docker inspect) *(complementaria)* | `fixture2030-cassandra` | docker CLI | OK | contenedor_en_ejecucion | - | contenedor=fixture2030-cassandra; estado=running; health=sin healthcheck; iniciado=2026-10-21T21:29:51.42084251Z; puertos (interno->publicado)=9042/tcp->0.0.0.0:9042, 9042/tcp->:::9042 |
| resolucion | resolución de 127.0.0.1 | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | puerto CQL (CQL) | `127.0.0.1:9042` | socket TCP | OK | conexion_exitosa | 0.3 ms | listener aceptó la conexión en 127.0.0.1:9042 (origen 127.0.0.1) en 0.3 ms |
| protocolo | sesión CQL sin keyspace (system.local) | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | handshake_ok | 1501.8 ms | sesión CQL establecida; protocolo nativo v5; Cassandra 5.0.9; cluster=Fixture2030_Cassandra; dc=datacenter1 |
| autenticacion | mecanismo de autenticación | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | N/A | sin_autenticacion_configurada | 0.0 ms | el cluster aceptó la sesión sin credenciales: en este laboratorio no exige autenticación (AllowAllAuthenticator). En producción esta capa debería existir. |
| contexto | keyspace fixture2030_comentarios | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | contexto_ok | 29.4 ms | keyspace 'fixture2030_comentarios' seleccionado; replicación={'class': 'org.apache.cassandra.locator.SimpleStrategy', 'replication_factor': '1'} |
| contexto | tabla comentarios_por_partido y patrón de partición | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | contexto_ok | 16.4 ms | tabla comentarios_por_partido: PRIMARY KEY ((partido_id, bucket_10min), creado_en DESC, comentario_id ASC) |
| autorizacion | SELECT LIMIT 1 sobre comentarios_por_partido | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | autorizado | 15.4 ms | SELECT permitido sobre fixture2030_comentarios.comentarios_por_partido |
| operacion | lectura limitada partición (PAR-0001, 203006132000) | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | lectura_ok | 15.0 ms | partición (partido_id=PAR-0001, bucket_10min=203006132000): 3 filas (LIMIT 3) |
| operacion | prueba negativa controlada: partición vacía *(complementaria)* | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | vacio_valido | 15.2 ms | partición inexistente PAR-9999: 0 filas, sin error (lista vacía ≠ timeout) |
| contexto | prueba negativa controlada: keyspace inexistente *(complementaria)* | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | contexto_inexistente | 14.6 ms | error esperado: InvalidRequest |
| contexto | prueba negativa controlada: tabla inexistente *(complementaria)* | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | tabla_inexistente | 15.3 ms | error esperado: InvalidRequest |
| operacion | prueba negativa controlada: consulta CQL inválida *(complementaria)* | `127.0.0.1:9042/fixture2030_comentarios` | cassandra-driver 3.30.1 | OK | consulta_invalida | 15.6 ms | SyntaxException en 15.5 ms: rechazo inmediato del servidor, no un timeout de conexión |
| api | GET /api/v1/partidos/PAR-0001/comentarios (operación exitosa) | `http://127.0.0.1:8000/api/v1/partidos/PAR-0001/comentarios?bucket_10min=203006132000&limit=3` | httpx -> API -> adaptador Cassandra | OK | operacion_exitosa | 11.7 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: fuente_datos=Cassandra; datos=3; X-Request-ID enviado=igual; X-Process-Time-Ms=10.34 |
| api | GET /api/v1/partidos/PAR-9999/comentarios (respuesta vacía válida) | `http://127.0.0.1:8000/api/v1/partidos/PAR-9999/comentarios?bucket_10min=203006132000&limit=3` | httpx -> API -> adaptador Cassandra | OK | vacio_valido | 14.9 ms | status=200 (esperado [200]); 200 con lista vacía: ausencia válida de datos, no un error; resumen: fuente_datos=Cassandra; datos=0; X-Request-ID enviado=igual; X-Process-Time-Ms=13.40 |
| api | GET /api/v1/partidos/PAR-0001/comentarios (error de validación) | `http://127.0.0.1:8000/api/v1/partidos/PAR-0001/comentarios?bucket_10min=203006132005` | httpx -> API -> adaptador Cassandra | OK | error_validacion | 1.7 ms | status=422 (esperado [422]); 422 DATOS_INVALIDOS: rechazado por la API antes de consultar la dependencia; resumen: error.codigo=DATOS_INVALIDOS; X-Request-ID enviado=igual; X-Process-Time-Ms=0.37 |

### Redis

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| configuracion | variables requeridas presentes | `127.0.0.1:6379` | lectura de configuración | OK | configuracion_completa | - | destino=127.0.0.1:6379; protocolo=RESP (TCP); db=0; claves sesion:*; autenticacion=sin password configurada (requirepass vacío en el laboratorio); origen de valores=.env (API) |
| proceso | estado del contenedor (docker inspect) *(complementaria)* | `fixture2030-redis` | docker CLI | OK | contenedor_en_ejecucion | - | contenedor=fixture2030-redis; estado=running; health=healthy; iniciado=2026-10-21T21:29:51.553480903Z; puertos (interno->publicado)=6379/tcp->0.0.0.0:6379, 6379/tcp->:::6379 |
| resolucion | resolución de 127.0.0.1 | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | puerto RESP (RESP) | `127.0.0.1:6379` | socket TCP | OK | conexion_exitosa | 0.3 ms | listener aceptó la conexión en 127.0.0.1:6379 (origen 127.0.0.1) en 0.3 ms |
| protocolo | PING en RESP crudo | `127.0.0.1:6379/db0` | socket (RESP manual) | OK | handshake_ok | 2.1 ms | RESP: PING -> +PONG sin credenciales |
| autenticacion | AUTH / requirepass | `127.0.0.1:6379/db0` | redis-py 8.1.0 | N/A | sin_autenticacion_configurada | 0.0 ms | el servidor respondió PONG sin AUTH: requirepass vacío en el laboratorio |
| contexto | base lógica db0 | `127.0.0.1:6379/db0` | redis-py 8.1.0 | OK | contexto_ok | 4.3 ms | SELECT 0 implícito; claves en db0=3; redis_version=8.10.2 |
| operacion | EXISTS + TTL sesion:SES-API-0001 | `127.0.0.1:6379/db0` | redis-py 8.1.0 | OK | clave_vigente | 0.6 ms | sesion:SES-API-0001: EXISTS=1, TTL=1795 s |
| operacion | prueba negativa controlada: expiración de clave diag:hito11:* (TTL 2 s) *(complementaria)* | `127.0.0.1:6379/db0` | redis-py 8.1.0 | OK | clave_expirada | 2503.3 ms | diag:hito11:1dbe2004 creada con EX 2 (TTL inicial 2); a los 2.5 s EXISTS=0, TTL=-2. Clave expirada y clave ausente se ven igual en Redis; ambas difieren de Redis no disponible (ConnectionError en la capa TCP/protocolo). |
| api | GET /api/v1/sesiones/SES-API-0001 (operación exitosa o clave ausente (200 si la sesión fue preparada; 404 si no existe o expiró)) | `http://127.0.0.1:8000/api/v1/sesiones/SES-API-0001` | httpx -> API -> adaptador Redis | OK | operacion_exitosa | 2.5 ms | status=200 (esperado [200, 404]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: estado=activa; fuente_datos=Redis; X-Request-ID enviado=igual; X-Process-Time-Ms=1.40 |
| api | GET /api/v1/sesiones/SES-DIAG-INEXISTENTE (clave ausente) | `http://127.0.0.1:8000/api/v1/sesiones/SES-DIAG-INEXISTENTE` | httpx -> API -> adaptador Redis | OK | recurso_inexistente | 2.3 ms | status=404 (esperado [404]); 404 SESION_NO_ENCONTRADA_O_EXPIRADA: la dependencia respondió y el recurso no existe; resumen: error.codigo=SESION_NO_ENCONTRADA_O_EXPIRADA; X-Request-ID enviado=igual; X-Process-Time-Ms=1.13 |

### InfluxDB

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| configuracion | variables requeridas presentes | `127.0.0.1:8181` | lectura de configuración | OK | configuracion_completa | - | destino=127.0.0.1:8181; protocolo=HTTP API v3 (/health, /api/v3/query_sql); databases=fixture2030_detalle, fixture2030_historico; autenticacion=token Bearer **** (valor oculto); origen de valores=.env (API) |
| proceso | estado del contenedor (docker inspect) *(complementaria)* | `fixture2030-influxdb` | docker CLI | OK | contenedor_en_ejecucion | - | contenedor=fixture2030-influxdb; estado=running; health=sin healthcheck; iniciado=2026-10-21T21:29:51.544292257Z; puertos (interno->publicado)=8181/tcp->127.0.0.1:8181 |
| resolucion | resolución de 127.0.0.1 | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | puerto HTTP API v3 (HTTP) | `127.0.0.1:8181` | socket TCP | OK | conexion_exitosa | 0.3 ms | listener aceptó la conexión en 127.0.0.1:8181 (origen 127.0.0.1) en 0.3 ms |
| protocolo | GET /health (sin token) | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | health_requiere_token | 21.1 ms | GET /health sin token -> 401: el servicio HTTP responde y exige token |
| autenticacion | GET /health con token Bearer | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | autenticado | 1.2 ms | GET /health con token -> 200: token aceptado (valor oculto) |
| autenticacion | prueba negativa controlada: token inválido *(complementaria)* | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | auth_fallida | 1.1 ms | token inválido -> 401: el servidor diferencia token válido de inválido |
| contexto | databases configuradas | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | contexto_ok | 1.1 ms | databases presentes: fixture2030_detalle, fixture2030_historico |
| autorizacion | SELECT 1 sobre fixture2030_detalle | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | ok | 2.7 ms | query_sql permitido sobre 'fixture2030_detalle' |
| operacion | SQL acotado estadisticas_equipo (1 minuto) | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | lectura_ok | 4.5 ms | estadisticas_equipo: partido_id=PAR-0001, rango [2030-06-13T20:00:00Z, 2030-06-13T20:01:00Z), agregación COUNT/MIN/MAX -> 12 puntos (primero=2030-06-13T20:00:00, último=2030-06-13T20:00:50) |
| operacion | SQL acotado resumen_equipo_minuto (resúmenes 15 min) *(complementaria)* | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | lectura_ok | 4.7 ms | fixture2030_historico.resumen_equipo_minuto: 6 resúmenes en 31 minutos |
| operacion | prueba negativa controlada: ventana sin puntos *(complementaria)* | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | vacio_valido | 3.4 ms | ventana 2031-01-01 sin datos: 0 puntos y HTTP 200 (ausencia de puntos ≠ error) |
| contexto | prueba negativa controlada: database inexistente *(complementaria)* | `http://127.0.0.1:8181 db=fixture2030_detalle` | httpx 0.28.1 (API HTTP v3) | OK | contexto_inexistente | 1.2 ms | HTTP 404: {"error":"query error: database not found: fixture2030_diag_inexistente"} |
| api | GET /api/v1/partidos/PAR-0001/estadisticas (operación exitosa) | `http://127.0.0.1:8000/api/v1/partidos/PAR-0001/estadisticas?desde=2030-06-13T20:00:00Z&hasta=2030-06-13T20:01:00Z&limit=10` | httpx -> API -> adaptador InfluxDB | OK | operacion_exitosa | 7.9 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: fuente_datos=InfluxDB; datos=10; X-Request-ID enviado=igual; X-Process-Time-Ms=6.71 |
| api | GET /api/v1/partidos/PAR-0001/estadisticas (respuesta vacía válida) | `http://127.0.0.1:8000/api/v1/partidos/PAR-0001/estadisticas?desde=2031-01-01T00:00:00Z&hasta=2031-01-01T00:01:00Z` | httpx -> API -> adaptador InfluxDB | OK | vacio_valido | 6.2 ms | status=200 (esperado [200]); 200 con lista vacía: ausencia válida de datos, no un error; resumen: fuente_datos=InfluxDB; datos=0; X-Request-ID enviado=igual; X-Process-Time-Ms=4.89 |
| api | GET /api/v1/partidos/PAR-0001/estadisticas (error de validación) | `http://127.0.0.1:8000/api/v1/partidos/PAR-0001/estadisticas?desde=2030-06-13T20:01:00Z&hasta=2030-06-13T20:00:00Z` | httpx -> API -> adaptador InfluxDB | OK | error_validacion | 1.9 ms | status=422 (esperado [422]); 422 VENTANA_TEMPORAL_INVALIDA: rechazado por la API antes de consultar la dependencia; resumen: error.codigo=VENTANA_TEMPORAL_INVALIDA; X-Request-ID enviado=igual; X-Process-Time-Ms=0.72 |

### InterSystems IRIS

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| configuracion | variables requeridas presentes | `127.0.0.1:1972 (Superserver) / 127.0.0.1:52773 (portal HTTP)` | lectura de configuración | OK | configuracion_completa | - | destino=127.0.0.1:1972 (Superserver) / 127.0.0.1:52773 (portal HTTP); protocolo=Superserver (DB-API) y HTTP (portal); namespace=USER; autenticacion=usuario presente (valor oculto) y password presente (valor oculto); origen de valores=.env (API) |
| proceso | estado del contenedor (docker inspect) *(complementaria)* | `fixture2030-iris` | docker CLI | OK | contenedor_en_ejecucion | - | contenedor=fixture2030-iris; estado=running; health=healthy; iniciado=2026-10-21T21:29:51.555106564Z; puertos (interno->publicado)=1972/tcp->127.0.0.1:1972, 52773/tcp->127.0.0.1:52773 |
| resolucion | resolución de 127.0.0.1 | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | Superserver (usado por la API) (Superserver) | `127.0.0.1:1972` | socket TCP | OK | conexion_exitosa | 0.4 ms | listener aceptó la conexión en 127.0.0.1:1972 (origen 127.0.0.1) en 0.4 ms |
| resolucion | resolución de 127.0.0.1 *(complementaria)* | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | portal HTTP (no usado por la API) (HTTP) *(complementaria)* | `127.0.0.1:52773` | socket TCP | OK | conexion_exitosa | 0.5 ms | listener aceptó la conexión en 127.0.0.1:52773 (origen 127.0.0.1) en 0.4 ms |
| protocolo | portal HTTP (Management Portal) *(complementaria)* | `127.0.0.1:52773` | httpx | OK | portal_http_ok | 278.1 ms | Management Portal respondió HTTP 200 (200/302/401 indican portal activo; no usa la identidad de la API) |
| protocolo | handshake Superserver (DB-API connect) | `127.0.0.1:1972/USER` | intersystems-irispython 5.4.1 (DB-API) | OK | protocolo_ok | 0.0 ms | handshake con el Superserver completado; inferido del mismo connect() (23.2 ms) |
| autenticacion | usuario/password en connect | `127.0.0.1:1972/USER` | intersystems-irispython 5.4.1 (DB-API) | OK | autenticacion_ok | 0.0 ms | credenciales aceptadas (valores ocultos); inferido del mismo connect() (23.2 ms) |
| contexto | namespace USER | `127.0.0.1:1972/USER` | intersystems-irispython 5.4.1 (DB-API) | OK | contexto_ok | 0.0 ms | namespace 'USER' seleccionado; inferido del mismo connect() (23.2 ms) |
| autorizacion | lectura de metadatos (INFORMATION_SCHEMA) | `127.0.0.1:1972/USER` | intersystems-irispython 5.4.1 (DB-API) | OK | autorizado | 1.5 ms | metadato legible: 5 tablas/clases proyectadas en el esquema Fixture |
| operacion | lectura Fixture.Partido PAR-0001 | `127.0.0.1:1972/USER` | intersystems-irispython 5.4.1 (DB-API) | OK | lectura_ok | 2.3 ms | Fixture.Partido PAR-0001: estado=Finalizado; total partidos=1 |
| operacion | prueba negativa controlada: objeto inexistente PAR-9999 *(complementaria)* | `127.0.0.1:1972/USER` | intersystems-irispython 5.4.1 (DB-API) | OK | recurso_inexistente | 1.1 ms | PAR-9999: 0 filas sin error (objeto inexistente ≠ Superserver inaccesible) |
| contexto | prueba negativa controlada: namespace incorrecto *(complementaria)* | `127.0.0.1:1972/USER` | intersystems-irispython 5.4.1 (DB-API) | OK | contexto_inexistente | 2019.8 ms | IRIS respondió 'Access Denied' al pedir un namespace inexistente: por seguridad usa el mismo mensaje que para una credencial inválida. Como las mismas credenciales funcionaron en 'USER', el rechazo se atribuye al namespace. Distinto de Superserver inaccesible, que no llega a responder. |
| api | GET /api/v1/partidos/PAR-0001/detalle (operación exitosa) | `http://127.0.0.1:8000/api/v1/partidos/PAR-0001/detalle` | httpx -> API -> adaptador InterSystems IRIS | OK | operacion_exitosa | 25.0 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: estado=Finalizado; codigo=PAR-0001; fuente_datos=InterSystems IRIS; eventos=1; X-Request-ID enviado=igual; X-Process-Time-Ms=23.72 |
| api | GET /api/v1/partidos/PAR-9999/detalle (recurso inexistente) | `http://127.0.0.1:8000/api/v1/partidos/PAR-9999/detalle` | httpx -> API -> adaptador InterSystems IRIS | OK | recurso_inexistente | 104.4 ms | status=404 (esperado [404]); 404 PARTIDO_IRIS_NO_ENCONTRADO: la dependencia respondió y el recurso no existe; resumen: error.codigo=PARTIDO_IRIS_NO_ENCONTRADO; X-Request-ID enviado=igual; X-Process-Time-Ms=102.84 |

### API Fixture 2030

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| resolucion | resolución de 127.0.0.1 | `127.0.0.1` | socket.getaddrinfo | OK | host_resuelto | 0.0 ms | 127.0.0.1 -> 127.0.0.1 |
| tcp | puerto de la API (uvicorn) (HTTP) | `127.0.0.1:8000` | socket TCP | OK | conexion_exitosa | 0.4 ms | listener aceptó la conexión en 127.0.0.1:8000 (origen 127.0.0.1) en 0.4 ms |
| api | GET /health/live (liveness) | `http://127.0.0.1:8000/health/live` | httpx -> API -> adaptador API Fixture 2030 | OK | operacion_exitosa | 29.4 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: estado=ok; X-Request-ID enviado=igual; X-Process-Time-Ms=1.06 |
| api | GET /health/ready (readiness) | `http://127.0.0.1:8000/health/ready` | httpx -> API -> adaptador API Fixture 2030 | OK | operacion_exitosa | 26.0 ms | status=200 (esperado [200, 503]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: estado=ready; deps=MongoDB:up,Neo4j:up,Cassandra:up,Redis:up,InfluxDB:up,InterSystems IRIS:up; X-Request-ID enviado=igual; X-Process-Time-Ms=24.72 |
| api | GET /health/dependencias (diagnóstico por dependencia) | `http://127.0.0.1:8000/health/dependencias?refrescar=true` | httpx -> API -> adaptador API Fixture 2030 | OK | operacion_exitosa | 2.0 ms | status=200 (esperado [200]); 200: la cadena cliente-API-adaptador-producto funcionó para este caso; resumen: estado_general=ready; deps=MongoDB:up,Neo4j:up,Cassandra:up,Redis:up,InfluxDB:up,InterSystems IRIS:up; X-Request-ID enviado=igual; X-Process-Time-Ms=0.69 |

### Repositorio

| Capa | Prueba | Objetivo | Cliente | Estado | Clasificación | Duración | Detalle |
|---|---|---|---|---|---|---|---|
| configuracion | NEO4J_PASSWORD distinta de identificadores públicos *(complementaria)* | `NEO4J_PASSWORD` | lectura de configuración | ADV | credencial_debil | - | el valor de NEO4J_PASSWORD coincide con un nombre público del proyecto (database, contenedor, keyspace). Es aceptable solo en el laboratorio local; en otro entorno debe cambiarse. Ese valor no se redacta en la evidencia porque taparía los nombres de los recursos. |
| configuracion | .env fuera de Git *(complementaria)* | `.env` | git check-ignore / git ls-files | OK | secretos_no_versionados | - | ignorado por .gitignore y no versionado |
| configuracion | hito11-conectividad/config/conectividad.env fuera de Git *(complementaria)* | `hito11-conectividad/config/conectividad.env` | git check-ignore / git ls-files | OK | secretos_no_versionados | - | ignorado por .gitignore y no versionado |

## Fallas y observaciones con diagnóstico (RNF10)

| Producto | Capa | Prueba | Resultado | Hipótesis | Siguiente paso |
|---|---|---|---|---|---|
| Repositorio | configuracion | NEO4J_PASSWORD distinta de identificadores públicos | ADV: credencial_debil | La credencial de laboratorio se eligió igual al nombre del proyecto. | Usar una credencial propia fuera del laboratorio y rotarla. |

## Evidencia asociada

- `docs/evidencia/resultados_config.txt` / `.json`
- `docs/evidencia/resultados_tcp.txt` / `.json`
- `docs/evidencia/resultados_clientes.txt` / `.json`
- `docs/evidencia/resultados_api.txt` / `.json` (incluye request ID y línea de log por solicitud)

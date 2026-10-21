# Mapa de dependencias de la API integrada

Este mapa describe **cómo se conecta la API del Hito 10** con cada producto. Se construyó a partir del código (`app/config/settings.py`, `app/adapters/*.py`), del `.env.example` y de los `docker-compose.yml` de cada hito.

Los valores de host y puerto son los del entorno de laboratorio (la notebook del equipo). Las credenciales no se publican: se indica solo el mecanismo y la variable que lo contiene.

> **Estado observado:** no se completa en este documento. Se registra en [`matriz_de_conectividad.md`](matriz_de_conectividad.md), que genera el script a partir de pruebas reales. Hasta que se ejecuta una prueba válida, el estado de cada producto es **no probado** (sección 5.1 de la consigna).

## Resumen

| Producto | Módulo del Fixture | Proceso que conecta | Host desde ese proceso | Puerto / protocolo | Contexto | Autenticación (sin valor) | Cliente / driver | Operación mínima | Endpoint de API | Estado esperado |
|---|---|---|---|---|---|---|---|---|---|---|
| MongoDB | Equipos y jugadores (Hito 4) | API (uvicorn en la notebook) | `127.0.0.1` | 27017 / MongoDB Wire Protocol | database `fixture2030`, authSource `admin`, colecciones `equipos` y `jugadores` | SCRAM: `MONGODB_USERNAME` + `MONGODB_PASSWORD` | `pymongo 4.18.3` | `find_one({_id:"EQ-01"})` con proyección y `maxTimeMS` | `GET /api/v1/equipos/{codigo}`, `GET /api/v1/jugadores` | disponible |
| Neo4j | Partidos, equipos, sedes y eventos (Hito 5) | API | `127.0.0.1` | 7687 / Bolt (la API) · 7474 / HTTP (Browser, solo personas) | database `neo4j` | basic auth: `NEO4J_USERNAME` + `NEO4J_PASSWORD` | `neo4j 6.4.0` | Cypher parametrizado `MATCH (p:Partido {codigo:$codigo})` | `GET /api/v1/partidos/{codigo}/eventos` | disponible |
| Cassandra | Comentarios por partido (Hito 6) | API | `127.0.0.1` | 9042 / CQL native protocol | keyspace `fixture2030_comentarios`, tabla `comentarios_por_partido`, partición `(partido_id, bucket_10min)` | sin autenticación en el laboratorio (`AllowAllAuthenticator`) | `cassandra-driver 3.30.1` | `SELECT ... WHERE partido_id=? AND bucket_10min=? LIMIT 3` | `GET /api/v1/partidos/{codigo}/comentarios` | disponible |
| Redis | Sesiones con expiración (Hito 7) | API | `127.0.0.1` | 6379 / RESP | db lógica `0`, claves `sesion:{id}` | sin `requirepass` en el laboratorio | `redis 8.1.0` (redis-py) | `HGETALL` + `TTL` de `sesion:{id}` | `GET /api/v1/sesiones/{id}` (el `DELETE` no se usa para diagnosticar) | disponible |
| InfluxDB 3 | Estadísticas temporales (Hito 8) | API | `127.0.0.1` | 8181 / HTTP API v3 | databases `fixture2030_detalle` y `fixture2030_historico` | token Bearer: `INFLUXDB_TOKEN` | `httpx 0.28.1` contra `/api/v3/query_sql` | `COUNT/MIN/MAX` en una ventana de 1 minuto | `GET /api/v1/partidos/{codigo}/estadisticas` | disponible |
| InterSystems IRIS | Objetos persistentes de partido (Hito 9) | API | `127.0.0.1` | 1972 / Superserver (la API) · 52773 / HTTP (Management Portal, solo personas) | namespace `USER`, clases `Fixture.Partido`, `Fixture.Arbitro`, `Fixture.EventoPartido` | usuario/password: `IRIS_USERNAME` + `IRIS_PASSWORD` | `intersystems_irispython 5.4.1` (DB-API) | `SELECT ... FROM Fixture.Partido WHERE Codigo = ?` | `GET /api/v1/partidos/{codigo}/detalle` | disponible |

## Detalle por producto

### MongoDB

- **Adaptador:** `app/adapters/mongodb.py`. Un único `MongoClient` creado al iniciar la API (no abre la conexión hasta la primera operación).
- **Timeouts:** `serverSelectionTimeoutMS`, `connectTimeoutMS`, `socketTimeoutMS` y `maxTimeMS` = `DEPENDENCY_TIMEOUT_SECONDS`.
- **Particularidad para el diagnóstico:** MongoDB **no falla** si la database o la colección no existen. Devuelve vacío y la crearía al escribir. Por eso el diagnóstico y `/health/dependencias` comprueban explícitamente que exista la colección `equipos`.

### Neo4j

- **Adaptador:** `app/adapters/neo4j.py`. Un `Driver` con pool de conexiones Bolt.
- **Dos puertos distintos:** 7474 es el Browser HTTP que usa una persona. **La API no lo usa.** 7687 es Bolt, el que usa la API. Que el Browser cargue no prueba que Bolt funcione.
- **Diferencia clave:** un partido inexistente devuelve un resultado vacío (404 en la API). Una database inexistente devuelve `Neo.ClientError.Database.DatabaseNotFound`. Un Neo4j caído devuelve `ServiceUnavailable`.

### Cassandra

- **Adaptador:** `app/adapters/cassandra.py`. Desde el Hito 11 abre la sesión **en la primera solicitud** y no al iniciar la API (ver [`diagnostico_de_fallas.md`](diagnostico_de_fallas.md), hallazgo H1).
- **Patrón de acceso:** la consulta exige la clave de partición completa `(partido_id, bucket_10min)`. Una partición sin filas es una respuesta vacía válida, no un error.

### Redis

- **Adaptador:** `app/adapters/redis.py`. Configurado sin reintentos (`Retry(NoBackoff(), 0)`) y con timeouts de conexión y lectura.
- **Diferencia clave:** clave ausente y clave expirada se ven igual en Redis (`EXISTS 0`, `TTL -2`). La API devuelve 404 en ambos casos. Redis no disponible produce `ConnectionError` y la API devuelve 503.

### InfluxDB 3

- **Adaptador:** `app/adapters/influxdb.py`. Cliente HTTP con el token en el header `Authorization` (nunca en la URL).
- **Diferencia clave desde el Hito 11:** token inválido (401), falta de permisos (403) y database inexistente (404) se distinguen de servicio caído. Hasta el Hito 10, todo status ≥ 400 se informaba igual.

### InterSystems IRIS

- **Adaptador:** `app/adapters/iris.py`. Abre y cierra una conexión DB-API por solicitud.
- **Dos puertos distintos:** 52773 es el Management Portal (HTTP) y 1972 es el Superserver que usa la API.
- **Desde el Hito 11** el `connect()` usa `timeout` para que un Superserver inalcanzable no bloquee la solicitud.

## Endpoints de diagnóstico agregados en el Hito 11

| Endpoint | Consulta dependencias | Uso |
|---|---|---|
| `GET /health` · `GET /health/live` | No | Liveness: el proceso de la API está activo |
| `GET /health/ready` | Usa la caché del diagnóstico (15 s) | Readiness: `ready`, `degraded` o `not_ready` |
| `GET /health/dependencias` | Sí, con caché y timeout por dependencia | Estado individual: `up`, `down`, `unknown`, `not_configured` |

El diseño se detalla en [`health_readiness.md`](health_readiness.md).

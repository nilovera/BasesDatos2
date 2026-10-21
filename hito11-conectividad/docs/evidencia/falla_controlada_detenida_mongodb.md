# Falla controlada: MongoDB detenido temporalmente

> Generado por `scripts/falla_controlada.py` el 2026-10-21T18:58:48-03:00 · commit `d2bed7c (con cambios sin commit)` · entorno: notebook Windows de Valentino - entorno-local consolidado.

## 1. Condición inicial

- Contenedor `fixture2030-mongodb`: **running**.
- Montajes/volúmenes: `volume:fixture2030_mongodb_data->/data/db`, `bind:/run/desktop/mnt/host/c/Users/Valentino/Documents/BasesDatos2-Conectividad/entorno-local/datos/mongodb->/scripts`, `volume:e97a7c473a99385e27884c1045de4fb682fd9bd558d9371582620d51b6932b40->/data/configdb`
- Datos (lectura): `{"equipos": 64, "jugadores": 1024}`
- Diagnóstico nativo: **disponible** — todas las capas requeridas probadas terminaron OK
- Health de la API: {'estado_general': 'ready', 'dependencias': {'MongoDB': 'up (ok)', 'Neo4j': 'up (ok)', 'Cassandra': 'up (ok)', 'Redis': 'up (ok)', 'InfluxDB': 'up (ok)', 'InterSystems IRIS': 'up (ok)'}}
- **Ruta del producto:** `GET /api/v1/equipos/EQ-01` → HTTP **200** en 318.53 ms (operacion_exitosa). 200: la cadena cliente-API-adaptador-producto funcionó para este caso
  - request_id: `b831b12e-52a1-47d5-b1d5-07557dca6c2a` · resumen: codigo=EQ-01; fuente_datos=MongoDB
  - log: `2026-10-21 18:58:50,134 | INFO | fixture2030.request | {"evento": "http_request", "request_id": "b831b12e-52a1-47d5-b1d5-07557dca6c2a", "metodo": "GET", "ruta": "/api/v1/equipos/EQ-01", "dependencia": "MongoDB", "resultado": 200, "duracion_ms": 2.0}`
- **Ruta de control (Redis):** `GET /api/v1/sesiones/SES-API-0001` → HTTP **200** en 269.69 ms (operacion_exitosa). 200: la cadena cliente-API-adaptador-producto funcionó para este caso
  - request_id: `19cd865f-c8c8-4a26-bfa1-96016cab82ee` · resumen: estado=activa; fuente_datos=Redis
  - log: `2026-10-21 18:58:50,714 | INFO | fixture2030.request | {"evento": "http_request", "request_id": "19cd865f-c8c8-4a26-bfa1-96016cab82ee", "metodo": "GET", "ruta": "/api/v1/sesiones/SES-API-0001", "dependencia": "Redis", "resultado": 200, "duracion_ms": 1.92}`

## 2. Cambio aplicado

- Comando: `docker stop fixture2030-mongodb` (rc=0, 0.5 s, 2026-10-21T18:58:51-03:00).
- No se usó `docker compose down -v`, `docker rm` ni ningún borrado de datos o volúmenes.

## 3. Prueba ejecutada durante la falla

- Contenedor: **exited**.
- Diagnóstico nativo: **no disponible** — capa que falla: `tcp` (connection_refused).
- Health de la API: {'estado_general': 'degraded', 'dependencias': {'MongoDB': 'down (no_disponible)', 'Neo4j': 'up (ok)', 'Cassandra': 'up (ok)', 'Redis': 'up (ok)', 'InfluxDB': 'up (ok)', 'InterSystems IRIS': 'up (ok)'}}

## 4. Respuesta de la API, mensaje de log y tiempo de espera

- **Ruta del producto caído:** `GET /api/v1/equipos/EQ-01` → HTTP **503** en 5445.0 ms (dependencia_no_disponible). 503 DEPENDENCIA_NO_DISPONIBLE: API viva, dependencia no disponible
  - request_id: `d6702032-71a5-42b5-8db1-5e57f2432cfb` · resumen: error.codigo=DEPENDENCIA_NO_DISPONIBLE
  - log: `2026-10-21 18:59:10,189 | WARNING | fixture2030.error | request_id=d6702032-71a5-42b5-8db1-5e57f2432cfb dependencia=MongoDB codigo=DEPENDENCIA_NO_DISPONIBLE status=503`
  - log: `2026-10-21 18:59:10,190 | INFO | fixture2030.request | {"evento": "http_request", "request_id": "d6702032-71a5-42b5-8db1-5e57f2432cfb", "metodo": "GET", "ruta": "/api/v1/equipos/EQ-01", "dependencia": "MongoDB", "resultado": 503, "duracion_ms": 5179.85}`
- **Ruta de control (Redis):** `GET /api/v1/sesiones/SES-API-0001` → HTTP **200** en 266.93 ms (operacion_exitosa). 200: la cadena cliente-API-adaptador-producto funcionó para este caso
  - request_id: `e468ffec-4028-4e18-94ed-baa071c14944` · resumen: estado=activa; fuente_datos=Redis
  - log: `2026-10-21 18:59:10,767 | INFO | fixture2030.request | {"evento": "http_request", "request_id": "e468ffec-4028-4e18-94ed-baa071c14944", "metodo": "GET", "ruta": "/api/v1/sesiones/SES-API-0001", "dependencia": "Redis", "resultado": 200, "duracion_ms": 1.31}`

La API respondió en 5445.0 ms: el driver esperó hasta agotar su límite (`DEPENDENCY_TIMEOUT_SECONDS` / selección de servidor) y luego devolvió un error identificable. La request no quedó bloqueada indefinidamente ni se reintentó en bucle (RNF5, RNF12).

## 5. Recuperación del servicio

- Comando: `docker start fixture2030-mongodb` (rc=0).
- Recuperado: **sí** — 1.5 s hasta que el diagnóstico nativo volvió a terminar OK (1 intentos).

## 6. Resultado después de recuperar la dependencia

- Diagnóstico nativo: **disponible** — todas las capas requeridas probadas terminaron OK
- Health de la API: {'estado_general': 'ready', 'dependencias': {'MongoDB': 'up (ok)', 'Neo4j': 'up (ok)', 'Cassandra': 'up (ok)', 'Redis': 'up (ok)', 'InfluxDB': 'up (ok)', 'InterSystems IRIS': 'up (ok)'}}
- **Ruta del producto:** `GET /api/v1/equipos/EQ-01` → HTTP **200** en 683.44 ms (operacion_exitosa). 200: la cadena cliente-API-adaptador-producto funcionó para este caso
  - request_id: `b07c49cc-1b0c-45d1-815f-dd0331764e4e` · resumen: codigo=EQ-01; fuente_datos=MongoDB
  - log: `2026-10-21 18:59:24,809 | INFO | fixture2030.request | {"evento": "http_request", "request_id": "b07c49cc-1b0c-45d1-815f-dd0331764e4e", "metodo": "GET", "ruta": "/api/v1/equipos/EQ-01", "dependencia": "MongoDB", "resultado": 200, "duracion_ms": 406.4}`

## 7. Datos y volúmenes conservados

- Datos antes: `{"equipos": 64, "jugadores": 1024}` · después: `{"equipos": 64, "jugadores": 1024}` → **conservados**.
- Volúmenes antes/después iguales: **sí**.

## Cambio de estado (RF20)

| Momento | Diagnóstico nativo | Ruta de la API | Health |
|---|---|---|---|
| Inicial | disponible | HTTP 200 | ready |
| Durante | no disponible | HTTP 503 | degraded |
| Después | disponible | HTTP 200 | ready |

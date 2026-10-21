# Diagnóstico de fallas

Cada falla se documenta con **hipótesis, prueba realizada, resultado y siguiente paso** (RNF10). El script completa estos campos de forma automática en la matriz y en las evidencias. Este documento explica los criterios, los hallazgos de la revisión de la API y el escenario de falla controlada.

## 1. Interpretación de la prueba TCP (sección 5.3)

| Resultado | Clasificación en la evidencia | Interpretación | Siguiente paso |
|---|---|---|---|
| Conexión exitosa | `conexion_exitosa` | Existe un listener en el host y puerto probados | Continuar con la capa de protocolo. **No** concluir que el producto está disponible |
| Connection refused | `connection_refused` | El host responde, pero no hay listener: contenedor detenido, puerto no publicado o proceso iniciando | `docker ps` (columna PORTS), `docker logs <contenedor>` |
| Timeout | `timeout` | No hubo respuesta dentro de `DIAG_TIMEOUT_SECONDS`: firewall, ruta, host equivocado o saturación | Verificar IP y firewall; repetir con un timeout mayor solo para diagnosticar |
| Host no resuelto | `host_no_resuelto` | El nombre no existe desde el entorno de ejecución (típico: usar `mongodb` desde la notebook) | Desde la notebook usar `127.0.0.1` + puerto publicado |
| Puerto incorrecto | `protocolo_inesperado` (capa protocolo) | El TCP conecta, pero responde otro servicio (ej. 7474 HTTP en lugar de 7687 Bolt) | Comparar con el mapeo de `docker ps` |

Una conexión TCP exitosa **nunca** se presenta como prueba de autenticación, autorización, contexto o consulta válida.

## 2. Estados utilizados

### Por prueba

| Estado | Significado |
|---|---|
| `OK` | Esa prueba concreta funcionó, en ese momento y desde ese origen (RNF17) |
| `FALLA` | Se intentó y falló |
| `ADVERTENCIA` | Funcionó con una observación (ej. conexión correcta pero el dato de demostración no existe) |
| `BLOQUEADA` | No se ejecutó porque falló una capa anterior |
| `SKIP` | No se ejecutó por **falta de herramienta o configuración**. **No significa producto caído** |
| `NO_APLICA` | La capa no existe en este entorno (ej. Cassandra y Redis sin autenticación en el laboratorio) |

### Por producto (RNF9)

| Estado | Regla |
|---|---|
| **disponible** | Todas las capas requeridas ejecutadas terminaron OK, incluida la lectura mínima |
| **degradado** | La lectura mínima funcionó, pero hubo una advertencia o falló una prueba complementaria (ej. portal HTTP caído, dato de demostración ausente) |
| **no disponible** | Una capa requerida terminó en FALLA |
| **no probado** | Todas las pruebas fueron SKIP / BLOQUEADA |
| **desconocido** | Lo ejecutado no alcanza para concluir (ej. solo se corrió el modo `tcp`) |
| **no configurado** | Faltan variables del producto en el entorno |

## 3. Diferencias que el diagnóstico conserva

| Situación | Cómo se ve en el diagnóstico | Cómo responde la API |
|---|---|---|
| Recurso inexistente (EQ-99, PAR-9999) | `recurso_inexistente`, estado OK | `404` |
| Respuesta vacía válida (partición o ventana sin datos) | `vacio_valido` | `200` con `datos: []` |
| Error de validación | — (no llega al producto) | `422 DATOS_INVALIDOS` / `VENTANA_TEMPORAL_INVALIDA` |
| Dependencia caída o puerto cerrado | `connection_refused` en TCP | `503 DEPENDENCIA_NO_DISPONIBLE` |
| Dependencia lenta | `timeout` | `504 TIEMPO_DE_ESPERA_AGOTADO` |
| Credencial rechazada | `auth_fallida` | `503 DEPENDENCIA_MAL_CONFIGURADA` con `detalles.capa = "autenticacion"` |
| Sin permisos | `sin_permiso` | `503 DEPENDENCIA_MAL_CONFIGURADA`, `capa = "autorizacion"` |
| Database / keyspace / namespace inexistente | `contexto_inexistente` | `503 DEPENDENCIA_MAL_CONFIGURADA`, `capa = "contexto"` |
| Error no controlado | `error_interno` | `500 ERROR_INTERNO` (la traza queda solo en el log) |
| Clave Redis ausente o expirada | `clave_ausente` / `clave_expirada` | `404 SESION_NO_ENCONTRADA_O_EXPIRADA` |

La API nunca oculta una falla de dependencia con un `200`. Cada error lleva `request_id` y el log registra `dependencia`, `codigo` y `status`.

## 4. Hallazgos de la revisión de la API del Hito 10

Antes de ejecutar las pruebas se revisaron los adaptadores. Se encontraron cuatro comportamientos que afectaban la conectividad y se corrigieron en el Hito 11.

### H1 — Una Cassandra caída impedía iniciar toda la API

- **Hipótesis:** el adaptador abría la sesión (`Cluster.connect`) en su constructor, dentro del `lifespan` de FastAPI. Si Cassandra no respondía, la excepción abortaba el arranque y los otros cinco motores quedaban inaccesibles.
- **Prueba:** se inició la API del Hito 10 con Cassandra detenida.
- **Resultado:** `cassandra.cluster.NoHostAvailable` → `Application startup failed. Exiting.`
- **Corrección:** `app/adapters/cassandra.py` abre la sesión en la primera solicitud que la necesita (con lock y timeouts). Si falla, responde 503/504 y la próxima solicitud vuelve a intentar una sola vez.
- **Verificación:** con el cambio, la API inicia con todos los motores detenidos. `/health/live` responde 200, `/health/ready` responde 503 `not_ready` y la ruta de comentarios responde 503 `DEPENDENCIA_NO_DISPONIBLE` en milisegundos.
- **Siguiente paso:** ninguno. Se recomienda mantener el patrón para nuevos adaptadores (RNF12, RNF13).

### H2 — InfluxDB informaba igual un token inválido que un servicio caído

- **Hipótesis:** el adaptador traducía cualquier status ≥ 400 a `DEPENDENCIA_NO_DISPONIBLE`.
- **Prueba:** revisión de `app/adapters/influxdb.py` (Hito 10).
- **Resultado:** 401, 403 y 404 se mostraban como 503 sin distinción.
- **Corrección:** `_raise_for_status()` distingue autenticación (401), autorización (403) y contexto (404 / "database not found"). Todos se informan como `503 DEPENDENCIA_MAL_CONFIGURADA` con la capa en `detalles`, sin incluir el token ni el mensaje del servidor.

### H3 — La conexión a IRIS no tenía límite de espera

- **Hipótesis:** `iris.dbapi.connect()` se llamaba sin `timeout`. Ante un host inalcanzable, la solicitud quedaba esperando el timeout del sistema operativo.
- **Prueba:** `connect('10.255.255.1', 1972, ..., timeout=2)` contra una IP sin ruta.
- **Resultado:** con `timeout=2` el driver devuelve `OperationalError` a los 2,0 s.
- **Corrección:** el adaptador pasa `timeout=DEPENDENCY_TIMEOUT_SECONDS` y clasifica el error por capa (`translate_iris_error`).

### H4 — MongoDB no detecta solo una database mal configurada

- **Hipótesis:** MongoDB crea las databases de forma perezosa. Un nombre mal escrito en `MONGODB_DATABASE` devuelve resultados vacíos y no un error.
- **Prueba:** prueba negativa del modo `nativos` (`list_collection_names()` sobre una database inexistente).
- **Resultado esperado:** 0 colecciones, sin excepción.
- **Corrección:** `MongoAdapter.ping()` (usado por `/health/dependencias`) verifica la colección `equipos` y responde `rechazo_contexto` si no existe. Las rutas de negocio no se modificaron: consultar un equipo de una database vacía devuelve 404, que es correcto para esa ruta.

## 5. Falla controlada y recuperación (sección 5.7)

El escenario principal es **dependencia detenida**:

```powershell
.\hito11-conectividad\scripts\falla_controlada.ps1 -Producto mongodb
```

El script:

1. Registra la **condición inicial**: estado y montajes del contenedor, cantidad de datos (`count_documents`), diagnóstico nativo, ruta de la API, ruta de un producto de control y `/health/dependencias`.
2. **Aplica el cambio:** `docker stop fixture2030-mongodb`. Nunca usa `docker compose down -v` ni `docker rm`.
3. **Prueba durante la falla:** diagnóstico (la capa TCP debe fallar con `connection_refused`), la ruta del producto (debe dar 503), la ruta de control (debe seguir en 200) y health (`degraded`).
4. Registra la **respuesta de la API**, la **línea de log** buscada por `request_id` y el **tiempo de espera**.
5. **Recupera** el servicio con `docker start` y espera hasta que el diagnóstico nativo vuelva a dar OK (registra los segundos).
6. **Repite** las pruebas (RF20) y compara datos y volúmenes antes y después.

La evidencia queda en `docs/evidencia/falla_controlada_detenida_<producto>.md` y `.json`, con una tabla de cambio de estado (inicial → durante → después).

**Escenario complementario:** configuración incorrecta, sin tocar Docker.

```powershell
.\hito11-conectividad\scripts\falla_controlada.ps1 -Escenario config -Producto neo4j -Set "NEO4J_DATABASE=noexiste"
```

Levanta una segunda API temporal en `:8001` con la variable sobrescrita **solo en ese proceso**, registra la respuesta (`503 DEPENDENCIA_MAL_CONFIGURADA`, capa `contexto`) y el diagnóstico nativo con el mismo override, y detiene la instancia temporal. El `.env` y la API principal no cambian.

Otros overrides útiles para el laboratorio:

| Override | Escenario de la consigna |
|---|---|
| `MONGODB_PASSWORD=clave-invalida-diag` | credencial inválida en un entorno local de prueba |
| `CASSANDRA_KEYSPACE=noexiste` | keyspace incorrecto |
| `IRIS_NAMESPACE=NOEXISTE` | namespace incorrecto |
| `REDIS_PORT=6390` | puerto no publicado / incorrecto |
| `NEO4J_URI=bolt://neo4j:7687` | host incorrecto (nombre de servicio Docker usado desde la notebook) |
| `DEPENDENCY_TIMEOUT_SECONDS=0.05` | timeout configurado demasiado bajo |

Los valores sobrescritos que contienen `PASSWORD` o `TOKEN` se redactan en la evidencia.

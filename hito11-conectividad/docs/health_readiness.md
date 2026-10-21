# Health, readiness y diagnóstico por dependencia

Implementado en la API (`app/routes/health.py`, `app/services/dependency_health.py`) y cubierto por pruebas unitarias sin motores (`tests/unit/test_dependency_health.py`).

## 1. Endpoints

| Endpoint | Tipo | ¿Consulta bases? | Respuesta |
|---|---|---|---|
| `GET /health` | liveness (compatibilidad con el Hito 10) | No | `200 {"estado":"ok", ...}` |
| `GET /health/live` | liveness | No | `200` mientras el proceso pueda atender HTTP |
| `GET /health/ready` | readiness | Usa la **caché** del diagnóstico | `200 ready` · `200 degraded` · `503 not_ready` |
| `GET /health/dependencias` | diagnóstico por dependencia | Sí, con caché y timeout | `200` con el estado individual de cada producto |
| `GET /health/dependencias?refrescar=true` | idem, forzando un chequeo nuevo | Sí | Limitado a **uno cada 5 s** |

## 2. Significado de los estados

### Por dependencia

| Estado | Significado |
|---|---|
| `up` | El chequeo configurado terminó correctamente |
| `down` | Se intentó y falló. La `clasificacion` indica por qué: `no_disponible`, `timeout`, `timeout_diagnostico`, `rechazo_autenticacion`, `rechazo_autorizacion`, `rechazo_contexto` |
| `unknown` | No se pudo evaluar (error no clasificado) |
| `not_configured` | El módulo no está preparado en este entorno (sin adaptador) |

### Readiness de la API

| Estado | HTTP | Regla | Por qué |
|---|---|---|---|
| `ready` | 200 | Todas las dependencias configuradas están `up` | — |
| `degraded` | 200 | Al menos una `up` y al menos una caída | Cada motor tiene su adaptador: si cae Redis, las rutas de MongoDB siguen funcionando. Sacar la API del tráfico cortaría también las rutas sanas |
| `not_ready` | 503 | Ninguna dependencia está `up` | La API no puede atender ningún caso de uso |

## 3. Qué ejecuta cada chequeo

Cada adaptador tiene un `ping()` liviano, de solo lectura:

| Dependencia | `ping()` | Capas que cubre |
|---|---|---|
| MongoDB | `admin.command("ping")` + `list_collection_names(filter={"name":"equipos"})` | conexión, autenticación, contexto (detecta database vacía/mal escrita) |
| Neo4j | `RETURN 1 AS ok` en la database configurada | Bolt, autenticación, contexto |
| Cassandra | `SELECT release_version FROM system.local` sobre la sesión del keyspace | CQL, keyspace (al abrir la sesión diferida) |
| Redis | `PING` | RESP, autenticación |
| InfluxDB | `GET /health` con token + `SELECT 1` en la database de detalle | HTTP, token, autorización, contexto |
| IRIS | `connect(..., timeout)` + `SELECT 1` | Superserver, autenticación, namespace |

Ningún mensaje de driver ni credencial se devuelve al cliente: solo la clasificación y una descripción genérica.

## 4. Frecuencia, timeout y costo

| Parámetro | Valor | Justificación |
|---|---|---|
| Caché del resultado | **15 s** (`CACHE_TTL_SECONDS`) | Un balanceador o monitor que consulte `/health/ready` cada segundo genera como máximo un chequeo profundo cada 15 s |
| Refresco forzado | como mínimo **5 s** entre chequeos (`MIN_REFRESH_SECONDS`) | Evita que `refrescar=true` se use como generador de carga |
| Timeout por dependencia | `DEPENDENCY_TIMEOUT_SECONDS + 1` (6 s con el valor por defecto) | Deja que el driver informe su propio error antes de que el diagnóstico corte la espera |
| Ejecución | En paralelo (un hilo por dependencia) | El tiempo total del chequeo es el de la dependencia más lenta, no la suma |
| Costo por chequeo | 6 operaciones triviales (ping / `RETURN 1` / `SELECT 1`) | No leen documentos de dominio ni recorren colecciones |
| Requests normales | **No** ejecutan chequeos | Cumple la consigna: no se consulta indiscriminadamente todas las bases en cada request |

Si un driver queda bloqueado más allá del timeout, el diagnóstico lo informa como `timeout_diagnostico` y responde igual. El hilo bloqueado no retrasa la respuesta (RNF5, RNF12).

Cada chequeo deja una línea de log estructurada:

```json
{"evento": "dependency_check", "dependencia": "Redis", "estado": "up", "clasificacion": "ok", "duracion_ms": 3.36}
```

## 5. Ejemplo

```http
GET /health/ready
```

```json
{
  "estado": "degraded",
  "dependencias": {
    "MongoDB": "up", "Neo4j": "up", "Cassandra": "up",
    "Redis": "down", "InfluxDB": "up", "InterSystems IRIS": "up"
  },
  "desde_cache": true,
  "antiguedad_segundos": 4.2
}
```

*(Ejemplo ilustrativo del formato. Los resultados reales están en la evidencia generada por los scripts.)*

## 6. Relación con el diagnóstico externo

`/health/dependencias` responde una pregunta operativa: **¿la API puede usar cada dependencia ahora?** No reemplaza al diagnóstico por capas (`evaluar_conectividad.ps1`), que explica **en qué capa** está la falla. Lo habitual es combinarlos: el health indica qué dependencia está `down` y el modo `nativos -Producto <x>` ubica la capa.

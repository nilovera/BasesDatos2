# Paso 7 — Contratos de eventos, idempotencia y Outbox

Estado: contrato y worker ejecutables para el primer flujo vertical. La
descripción HTTP está en `backend/openapi.json`.

## Principios

- El hecho deportivo se confirma primero en MongoDB.
- Todo evento tiene identidad, secuencia por partido y versión de contrato.
- Toda escritura exige `Idempotency-Key`.
- La misma clave con el mismo contenido produce el mismo resultado.
- La misma clave con contenido distinto es un conflicto.
- Las proyecciones pueden demorarse, pero no inventar ni reemplazar el hecho oficial.
- Una corrección es un nuevo hecho auditable.

## Identidad

| Dato | Formato | Uso |
|---|---|---|
| `eventoId` | `EVE-000001` | Identidad durable del hecho |
| `partidoId` | `PAR-0001` | Agregado afectado |
| `secuencia` | entero positivo | Orden total dentro del partido |
| `Idempotency-Key` | cadena opaca de 16 a 128 caracteres | Identidad del intento lógico del cliente |
| `X-Request-ID` | cadena de trazabilidad | Correlación de logs; no deduplica |
| `outboxId` | UUID o identificador opaco | Identidad del mensaje de propagación |

`eventoId`, `Idempotency-Key` y `X-Request-ID` no son intercambiables.

## Hash de solicitud

La API normaliza método, ruta, partido y body JSON, y calcula un hash SHA-256.
Se almacena junto con la clave idempotente.

| Situación | Respuesta |
|---|---|
| Clave nueva | Ejecutar transacción y responder `201` |
| Misma clave y mismo hash | Devolver resultado original con `200` y `Idempotency-Replayed: true` |
| Misma clave y hash diferente | `409 IDEMPOTENCY_KEY_REUSED` |
| Operación en curso | Espera acotada o `409 IDEMPOTENCY_IN_PROGRESS` |

La clave se conserva al menos durante la ventana definida para reintentos de la
demostración. Su TTL definitivo debe medirse contra volumen y necesidades de
auditoría.

## Comando de evento

Endpoint inicial:

`POST /api/v1/partidos/{partidoId}/eventos`

Headers:

- `Idempotency-Key`: obligatorio;
- `X-Request-ID`: recomendado;
- `Content-Type: application/json`.

Tipos de body:

### Inicio

```json
{
  "tipo": "INICIO_PARTIDO",
  "ocurridoEn": "2030-06-13T20:00:00Z"
}
```

Solo se admite desde `PROGRAMADO`. Pasa el partido a `EN_CURSO`.

### Gol

```json
{
  "tipo": "GOL",
  "ocurridoEn": "2030-06-13T20:23:00Z",
  "periodo": 1,
  "minuto": 23,
  "equipoId": "EQ-01",
  "jugadorId": "JUG-0001"
}
```

El partido debe estar `EN_CURSO`; equipo y jugador deben participar del partido.

### Sustitución

```json
{
  "tipo": "SUSTITUCION",
  "ocurridoEn": "2030-06-13T21:05:00Z",
  "periodo": 2,
  "minuto": 60,
  "equipoId": "EQ-01",
  "saleJugadorId": "JUG-0001",
  "entraJugadorId": "JUG-0009"
}
```

Los jugadores deben pertenecer al mismo equipo y la participación debe permitir
la transición. Este evento delimita qué muestras acepta InfluxDB para cada uno.

### Corrección

```json
{
  "tipo": "CORRECCION_EVENTO",
  "ocurridoEn": "2030-06-13T20:25:00Z",
  "eventoOriginalId": "EVE-000001",
  "motivo": "Jugador informado incorrectamente",
  "reemplazo": {
    "tipo": "GOL",
    "periodo": 1,
    "minuto": 23,
    "equipoId": "EQ-01",
    "jugadorId": "JUG-0002"
  }
}
```

La corrección referencia un evento del mismo partido y recalcula el agregado.
No elimina el evento original.

## Respuesta confirmada

```json
{
  "eventoId": "EVE-000001",
  "partidoId": "PAR-0001",
  "secuencia": 1,
  "tipo": "INICIO_PARTIDO",
  "estadoPartido": "EN_CURSO",
  "marcador": {"local": 0, "visitante": 0},
  "versionPartido": 2,
  "propagacion": "PENDIENTE"
}
```

`propagacion: PENDIENTE` no significa que falló la escritura. Significa que el
hecho oficial fue confirmado y sus vistas derivadas aún pueden estar en tránsito.

## Sobre de Outbox

```json
{
  "versionContrato": 1,
  "outboxId": "8b18e8f7-2cde-4b75-85ff-035b55cc2fd0",
  "eventoId": "EVE-000001",
  "tipo": "INICIO_PARTIDO",
  "partidoId": "PAR-0001",
  "secuencia": 1,
  "ocurridoEn": "2030-06-13T20:00:00Z",
  "registradoEn": "2030-06-13T20:00:00.150Z",
  "payload": {}
}
```

Cada consumidor guarda un checkpoint o deduplica por `eventoId`. Procesar dos
veces el mismo mensaje no debe duplicar estadísticas, relaciones ni caché.

## Implementación del consumidor

`outbox-worker` es un servicio separado de la API. En este incremento proyecta
los eventos confirmados a Redis porque ese motor mantiene el estado caliente y
los eventos recientes; MongoDB sigue siendo la única fuente oficial.

1. Reclama un mensaje `PENDIENTE`, o uno `PROCESANDO` cuyo lease venció, mediante
   `findOneAndUpdate` atómico.
2. Incrementa `intentos` y registra `bloqueo.workerId` y `bloqueo.hasta`.
3. Ejecuta un script Lua en Redis que, atómicamente, deduplica por `eventoId`,
   invalida `cache:partido:*` y agrega el sobre al Stream acotado del partido.
4. Marca el mensaje `PUBLICADO`, libera el lease y fija la retención.
5. Si falla, vuelve a `PENDIENTE` con backoff exponencial y jitter; al agotar
   ocho intentos pasa a `FALLIDO` para diagnóstico.

La entrega es **al menos una vez** y el efecto observable es idempotente. La
prueba controlada fuerza un segundo procesamiento después de publicar y exige
una sola copia en el Stream.

## Reintentos

- Backoff exponencial con jitter y máximo documentado.
- Errores transitorios vuelven a `PENDIENTE` con `proximoIntentoEn`.
- Errores permanentes pasan a `FALLIDO` y requieren diagnóstico.
- Un lock vencido permite que otro worker retome el mensaje.
- Publicar y guardar el checkpoint puede fallar entre pasos; por eso cada destino
  debe ser idempotente.

## Errores HTTP iniciales

| Código | Código de dominio | Ejemplo |
|---|---|---|
| 400 | `INVALID_REQUEST` | JSON o header inválido |
| 404 | `MATCH_NOT_FOUND` | Partido inexistente |
| 409 | `INVALID_MATCH_STATE` | Gol antes del inicio |
| 409 | `IDEMPOTENCY_KEY_REUSED` | Misma clave con otro body |
| 409 | `VERSION_CONFLICT` | Escritura concurrente perdió la versión |
| 422 | `DOMAIN_VALIDATION_ERROR` | Jugador ajeno al equipo |
| 503 | `OFFICIAL_STORE_UNAVAILABLE` | MongoDB no confirma la operación |

## Trazabilidad y métricas

Logs y métricas deben incluir `requestId`, `partidoId`, `tipo`, resultado y
latencia, pero nunca credenciales ni el body completo si pudiera contener datos
sensibles. Métricas previstas:

- requests y errores por endpoint;
- latencia HTTP;
- eventos confirmados por tipo;
- repeticiones idempotentes y conflictos;
- `fixture2030_outbox_pending{consumer="redis"}`;
- `fixture2030_outbox_oldest_pending_seconds{consumer="redis"}`;
- `fixture2030_outbox_published_total{result="NEW|REPLAY"}`;
- `fixture2030_outbox_retries_total`;
- `fixture2030_outbox_failed{consumer="redis"}`;
- `up{job="fixture2030-outbox"}`.

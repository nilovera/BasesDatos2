# Backend — API ejecutable

Servicio FastAPI que implementa el primer flujo vertical sobre MongoDB. El
contrato estable está en `openapi.json` y la documentación interactiva queda
disponible en `http://localhost:8000/docs`.

## Endpoints

- `GET /health`
- `GET /metrics`
- `GET /api/v1/partidos/{partidoId}`
- `GET /api/v1/partidos/{partidoId}/eventos`
- `POST /api/v1/partidos/{partidoId}/eventos`

Toda escritura requiere `Idempotency-Key`. Una creación devuelve `201`; una
repetición del mismo body devuelve `200` y `Idempotency-Replayed: true`; la
misma clave con otro body devuelve `409`.

## Atomicidad

Cada evento se confirma en una transacción MongoDB con tres efectos:

1. actualiza el agregado `partidos` con control de versión;
2. inserta el hecho en `eventos_oficiales`;
3. inserta el mensaje pendiente en `outbox`.

Si una operación falla, ninguno de los tres cambios queda visible. La API usa
write concern `majority` sobre el replica set de laboratorio.

## Alcance actual

Implementa `INICIO_PARTIDO`, `GOL`, `CORRECCION_EVENTO` y `SUSTITUCION`. En
este incremento la participación se valida por pertenencia al plantel activo;
la alineación minuto a minuto se incorporará con el simulador y la telemetría.

La API corre con un worker para mantener simples las métricas de proceso. La
prueba de carga definirá luego la estrategia de múltiples workers.

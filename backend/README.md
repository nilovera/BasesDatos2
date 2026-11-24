# Backend — API ejecutable

Servicio FastAPI que implementa el flujo oficial sobre MongoDB, una capa
temporal Redis y comentarios durables en Cassandra. El contrato estable está en `openapi.json` y la documentación
interactiva queda disponible en `http://localhost:8000/docs`.

## Endpoints

- `GET /health`
- `GET /metrics`
- `GET /api/v1/partidos/{partidoId}`
- `GET /api/v1/partidos/{partidoId}/eventos`
- `POST /api/v1/partidos/{partidoId}/eventos`
- `POST /api/v1/sesiones`
- `GET /api/v1/sesiones/{sesionId}`
- `POST /api/v1/sesiones/{sesionId}/renovacion`
- `DELETE /api/v1/sesiones/{sesionId}`
- `POST/GET /api/v1/partidos/{partidoId}/comentarios`
- `GET /api/v1/usuarios/{usuarioId}/comentarios`
- `PATCH /api/v1/comentarios/{comentarioId}/moderacion`

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

## Redis

La lectura de partidos usa Cache-Aside y expone `X-Cache: HIT`, `MISS` o
`BYPASS`. Después de una escritura oficial se invalida la clave. Las sesiones
se guardan como Hash con TTL; un GET no renueva el tiempo y el endpoint de
renovación ejecuta la actualización de manera explícita y atómica.

## Cassandra

La publicación usa `Idempotency-Key`. Las vistas por partido y usuario se
escriben en un batch acotado y se consultan por claves de partición conocidas.
La moderación actualiza ambas vistas sin escaneos ni `ALLOW FILTERING`. La
paginación devuelve un cursor opaco compuesto por timestamp e identificador,
por lo que no omite comentarios con la misma marca temporal.

`GET /health` devuelve `UP` cuando MongoDB, Redis y Cassandra están operativos,
y `DEGRADED` con el estado individual cuando una dependencia falla. El proceso
HTTP continúa observable para diferenciar la caída de una base de la caída de
la propia API.

Regenerar el contrato después de modificar rutas o modelos:

```text
python scripts/exportar_openapi.py
```

## Alcance actual

Implementa `INICIO_PARTIDO`, `GOL`, `CORRECCION_EVENTO` y `SUSTITUCION`. En
este incremento la participación se valida por pertenencia al plantel activo;
la alineación minuto a minuto se incorporará con el simulador y la telemetría.

La API corre con un worker para mantener simples las métricas de proceso. La
prueba de carga definirá luego la estrategia de múltiples workers.

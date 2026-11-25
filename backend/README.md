# Backend — API ejecutable

Servicio FastAPI que implementa el flujo oficial sobre MongoDB, una capa
temporal Redis, comentarios durables en Cassandra, telemetría en InfluxDB y
recorridos en Neo4j. El contrato estable está en `openapi.json` y la documentación
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
- `POST/GET /api/v1/partidos/{partidoId}/telemetria/posiciones`
- `GET /api/v1/partidos/{partidoId}/jugadores/{jugadorId}/mapa-calor`
- `POST /api/v1/partidos/{partidoId}/telemetria/estadisticas-equipos`
- `POST /api/v1/partidos/{partidoId}/telemetria/agregaciones/15m`
- `GET /api/v1/partidos/{partidoId}/telemetria/resumenes-equipos/15m`
- `GET /api/v1/grafo/resumen`
- `GET /api/v1/grafo/equipos/{equipoId}/rivales`
- `GET /api/v1/grafo/jugadores/{jugadorId}/recomendaciones`
- `GET /api/v1/grafo/equipos/{origenId}/camino/{destinoId}`

Los eventos oficiales y comentarios requieren `Idempotency-Key`. Una creación devuelve `201`; una
repetición del mismo body devuelve `200` y `Idempotency-Replayed: true`; la
misma clave con otro body devuelve `409`.

La telemetría usa como identidad tabla + tags + timestamp. Repetir el mismo
lote converge sobre los mismos puntos; dentro de un lote se rechazan dos
valores para el mismo jugador/equipo y timestamp.

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

## InfluxDB

Los lotes de hasta 250 muestras se escriben por `/api/v3/write_lp` con
`accept_partial=false`. La lectura de posiciones usa cursor opaco compuesto por
timestamp y jugador, y el mapa de calor se reproduce desde los puntos. Los
resúmenes de 15 minutos se guardan en una base de mayor retención.

## Neo4j

El grafo es una proyección del catálogo autoritativo. Permite recorrer partidos,
recomendar jugadores con el mismo puesto y confederación, y explicar caminos
entre equipos. La carga repetida converge mediante `MERGE`.

`GET /health` devuelve `UP` cuando MongoDB, Redis, Cassandra, InfluxDB y Neo4j están operativos,
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

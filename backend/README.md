# Backend — API ejecutable

Servicio FastAPI que implementa el flujo oficial sobre MongoDB, una capa
temporal Redis, comentarios durables en Cassandra, telemetría en InfluxDB y
recorridos en Neo4j y un Data Mart PostgreSQL separado. El contrato estable está en `openapi.json` y la documentación
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
- `POST /api/v1/analitica/datamart/refrescar`
- `GET /api/v1/analitica/datamart/resumen`
- `GET /api/v1/analitica/{datamart|operacional}/goles-por-equipo`

Los eventos oficiales y comentarios requieren `Idempotency-Key`. Una creación devuelve `201`; una
repetición del mismo body devuelve `200` y `Idempotency-Replayed: true`; la
misma clave con otro body devuelve `409`.

La telemetría usa como identidad tabla + tags + timestamp. Repetir el mismo
lote converge sobre los mismos puntos; dentro de un lote se rechazan dos
valores para el mismo jugador/equipo y timestamp.

## Atomicidad

Cada evento se confirma en una transacción MongoDB con estos efectos:

1. actualiza el agregado `partidos` con control de versión;
2. inserta el hecho en `eventos_oficiales`;
3. inserta el mensaje pendiente en `outbox`;
4. agrega la entrega de auditoría en `auditoria_pendiente`.

El servicio `outbox-worker` reclama mensajes con lease, invalida el cache del
partido y agrega el evento a un Redis Stream. Un Hash por `eventoId` hace que el
script Lua sea idempotente aun si Redis confirmó la proyección y el acuse en
MongoDB falló. Luego proyecta el evento a Neo4j mediante `MERGE`; solo después
confirma el mensaje. Los reintentos usan backoff exponencial con jitter; al agotar el
límite el mensaje pasa a `FALLIDO` sin eliminarse.

La API ya no invalida Redis directamente después del commit: esa escritura
derivada pertenece al worker y por eso la consistencia del cache es eventual.

Si la transacción falla, ninguno de esos cambios queda confirmado. La API usa
write concern `majority` sobre el replica set de laboratorio.

## Redis

La lectura de partidos usa Cache-Aside y expone `X-Cache: HIT`, `MISS` o
`BYPASS`. El worker invalida la clave después de una escritura oficial. Las sesiones
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

El grafo proyecta el catálogo común y eventos oficiales mediante Outbox. Permite recorrer partidos,
recomendar jugadores con el mismo puesto y confederación, y explicar caminos
entre equipos. La carga repetida converge mediante `MERGE`.

## Data Mart

PostgreSQL recibe por lote una proyección analítica de MongoDB e InfluxDB. El
refresh usa UPSERT y conserva por separado eventos oficiales y ventanas de 15
minutos. Estas rutas no participan de la transacción oficial. Las consultas
reutilizan un pool PostgreSQL acotado de 2 a 10 conexiones; la configuración es
ajustable mediante `DATAMART_POOL_*`.

`GET /health` devuelve `UP` cuando MongoDB, Redis, Cassandra, InfluxDB, Neo4j y Data Mart están operativos,
y `DEGRADED` con el estado individual cuando una dependencia falla. El proceso
HTTP continúa observable para diferenciar la caída de una base de la caída de
la propia API.

Regenerar el contrato después de modificar rutas o modelos:

```text
python scripts/exportar_openapi.py
```

## Alcance actual

Implementa `INICIO_PARTIDO`, `GOL`, `TARJETA`, `SUSTITUCION`,
`GOL_ANULADO_VAR`, `FIN_PARTIDO` y `CORRECCION_EVENTO`. El simulador crea una
alineación 1-4-4-2, aplica cambios puesto por puesto y sólo genera telemetría de
los once jugadores activos. Para escrituras manuales externas todavía se valida
plantel/equipo, no la participación histórica completa.

La API corre con un worker para mantener simples las métricas de proceso. La
carga ya tiene mediciones locales; una estrategia de múltiples workers
requiere validar además la coordinación del simulador y las métricas.

## Auditoría del incremento 15

La API 0.10.0 expone actividad por actor/día y recurso/día, y consulta de
entregas pendientes. Las rutas están en `openapi.json`; requieren una sesión
ADMIN de laboratorio mediante `X-Session-ID`. Los comentarios incorporan
auditoría en su batch Cassandra; las acciones MongoDB usan un relay durable.
Los logs HTTP incluyen request ID, ruta, método, resultado y duración sin
cuerpos ni credenciales.

Diseño y límites: [auditoría](../docs/diseno/10_auditoria_actividad.md).
Pruebas unitarias y ejecución HTTP integrada de auditoría con resultado OK:
[estado de validación](../docs/estado_validacion.md).

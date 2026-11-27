# Cassandra

Cassandra es la fuente durable de comentarios. El esquema se diseña por
consulta y mantiene vistas separadas por partido y por usuario. No utiliza
`ALLOW FILTERING`, joins ni escaneos globales.

## Laboratorio y arquitectura objetivo

El entorno local usa `cassandra:5.0.9`, un nodo, `SimpleStrategy` y RF=1 para
ser reproducible en una notebook. Esto demuestra CQL, particionamiento,
clustering, persistencia y degradación, pero **no** tolerancia real a fallas.

La arquitectura objetivo usa al menos tres nodos,
`NetworkTopologyStrategy`, RF=3, `LOCAL_QUORUM` para publicar y `LOCAL_ONE`
para leer el feed público. Esa diferencia se mantiene explícita para no
presentar el laboratorio como una prueba de quórum.

## Particiones

- Feed: `(match_id, bucket_minuto_utc, shard)`.
- Perfil: `(user_id, day_bucket_utc)`.
- Clustering: `created_at DESC, comment_id ASC`.
- Shards del laboratorio: 4, calculados de forma estable desde `usuarioId`.
- Moderación: actualización acotada de las dos vistas mediante un localizador.
- Idempotencia: `INSERT IF NOT EXISTS` por `Idempotency-Key` y hash del body.

Los buckets limitan el crecimiento de cada partición y los shards evitan que
una final concentre todas las escrituras en una sola partición.



## Auditoría y validación

El incremento 15 agrega historial por actor/día y recurso/día, con reserva
idempotente de operación y sin TTL configurado. Las acciones de comentarios
se conservan en su batch; las oficiales llegan desde una cola MongoDB. El
modelo exacto se describe en [auditoría](../docs/diseno/10_auditoria_actividad.md).

Los comentarios, el nodo local y la auditoría tienen evidencia Docker. La
auditoría cuenta además con pruebas unitarias; su resultado HTTP integrado
registra historial, cero duplicados y entrega MongoDB → Cassandra confirmada. El número de shards
no se presenta como óptimo sin un benchmark representativo de escritura.
Ver [estado de validación](../docs/estado_validacion.md).

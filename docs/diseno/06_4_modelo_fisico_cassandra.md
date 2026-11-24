# 6.4 Modelo físico de Cassandra

## Responsabilidad

Cassandra es la fuente durable de comentarios y su estado de moderación. No
almacena el fixture oficial, sesiones ni telemetría. Los identificadores de
partidos y usuarios siguen las convenciones comunes (`PAR-0001`, `USR-0003`).

## Patrones de acceso

| Consulta | Tabla | Clave de partición | Clustering |
|---|---|---|---|
| Feed reciente de un partido | `comments_by_match_bucket_shard` | `(match_id, bucket, shard)` | `created_at DESC, comment_id ASC` |
| Historial de un usuario | `comments_by_user_day` | `(user_id, day_bucket)` | `created_at DESC, comment_id ASC` |
| Localizar para moderar | `comment_locator_by_id` | `comment_id` | — |
| Detectar replay/conflicto | `comment_write_requests` | `idempotency_key` | — |

Se acepta duplicación entre las dos vistas porque responden consultas
distintas. No se usan joins, índices secundarios ni `ALLOW FILTERING`.

## Hotspots, buckets y shards

El feed usa buckets de un minuto UTC y cuatro shards estables calculados desde
`usuarioId`. Así una final no concentra toda la escritura en una partición y
la lectura hace fan-out solamente sobre cuatro particiones conocidas. La API
fusiona los resultados y pagina mediante el límite temporal `antesDe`.

El historial por usuario usa un bucket diario porque el volumen individual es
mucho menor. La cantidad de shards deberá validarse con los escenarios `1x`,
`5x` y `10x`; cuatro es una decisión inicial, no un resultado de capacidad.

## Consistencia e idempotencia

La publicación registra primero la clave idempotente con `INSERT IF NOT
EXISTS`. Repetir clave y body devuelve el mismo comentario; reutilizar la
clave con otro body devuelve `409`.

El laboratorio usa RF=1 y `LOCAL_ONE`. La arquitectura objetivo usa RF=3,
`LOCAL_QUORUM` para confirmar publicaciones y `LOCAL_ONE` para el feed público.
Un batch logged contiene únicamente las tres escrituras acotadas del mismo
comentario; no se usa como mecanismo de carga masiva.

## Moderación

El localizador permite conocer todas las claves primarias sin escanear. La
moderación actualiza las vistas por partido y por usuario. El feed público
omite `OCULTO`; la vista administrativa puede recuperarlo sin mostrar el
contenido.

## Límites demostrados

- Un nodo demuestra persistencia y modelo CQL, no quórum.
- No se realizaron todavía pruebas de carga para elegir 4, 8 o 16 shards.
- La autenticación/autorización administrativa es simulada.
- La convergencia se ejecuta sin worker de reparación; se agregará junto con
  el procesamiento completo de Outbox.


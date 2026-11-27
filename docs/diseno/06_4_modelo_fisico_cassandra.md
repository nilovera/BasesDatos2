# 6.4 Modelo físico de Cassandra

## Responsabilidad y consultas

Cassandra conserva comentarios, su visibilidad actual y el historial de
auditoría incorporado en el incremento 15. El diseño parte de consultas
conocidas: comentarios recientes de un partido, comentarios de un usuario y
acciones de un actor o recurso durante un día.

| Tabla | Consulta o control |
|---|---|
| comments_by_match_bucket_shard | Comentarios por partido, bucket temporal y shard |
| comments_by_user_day | Comentarios de un usuario y día |
| comment_write_requests | Identidad y hash idempotente de publicación |
| comment_locator_by_id | Localizador por ID para actualizar las dos vistas de comentarios |
| audit_by_actor_day | Historial por actor y día UTC |
| audit_by_resource_day | Historial por recurso y día UTC |
| audit_operations | Reserva de operación y metadatos originales del historial |

Los nombres, columnas y claves exactas se definen en `cassandra/init/`.
El estado actual de moderación se conserva en ambas vistas del comentario.
Las vistas duplicadas evitan escaneos globales y responden a accesos distintos;
no constituyen replicación física ni tablas normalizadas con joins.

## Particiones, orden y paginación

Los comentarios por partido combinan bucket temporal y cuatro shards
deterministas. El bucket limita el crecimiento de cada partición y el shard
distribuye escrituras del mismo partido. La lectura combina particiones
acotadas y aplica un orden estable. La vista por usuario utiliza bucket diario.

La auditoría usa particiones actor/día y recurso/día, ordenadas por fecha e ID.
El cursor incorpora las claves de consulta y ambos valores de orden para
resolver acciones con igual marca temporal. No hay consulta global de todas
las acciones ni búsqueda por filtros arbitrarios.

## Escritura e idempotencia

La publicación conserva la identidad del comando y escribe sus vistas con un
batch logged acotado. El incremento 15 agrega las vistas del historial al batch.
La moderación actualiza visibilidad y agrega una acción; no reemplaza acciones
anteriores. Un replay confirmado devuelve su respuesta sin volver a aplicar un
estado antiguo. En moderación, `Idempotency-Key` es opcional.

El batch no da aislamiento de lectura entre particiones. La reserva previa de
operación puede existir antes de completarse las vistas; los reintentos deben
conservar sus metadatos originales. No se implementa un worker general de
reparación de todas las vistas sociales.

## Consistencia, conservación y validación

El laboratorio usa RF=1 y `LOCAL_ONE`. El nodo fue verificado UN y se registró
su falla y recuperación. Los comentarios participan en la carga mixta de
lectura; no hay un benchmark de escritura que determine el número óptimo de
shards ni una demostración con RF=3.

El historial de auditoría no configura TTL y es append-only desde la API. No
es WORM: un administrador con acceso a las tablas puede modificarlo. Para una
escala mayor se requieren política de conservación, permisos reales y medición
de particiones, especialmente del actor de servicio del simulador.

La auditoría tiene validación unitaria y una comprobación HTTP integrada
exitosa en Docker. Su resultado propio verifica tres acciones de un comentario
sin duplicados y la entrega de la creación de una simulación desde MongoDB.
No representa una prueba de capacidad ni de replicación.
Ver [diseño de auditoría](10_auditoria_actividad.md) y
[estado de validación](../estado_validacion.md).

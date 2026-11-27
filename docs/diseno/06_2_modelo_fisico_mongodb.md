# 6.2 Modelo físico de MongoDB

## Responsabilidad y despliegue

MongoDB es autoridad del catálogo y del núcleo deportivo. El laboratorio
despliega un replica set `rs0` de un miembro para habilitar transacciones. La
verificación Docker registra PRIMARY, 64 equipos, 1.024 jugadores y cero
jugadores huérfanos. Un miembro no proporciona alta disponibilidad.

## Colecciones y accesos

| Colección | Propósito y acceso |
|---|---|
| equipos | Catálogo por identificador de equipo |
| jugadores | Catálogo por identificador y pertenencia a equipo |
| partidos | Estado, marcador, alineaciones, versión y secuencia del agregado |
| eventos_oficiales | Hechos por partido y secuencia; identidad de evento única |
| contadores | Asignación secuencial de identificadores de eventos y partidos simulados |
| outbox | Entrega de eventos a Redis y Neo4j, con estado, lease y reintentos |
| simulaciones | Configuración, semilla, reloj y estado de ejecuciones deportivas |
| auditoria_pendiente | Entrega durable de acciones MongoDB hacia el historial Cassandra |

Los esquemas e índices de `mongodb/init/` definen las restricciones efectivas.
La clave, el hash y la respuesta idempotente del comando deportivo se conservan
en `eventos_oficiales`, no en una colección de idempotencia separada.
La colección de entrega de auditoría se incorpora mediante
`04_audit_schema.js`. Su contenido se elimina después de confirmar el destino;
el historial consultable permanece en Cassandra.

## Transacción y concurrencia

Registrar un evento valida las referencias, el estado permitido y el comando.
La transacción comprueba la versión, actualiza el partido, inserta el evento,
conserva la respuesta idempotente y agrega Outbox. El incremento 15 incluye el
envío de auditoría en esa transacción. Un conflicto de versión o un error no
debe dejar un evento confirmado con el agregado sin actualizar.

El identificador del evento y la secuencia por partido evitan confundir
reintentos con hechos distintos. La lectura incremental de eventos usa la
secuencia del partido como referencia. Una corrección inserta otro evento que
referencia el original y recalcula el agregado; no borra el historial original.

## Semillas y límites

La generación de catálogo es reproducible. La carga del partido usa una
inserción condicionada para conservar el estado operativo al reiniciar el
entorno. El partido base parte sin eventos y las nuevas simulaciones crean
partidos propios. Los números de una captura no representan conteos permanentes.

El despliegue local no acredita autenticación MongoDB de producción, réplica
redundante, sharding o restauración de backups. La carga HTTP mide el conjunto
de la API; no aísla la capacidad máxima del motor documental.

Pruebas y resultados: [estado de validación](../estado_validacion.md).

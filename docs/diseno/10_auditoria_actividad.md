# Auditoría de actividad del Fixture 2030

## Alcance implementado

Se conserva un evento por acción confirmada. Un reintento idempotente no representa una nueva acción y conserva el registro original. Las solicitudes rechazadas y las lecturas quedan en los logs HTTP; este incremento no registra cada GET, cada muestra de posición ni cada movimiento de la interfaz como un evento de auditoría.

| Acción | Recurso | Origen del registro |
|---|---|---|
| PUBLICAR_COMENTARIO | COMENTARIO | Batch acotado de Cassandra |
| MODERAR_COMENTARIO | COMENTARIO | Batch acotado de Cassandra |
| REGISTRAR_EVENTO | EVENTO | Transacción MongoDB y reenvio durable |
| CORREGIR_EVENTO | EVENTO | Transacción MongoDB y reenvio durable |
| CREAR_SIMULACION | SIMULACION | Transacción MongoDB y reenvio durable |
| INICIAR_SIMULACION | SIMULACION | Transacción MongoDB y reenvio durable |
| PAUSAR_SIMULACION | SIMULACION | Transacción MongoDB y reenvio durable |
| REANUDAR_SIMULACION | SIMULACION | Transacción MongoDB y reenvio durable |
| VELOCIDAD_SIMULACION | SIMULACION | Transacción MongoDB y reenvio durable |

No se rellenan retrospectivamente acciones anteriores a esta actualización: no hay evidencia suficiente para atribuirles un actor. Los eventos que genere el simulador también se auditan desde los mismos servicios de escritura.

Una corrección se agrupa bajo el identificador del evento original y conserva en el detalle el nuevo evento de corrección. Así una consulta por recurso recupera el alta y su corrección juntas.

## Identificación del actor

| actorTipo | Significado |
|---|---|
| SESION_LAB | Usuario de una sesión existente en Redis recibida por X-Session-ID |
| DECLARADO | Autor o moderador indicado en el comando, sin sesión que pruebe identidad |
| ANONIMO | Request HTTP sin sesión ni autor declarado aplicable |
| SERVICIO | Operación interna, como las generadas por simulador |

Las sesiones existentes son de laboratorio: el cliente puede crear una sesión eligiendo su usuario y rol. No se presentan como autenticación de producción. Las consultas de auditoría exigen una sesión de laboratorio ADMIN. No se guardan su identificador, token ni cabeceras de autorización en la auditoría.

Si se proporciona una sesión, el autor o moderador del comando debe coincidir con su usuario; de lo contrario se responde 403. El simulador se identifica como servicio `simulador`; el autor sintético del comentario queda separado en `detalle.autorComentario`.

## Registro conservado

Cada evento contiene `auditoriaId`, `operacionId`, `actorId`, `actorTipo`, `fecha` UTC, `accion`, `recursoTipo`, `recursoId`, `resultado`, `requestId`, `metodo`, `ruta` y metadatos acotados en `detalle`.

No se guardan textos de comentarios, cuerpos completos, tokens, sesiones ni credenciales. Para moderación se conserva el estado aplicado y un hash del motivo, no el texto libre. El resultado de una acción confirmada es `OK`; los errores de requests se registran técnicamente con su código HTTP. No se afirma que este historial sustituya una auditoría de todos los intentos fallidos.

## Modelo Cassandra dirigido por consultas

| Tabla | Consulta que resuelve | Clave |
|---|---|---|
| audit_by_actor_day | Qué hizo un actor en un día UTC | Partición actor_id y day_bucket; clustering occurred_at DESC y audit_id ASC |
| audit_by_resource_day | Qué acciones afectaron un recurso en un día UTC | Partición resource_type, resource_id y day_bucket; mismo clustering |
| audit_operations | Identidad y contenido original de una operación | operation_id |

Las consultas usan claves completas de partición, límites entre 1 y 100 y cursor por fecha e ID. El cursor incluye actor o recurso y día para evitar mezclar paginas de consultas distintas. La fecha se normaliza a milisegundos, igual que Cassandra timestamp. No se usan filtros globales.

La duplicación entre las dos vistas es intencional y responde a consultas diferentes. Cada acción se agrega como una fila; la API no ofrece modificar ni borrar el historial. La reserva por operación usa INSERT IF NOT EXISTS y conserva los metadatos originales. El marcador interno `projected` puede cambiar; el contenido del evento no se reemplaza.

Esto es append-only en la aplicación, no almacenamiento físicamente inalterable: un administrador con acceso directo a Cassandra puede modificar tablas. No se implementaron firma, WORM ni control externo de integridad.

## Confirmación y reintentos

### Comentarios y moderación

Publicar un comentario agrega su auditoría al mismo batch logged acotado que escribe las vistas del comentario. Moderar agrega la nueva acción junto con la actualización del estado. Antes del batch se reserva la identidad idempotente; esa reserva por si sola no aparece en las consultas del historial.

La clave de publicación existente identifica una sola acción. En moderación se admite `Idempotency-Key` opcional; una misma clave con otro estado, actor, recurso o motivo devuelve conflicto. Un replay confirmado devuelve la respuesta anterior sin volver a aplicar el estado: no revierte una moderación posterior. Sin esa clave, cada nueva llamada de moderación es una acción distinta.

Un batch logged facilita completar sus escrituras ante fallos, pero no proporciona aislamiento de lectura entre particiones. El laboratorio conserva RF=1 y LOCAL_ONE; no se declara quórum, alta disponibilidad ni orden global entre todos los actores.

### Operaciones oficiales y simulaciones

La transacción MongoDB guarda el cambio de negocio y un documento en `auditoria_pendiente`. Si no puede guardar ambos, no se confirma la transacción. La auditoría puede atrasarse respecto del dato oficial.

Un hilo de la API reclama pendientes con un lease, envía el evento a Cassandra y elimina el pendiente solo después de confirmar la escritura. Ante un fallo, conserva el evento y programa otro intento con espera creciente. Si la API cae después de escribir Cassandra y antes de quitar el pendiente, la reserva idempotente evita duplicados al repetirlo.

MongoDB es un punto transitorio de entrega para estas acciones; el historial consultable final esta en Cassandra. No se copian a MongoDB los textos de comentarios ni la telemetría por agregar esta auditoría. La Outbox deportiva para Redis y Neo4j mantiene su responsabilidad separada.

## Operación y conservación

Swagger expone:

- `GET /api/v1/auditoria/actores/{actorId}?dia=YYYYMMDD`
- `GET /api/v1/auditoria/recursos/{tipo}/{recursoId}?dia=YYYYMMDD`
- `GET /api/v1/auditoria/pendientes`

No hay una pantalla nueva en el front. Las consultas exigen X-Session-ID de una sesión ADMIN del laboratorio. En logs HTTP se usa el template de ruta para evitar imprimir identificadores de sesiones. Las dependencias informadas por ruta son las previstas para ese flujo; no son spans medidos ni prueban que cada request haya consultado todas ellas.

El esquema no configura TTL para el historial: la política de conservación queda sin un plazo de expiración automático. Antes de usarlo a gran escala se deben definir archivo, retención, permisos reales y carga por partición. Un servicio muy activo podría requerir buckets menores o shards; el bucket diario es la decisión inicial del laboratorio.

## Validación y límites

Las pruebas unitarias comprueban identidad del actor, exclusión de campos sensibles, idempotencia, recuperación tras fallo de batch, historial de moderación, replay antiguo, paginación de marcas temporales iguales, transacción de cola y conservación de pendientes cuando Cassandra falla.

El script `scripts/probar_auditoria.ps1` comprueba con HTTP y motores reales publicación, replay, dos moderaciones, paginación, vistas, acceso ADMIN y entrega de una creación de simulación desde MongoDB. Conserva evidencia sin guardar el identificador de sesión. No detiene contenedores ni inicia partidos.

La validación local comprende 170 pruebas unitarias y de regresión, incluidas
25 específicas de auditoría. La ejecución HTTP con motores reales del
27 de noviembre de 2026 terminó en OK. El
[resultado original](../../evidencia/ejecuciones/auditoria-20261127T040527Z/resultado.json)
conserva tres acciones del comentario de prueba, cero duplicados, rechazo de
consulta pública con 403 y entrega MongoDB → Cassandra confirmada al crear
una simulación. El script también comprobó paginación, vista por actor y que
repetir una moderación antigua no revierta el estado posterior.

La creación de simulación valida ese recorrido de entrega; no acredita por
sí sola todas las acciones oficiales, reinicios intermedios, capacidad o
replicación. Los resultados unitarios y la integración son evidencias
complementarias. La transcripción de instalación identifica API 0.10.0; el JSON
original no capturó el SHA de ejecución y esa limitación se conserva en la
[procedencia](../../evidencia/ejecuciones/auditoria-20261127T040527Z/procedencia.json).

Los logs HTTP técnicos se observan en la salida del contenedor. Cassandra
conserva el historial de acciones confirmadas; no almacena todos los logs
técnicos de la API. No todas las modificaciones de perfiles, sesiones,
telemetría o ETL tienen auditoría de usuario en este incremento.
Ver [estado de validación](../estado_validacion.md).

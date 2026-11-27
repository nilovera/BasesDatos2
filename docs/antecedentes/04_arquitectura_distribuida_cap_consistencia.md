# Fixture 2030 — Arquitectura, consistencia y distribución

## Propiedad del dato

MongoDB es autoridad del catálogo y del hecho deportivo. Cassandra es autoridad
de comentarios, moderación e historial de auditoría. InfluxDB conserva la
telemetría sintética ingresada. Redis y Neo4j mantienen vistas derivadas o
temporales. El Data Mart organiza copias analíticas obtenidas mediante ETL.
No existe una transacción distribuida que abarque todos los motores.

## Consistencia y coordinación

### Transacción oficial

El registro de un evento valida el comando y la versión del partido. En una
transacción MongoDB se actualiza el agregado, se agrega el evento y se conserva
el mensaje Outbox. El incremento 15 agrega el envío de auditoría a esa misma
transacción. Si alguno de esos cambios no puede confirmarse, la operación
completa no se presenta como exitosa.

`writeConcern: majority` opera sobre la topología desplegada. Con un solo miembro
no proporciona tolerancia a la pérdida de ese miembro ni de su almacenamiento.
La atomicidad local no garantiza que Redis, Neo4j o Cassandra ya hayan recibido
la proyección al devolver la respuesta HTTP.

### Entrega eventual

El worker Outbox reclama mensajes mediante lease, actualiza Redis y luego
proyecta Neo4j. Solo marca `PUBLICADO` tras completar ambos pasos. Los reintentos
usan identidad estable y los destinos deduplican el efecto. Si falla entre la
escritura remota y la confirmación del mensaje, repetirlo no debe producir un
segundo evento lógico.

La secuencia define el orden deportivo por partido. El worker actual no impone
una barrera estricta que impida procesar n+1 mientras n se reintenta. Por ello
no se afirma orden causal global de todas las proyecciones. La consulta del
marcador puede recurrir a MongoDB cuando la secuencia derivada no coincide con
la oficial. Neo4j no debe emplearse como autoridad para resolver un conflicto
de marcador o una corrección histórica.

### Comentarios y auditoría

Los comentarios escriben varias vistas con un batch logged acotado. El batch
favorece la terminación de las mutaciones, sin aislamiento de lectura entre
particiones ni transacción distribuida con MongoDB. La auditoría de comentarios
se agrega al mismo batch; la de hechos MongoDB llega mediante una cola durable
separada. La entrega puede retrasarse y el historial debe consultarse con esa
consideración.

## Particionado y replicación

Particionar distribuye conjuntos de datos; replicar conserva copias. Tener
contenedores de motores diferentes no equivale a replicar cada base.

| Motor | Implementación local | Diseño de escala que requiere validación adicional |
|---|---|---|
| MongoDB | Replica set de un miembro, índices por IDs y acceso por partido | Varios miembros en dominios de falla distintos; sharding solo con volumen y distribución medidos |
| Cassandra | Un nodo, RF=1, `LOCAL_ONE`; comentarios por bucket y cuatro shards | RF=3, consistencia elegida por operación, pruebas de pérdida de nodo y particiones calientes |
| Redis | Standalone, 256 MB, LFU, RDB y AOF | Réplicas y failover; separación de sesiones y caché según criticidad |
| InfluxDB | Un nodo Core; retención diferenciada de detalle e histórico | Estrategia de capacidad, backup y recuperación compatible con la edición elegida |
| Neo4j | Community de un nodo; IDs únicos y proyección por evento | Edición/topología compatible con redundancia y pruebas de reconstrucción |
| Data Mart | PostgreSQL de un nodo con volumen y pool | Réplica, backups, reconciliación de ETL y carga analítica representativa |

En Cassandra una clave de partido única sería un punto caliente durante la
final. El bucket temporal acota el tamaño y el shard reparte la escritura. La
vista por usuario y día resuelve otro patrón de lectura; no es normalización
relacional ni una réplica física. La auditoría usa actor/día y recurso/día;
un actor de servicio muy activo podría requerir menor bucket o sharding.

La cantidad de particiones puede estimarse con la tasa máxima por partido,
duración del bucket, bytes por fila y factor de replicación. Esos parámetros
deben medirse con distribución sesgada, no solo con un promedio uniforme.

## Comportamiento ante fallas

| Falla | Efecto esperado | Evidencia o alcance |
|---|---|---|
| API | Interrumpe acceso HTTP | Parada, alerta y recuperación registradas |
| MongoDB | Impide confirmar eventos oficiales | Parada, degradación y recuperación registradas |
| Redis | Bypass del caché; sesiones y temporales afectados | Bypass y recuperación registrados |
| Cassandra | Comentarios degradados y auditoría atrasada | Falla social registrada; entrega de auditoría MongoDB → Cassandra comprobada por HTTP, sin prueba nueva de falla del destino |
| InfluxDB | Telemetría y mapas degradados | Lectura oficial conservada en la prueba |
| Neo4j | Recorridos degradados y Outbox puede acumularse | Lectura oficial y recuperación registradas |
| Data Mart | Consulta analítica y ETL degradados | Aislamiento y recuperación registrados |
| Worker Outbox | Datos oficiales confirmados con proyecciones atrasadas | Replay y convergencia registrados |

La continuidad de una lectura oficial no implica continuidad total de la
simulación: un fallo de escritura en sus dependencias puede detener su trabajo
con estado `ERROR`. El sistema informa degradación en lugar de simular éxito.

## Recuperación y durabilidad

Los volúmenes Docker sobreviven a reinicios normales. RDB/AOF agrega mecanismos
de persistencia Redis; no elimina el riesgo de pérdida del host. La prueba de
parada/reinicio conserva esos volúmenes y no acredita restauración de backups.

Una estrategia productiva debe definir copias verificadas, almacenamiento fuera
del dominio de falla, retención, cifrado, permisos y ensayos de restauración.
El RPO expresa pérdida de datos tolerable; el RTO, tiempo de recuperación.
No se asignan valores alcanzados a estas métricas porque no hay un ensayo
integral que los haya medido.

## Evidencia y límites

Las verificaciones Docker, fallas y carga existentes se enlazan en el
[registro de validación](../estado_validacion.md). Acreditan un laboratorio
integrado de un host. No acreditan failover automático, partición entre réplicas,
recuperación regional, millones de usuarios ni capacidad máxima sostenida.
La arquitectura distribuida de escala es una referencia de evolución, con
costos y pruebas adicionales, no un despliegue ya realizado.

# Fixture 2030 — Comparación de motores y estrategia CAP

## Fundamento de la persistencia políglota

La plataforma combina modelos porque sus consultas y garantías difieren. No se
selecciona un motor por una superioridad general, sino por el costo de resolver
el acceso concreto: leer un agregado, recorrer vínculos, consultar una serie
temporal o agregar hechos analíticos. La especialización agrega complejidad de
operación y sincronización; se acepta cuando existe una responsabilidad diferenciada.

| Motor | Adecuación principal | Costo o límite | Aplicación efectiva |
|---|---|---|---|
| MongoDB | Documentos flexibles, índices y transacciones entre documentos | Las referencias requieren validación; las copias externas no participan de la transacción | Catálogo, partidos, eventos, Outbox y cola transitoria de auditoría |
| Redis | Acceso por clave y estructuras en memoria | Memoria finita, expiración y expulsión; persistencia local sin HA | Caché, sesiones, marcador, contadores, ranking y Stream |
| Cassandra | Escrituras distribuidas y consultas por partición conocida | Diseño dirigido por consultas; duplicación, particiones calientes y tombstones | Comentarios y auditoría por actor/recurso y día |
| InfluxDB | Muestras con tiempo, rangos, ventanas y retención | Cardinalidad de series y costo de conservación; despliegue local de un nodo | Posiciones, estadísticas y resúmenes |
| Neo4j | Recorridos y patrones entre entidades | Sincronización del catálogo; no sustituye un CRUD documental por defecto | Rivales, recomendaciones, caminos y relaciones de eventos |
| PostgreSQL Data Mart | Grano definido, dimensiones y agregaciones SQL | Frescura batch y mantenimiento de ETL | Hechos de eventos y estadísticas por equipo/15 minutos |

El Data Mart no reemplaza la persistencia operacional NoSQL ni confirma
partidos. Constituye un destino analítico separado. IRIS se evaluó y excluyó
por superposición de responsabilidad con MongoDB, según
[ADR-001](../diseno/ADR-001-exclusion-iris.md).

## Comparación por decisión

### Núcleo deportivo

Un evento altera el partido y genera trabajo para sus vistas. MongoDB permite
confirmar esos documentos en una transacción, con una versión del agregado y
una clave idempotente. Cassandra también puede guardar eventos, pero mantener
allí otro registro oficial agregaría una autoridad deportiva sin una necesidad
de consulta que lo justifique en esta implementación.

### Comentarios y auditoría

Cassandra permite organizar la escritura y lectura por partido, usuario, actor
o recurso. Las vistas duplicadas resuelven consultas diferentes sin joins ni
escaneos globales. La flexibilidad de MongoDB no es el criterio dominante para
este historial; en Cassandra la contrapartida es definir las consultas antes
de las claves. No existe una copia automática de los comentarios en MongoDB.

### Telemetría

La dimensión temporal, las ventanas de 15 minutos y la retención justifican
InfluxDB. MongoDB conserva el evento deportivo y puede aportar sus referencias,
pero no recibe automáticamente cada muestra. El Data Mart extrae resúmenes
cuando se ejecuta su refresh; ese proceso no cambia el propietario de la serie.

### Relaciones

Los nodos de Neo4j comparten IDs con MongoDB. Los atributos necesarios para
recorrer o filtrar se proyectan explícitamente; no existe una vinculación
automática entre ambos motores. Un cambio en MongoDB no modifica por sí solo
todos los atributos de Neo4j. Outbox cubre la proyección de eventos oficiales;
la carga del catálogo tiene su propio procedimiento.

## CAP aplicado a las operaciones

CAP describe el compromiso entre consistencia y disponibilidad durante una
partición de red. No significa elegir dos propiedades permanentemente ni
clasificar todos los productos con una etiqueta sin considerar topología y
nivel de consistencia.

| Subsistema | Decisión ante falta de confirmación | Justificación |
|---|---|---|
| Hecho deportivo | Rechazar o reintentar si la autoridad no puede confirmar | Evitar resultados contradictorios o duplicados |
| Comentarios | Confirmar conforme al nivel de consistencia configurado | Priorizar escritura y lectura por partición dentro de garantías explícitas |
| Caché y proyecciones | Admitir retraso y consultar la autoridad cuando el flujo lo permite | La copia temporal no define el hecho oficial |
| Telemetría y analítica | Informar degradación de ese módulo | No inventar muestras o resultados para ocultar una dependencia caída |
| Auditoría oficial | Confirmar cambio y entrega durable juntos en MongoDB; publicar después en Cassandra | Evitar perder la intención de auditar por una caída del destino |

El laboratorio usa MongoDB de un miembro, Cassandra RF=1 y Redis standalone.
Estas configuraciones no demuestran comportamiento bajo partición entre réplicas.
Para un diseño Cassandra de tres réplicas, `LOCAL_QUORUM` exigiría dos respuestas
en el datacenter. Con RF=3, R=2 y W=2 se cumple R+W>N; esa condición de
intersección no sustituye por sí sola una garantía transaccional o linealizable.

## Criterio de rendimiento

La adecuación del modelo no equivale a un benchmark. La carga mixta registró
79,932 req/s de lectura en estrés con cero errores, pero no aisló la capacidad
máxima de cada motor ni midió una ráfaga de escrituras sociales. La comparación
del Data Mart fue favorable en una ejecución con pool y desfavorable en la
línea base sin pool; ambas se conservan. La selección se fundamenta en patrones
y garantías, con mediciones limitadas al escenario realmente ejecutado.

Resultados y límites: [estado de validación](../estado_validacion.md).

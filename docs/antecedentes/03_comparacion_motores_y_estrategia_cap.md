# Fixture 2030 — Comparación de motores y estrategia CAP

**Estado:** decisión revisada — IRIS excluido de la arquitectura objetivo  
**Versión:** 1.2  
**Fecha:** 30 de octubre de 2026  
**Documentos relacionados:** `alcance_funcional_fixture2030.md` y `02_patrones_acceso_y_requisitos_fixture2030.md`

---

## 1. Objetivo

Comparar los seis motores estudiados para cada necesidad de Fixture 2030 y asignar responsabilidades sin utilizar InterSystems IRIS en la arquitectura objetivo:

- MongoDB.
- Redis.
- Cassandra.
- InfluxDB.
- Neo4j.
- InterSystems IRIS, conservado únicamente como alternativa evaluada y descartada.

La comparación no busca que una sola tecnología resuelva todo. Para cada necesidad se distinguirá:

- **Fuente oficial:** conserva el dato durable y autoritativo.
- **Capa caliente:** responde lecturas o actualizaciones de muy baja latencia.
- **Proyección especializada:** copia preparada para una consulta particular.
- **Histórico o agregado:** conserva información procesada a largo plazo.

La exclusión de IRIS es una decisión aprobada por el grupo. Su columna permanece en la comparación para demostrar que fue evaluado, como exige la devolución del Hito 2, pero no será fuente, caché ni proyección de ninguna funcionalidad.

---

## 2. El volumen debe analizarse por picos

El promedio de comentarios de todo el torneo no representa el caso crítico. Una semifinal y, especialmente, una final pueden concentrar simultáneamente:

- Mayor cantidad de espectadores.
- Ráfagas de comentarios después de goles, penales o decisiones arbitrales.
- Muchas lecturas sobre la misma ventana temporal.
- Likes y reacciones concurrentes.
- Consultas constantes del timeline reciente.
- Moderación y rate limiting.

Por eso deben medirse al menos tres escenarios:

| Escenario | Propósito |
|---|---|
| Carga habitual | Validar el funcionamiento normal del torneo. |
| Semifinal | Probar varias veces el tráfico habitual. |
| Final | Probar el pico máximo, ráfagas y degradación controlada. |

Hasta conocer cifras de la cátedra no se inventará una capacidad productiva exacta. Se utilizará esta fórmula:

```text
comentarios_totales_pico = comentarios_por_segundo × duración_del_pico

almacenamiento_bruto = comentarios_totales_pico × tamaño_promedio

almacenamiento_replicado = almacenamiento_bruto × factor_de_replicación
```

La prueba de carga deberá ejecutarse, como mínimo, en niveles `1x`, `5x` y `10x` respecto de la carga académica definida.

---

## 3. Criterios de comparación

No se utilizará únicamente el volumen. Cada motor se analizará según:

| Criterio | Pregunta |
|---|---|
| Encaje del modelo | ¿La estructura natural del motor coincide con el dato? |
| Patrón de acceso | ¿Resuelve eficientemente las consultas dominantes? |
| Escritura y escalabilidad | ¿Soporta la frecuencia y los picos previstos? |
| Consistencia | ¿Ofrece la garantía que necesita la operación? |
| Disponibilidad y CAP | ¿Cómo responde ante una partición de red? |
| Durabilidad y recuperación | ¿Puede perderse una operación confirmada? |
| Distribución | ¿Permite particionar y replicar sin hotspots graves? |
| Operación | ¿Es fácil monitorear, respaldar y recuperar? |
| Ecosistema y profesionales | ¿Existen drivers, documentación y especialistas disponibles? |
| Complejidad | ¿Cuánto acoplamiento y sincronización agrega? |

### Escala cualitativa

| Puntaje | Interpretación |
|---:|---|
| 5 | Encaje natural como motor principal. |
| 4 | Alternativa fuerte o proyección muy útil. |
| 3 | Viable con trade-offs importantes. |
| 2 | Uso secundario o poco conveniente. |
| 1 | No corresponde al patrón principal. |

El puntaje indica encaje, no una decisión automática. Un motor con buen puntaje técnico puede descartarse como fuente principal por complejidad operativa, escasez de profesionales o dependencia tecnológica.

---

## 4. Perfil general de los seis motores

### 4.1 MongoDB

**Fortalezas**

- Documentos flexibles y agregados fáciles de comprender.
- Consultas e índices variados.
- Buen ajuste para catálogos, perfiles y metadatos.
- Ecosistema amplio y disponibilidad de profesionales.
- Replica sets y sharding disponibles.

**Debilidades**

- No es el modelo natural para series temporales masivas.
- Un documento creciente o una clave muy demandada puede generar hotspots.
- Las relaciones profundas requieren duplicación, consultas adicionales o una proyección.
- Puede resolver comentarios, pero necesita mayor cuidado para competir con un modelo diseñado por consulta bajo ráfagas extremas.

### 4.2 Redis

**Fortalezas**

- Latencia muy baja.
- TTL, sesiones, contadores, sorted sets y rate limiting.
- Excelente capa caliente y caché.
- Operaciones atómicas sobre estructuras en memoria.

**Debilidades**

- La memoria es costosa para conservar grandes históricos.
- Persistencia y replicación no lo convierten automáticamente en la mejor fuente oficial.
- Una caché puede perderse y debe poder reconstruirse.
- El particionado de una estructura muy caliente requiere atención.

### 4.3 Cassandra

**Fortalezas**

- Escrituras distribuidas y sostenidas.
- Arquitectura peer-to-peer sin un maestro único.
- Alta disponibilidad y consistencia configurable.
- Particiones y clustering diseñados desde consultas conocidas.
- Buen ajuste para timelines, comentarios, eventos append-only y auditoría.

**Debilidades**

- No permite consultas arbitrarias eficientes.
- Cada patrón dominante puede requerir una tabla o proyección propia.
- Una mala clave de partición produce hotspots o particiones gigantes.
- Operación, compaction, reparación y capacidad requieren conocimiento especializado.

### 4.4 InfluxDB

**Fortalezas**

- Series temporales, filtros por rango y agregaciones.
- Retención y downsampling.
- Buen ajuste para estadísticas y posiciones temporales.
- Consultas por tiempo y tags.

**Debilidades**

- No es una base general de usuarios, comentarios o fixture.
- Un evento semántico oficial no debe reducirse a una medición temporal.
- La cardinalidad de tags debe controlarse.
- Relaciones y reglas de dominio complejas no son su fortaleza.

### 4.5 Neo4j

**Fortalezas**

- Navegación de relaciones y consultas de múltiples saltos.
- Expresa con claridad equipos, jugadores, partidos, sedes y eventos relacionados.
- Útil para caminos, cruces, historial y exploración relacional.

**Debilidades**

- No es la primera elección para sesiones, comentarios masivos o series temporales.
- Las agregaciones temporales intensivas requieren otro modelo.
- Mantenerlo como proyección agrega sincronización.
- No debe utilizarse solo porque existan claves foráneas simples.

### 4.6 InterSystems IRIS — evaluado y descartado

**Fortalezas**

- Buen soporte para objetos de dominio, identidad, reglas y transacciones.
- Adecuado para un agregado estable como Partido.
- Permite concentrar estado, transiciones y validaciones.
- Ofrece acceso SQL y por objetos.

**Debilidades**

- Menor disponibilidad de profesionales que MongoDB, Redis o tecnologías más difundidas.
- Ecosistema y comunidad más acotados.
- Mayor dependencia del proveedor.
- No conviene extenderlo a todos los módulos solamente porque ya está implementado.

**Decisión**

No se utilizará IRIS. Aunque técnicamente puede resolver el agregado Partido, el grupo no acepta su menor disponibilidad de profesionales, su ecosistema más acotado ni la dependencia del proveedor. Sus antiguas responsabilidades se reasignan a MongoDB, Redis, Cassandra y Neo4j según el patrón de acceso.

---

## 5. Matriz comparativa completa

Los puntajes comparan el encaje como motor principal de la necesidad. Un puntaje bajo no impide que el motor se use como caché o proyección.

| Necesidad | MongoDB | Redis | Cassandra | InfluxDB | Neo4j | IRIS descartado | Propuesta principal |
|---|---:|---:|---:|---:|---:|---:|---|
| Equipos | 5 | 2 | 2 | 1 | 3 | 3 | MongoDB |
| Jugadores | 5 | 2 | 2 | 2 | 3 | 3 | MongoDB |
| Usuarios | 5 | 3 | 2 | 1 | 2 | 3 | MongoDB |
| Fixture | 5 | 2 | 2 | 1 | 4 | 5 | MongoDB; Neo4j como proyección justificada |
| Estado del partido | 5 | 4 | 2 | 2 | 3 | 5 | MongoDB oficial; Redis caliente |
| Alineaciones | 5 | 2 | 3 | 2 | 4 | 5 | MongoDB oficial; Neo4j opcional |
| Sustituciones | 5 | 4 | 4 | 3 | 4 | 4 | MongoDB oficial; Redis y Cassandra derivados |
| Eventos oficiales | 5 | 4 | 4 | 3 | 4 | 4 | MongoDB oficial; Redis caliente y Cassandra histórico |
| Sesiones | 3 | 5 | 2 | 1 | 1 | 2 | Redis |
| Comentarios | 3 | 3 | 5 | 1 | 2 | 2 | Cassandra; Redis de apoyo |
| Estadísticas de equipos | 2 | 3 | 4 | 5 | 1 | 2 | InfluxDB |
| Estadísticas de jugadores | 2 | 3 | 4 | 5 | 2 | 2 | InfluxDB |
| Mapas de calor | 2 | 2 | 3 | 5 | 2 | 1 | InfluxDB |
| Rankings en vivo | 3 | 5 | 3 | 4 | 2 | 2 | Redis derivado; reconstruible |
| Auditoría | 3 | 1 | 5 | 3 | 2 | 3 | Cassandra; archivo externo posterior |
| Multimedia — metadatos | 5 | 2 | 2 | 1 | 2 | 2 | MongoDB; archivos en object storage |

---

## 6. Comparación por necesidad

### 6.1 Equipos y jugadores

| Motor | Evaluación |
|---|---|
| MongoDB | Mejor encaje: documentos relativamente estables, atributos flexibles, búsquedas por equipo, posición o confederación e índices conocidos. |
| Redis | Útil para cachear fichas demandadas, pero no como fuente permanente. |
| Cassandra | Puede almacenar el catálogo si se conocen todas las consultas, pero agrega duplicación y rigidez innecesarias para solo 64 equipos y 1024 jugadores. |
| InfluxDB | Solo corresponde a estadísticas temporales de jugadores, no a su ficha maestra. |
| Neo4j | Útil como proyección para navegar jugador-equipo-partido-evento; no es necesario como fuente de atributos descriptivos. |
| IRIS | Técnicamente viable, pero descartado por riesgo operativo, ecosistema reducido y menor disponibilidad de profesionales. |

**Propuesta:** MongoDB como fuente del catálogo; Redis opcional como caché; Neo4j solo para consultas relacionales demostrables.

### 6.2 Usuarios

| Motor | Evaluación |
|---|---|
| MongoDB | Documentos flexibles para preferencias, idioma, equipo favorito y configuración. Ecosistema amplio. |
| Redis | Excelente para sesión y caché, pero el perfil no debe expirar con el TTL. |
| Cassandra | Escala, pero las consultas de perfil y modificaciones parciales no justifican el modelado por múltiples tablas. |
| InfluxDB | No corresponde a perfiles. |
| Neo4j | Solo tendría valor si se diseñaran relaciones sociales, algo fuera del alcance. |
| IRIS | Descartado globalmente; no aporta una ventaja suficiente frente a MongoDB. |

**Propuesta:** MongoDB para perfiles; Redis para sesiones.

### 6.3 Fixture, partidos y alineaciones

| Motor | Evaluación |
|---|---|
| MongoDB | Mejor alternativa seleccionada. Puede representar el agregado Partido con documentos, validaciones, índices y transacciones; su ecosistema reduce riesgo operativo. |
| Redis | Excelente para estado caliente y próximas fechas, pero insuficiente como única fuente oficial. |
| Cassandra | No es natural para transiciones de estado y reglas; requeriría tablas por cada consulta. |
| InfluxDB | Puede registrar evolución temporal, pero no gobierna el ciclo de vida del partido. |
| Neo4j | Excelente para navegar cruces y relaciones, pero no es necesario para reglas transaccionales simples del partido. |
| IRIS | Buen encaje conceptual, pero descartado por decisión arquitectónica y operativa. |

**Propuesta:** MongoDB como fuente oficial del bounded context Partido; Redis como lectura caliente; Neo4j solo si se confirman consultas de varios saltos.

**Diseño transaccional:** el partido, la alineación, la sustitución, el evento oficial que modifica el marcador y un registro `outbox` se escribirán en una transacción MongoDB. De esta manera no se confirma un gol sin actualizar coherentemente el marcador y dejar una orden durable para actualizar las proyecciones.

**Trade-off aceptado:** MongoDB no expresa cruces complejos tan naturalmente como un grafo. Se acepta porque permite concentrar las reglas oficiales en un motor conocido; Neo4j puede reconstruirse como proyección para navegación.

### 6.4 Sustituciones y eventos oficiales

| Motor | Evaluación |
|---|---|
| MongoDB | Buen encaje como fuente oficial si los eventos se guardan en una colección separada y la actualización del partido se realiza en una transacción. El timeline masivo se sirve mediante proyecciones. |
| Redis | Ideal para el timeline más reciente y el marcador visible; no debe ser el único registro durable. |
| Cassandra | Muy buen encaje para eventos append-only por partido y tiempo, idempotencia por identificador y disponibilidad distribuida. |
| InfluxDB | Útil para métricas derivadas del evento, no como registro semántico oficial. |
| Neo4j | Útil para consultas jugador-evento-partido-equipo, pero no como camino principal de ingesta. |
| IRIS | Descartado globalmente. |

**Propuesta:**

1. MongoDB valida el estado del partido y la idempotencia del comando.
2. Una transacción inserta el evento oficial, actualiza marcador o participación y agrega un registro `outbox`.
3. Un publicador procesa el `outbox` y actualiza Redis, Cassandra y las demás proyecciones.
4. Redis mantiene timeline y marcador calientes para la consulta masiva.
5. Cassandra conserva una proyección durable del timeline si las pruebas justifican esa lectura histórica distribuida.
6. InfluxDB recibe únicamente métricas numéricas derivadas.
7. Neo4j recibe una proyección relacional solo si existe una consulta concreta que la justifique.

**Trade-off:** las proyecciones no se actualizan dentro de la transacción oficial. Serán eventualmente consistentes y requerirán idempotencia, secuencia por partido, reintentos, cola de errores y reconciliación. El `outbox` evita la doble escritura no coordinada entre MongoDB y los demás motores.

### 6.5 Sesiones

| Motor | Evaluación |
|---|---|
| MongoDB | Puede almacenar sesiones, pero TTL y acceso intensivo son menos naturales que en Redis. |
| Redis | Encaje ideal: clave conocida, TTL, renovación y cierre inmediato. |
| Cassandra | Escala, pero no ofrece una ventaja suficiente para un dato efímero por clave. |
| InfluxDB | No corresponde. |
| Neo4j | No corresponde. |
| IRIS | Descartado globalmente. |

**Propuesta:** Redis. La pérdida de sesión obliga a reautenticar; nunca debe perderse el perfil permanente.

### 6.6 Comentarios

| Motor | Evaluación |
|---|---|
| MongoDB | Viable con sharding e índices. Es flexible, pero debe evitar documentos crecientes y un shard caliente por partido. |
| Redis | Excelente para timeline reciente, rate limiting, contadores y caché. Mantener todo el histórico en memoria es costoso y riesgoso. |
| Cassandra | Mejor encaje para escrituras intensas, timeline por clave conocida, replicación y disponibilidad. Exige una clave de partición diseñada para la final. |
| InfluxDB | El timestamp no convierte un comentario en serie temporal. No corresponde al contenido semántico y sus consultas. |
| Neo4j | Respuestas y menciones forman relaciones, pero no justifican un grafo para el flujo masivo principal. |
| IRIS | Descartado globalmente; tampoco ofrece ventaja para este patrón. |

**Propuesta:** Cassandra como fuente durable; Redis para caché reciente, rate limiting y contadores.

### 6.7 Estadísticas y mapas de calor

| Motor | Evaluación |
|---|---|
| MongoDB | Puede guardar snapshots, pero no es el modelo natural para ventanas y downsampling. |
| Redis | Excelente para último valor y ranking en vivo; no para todo el histórico detallado. |
| Cassandra | Buena ingesta por partido/jugador/tiempo, pero las agregaciones temporales requieren diseño y procesamiento adicional. |
| InfluxDB | Encaje natural para tiempo, rango, tags, retención, agregados y downsampling. |
| Neo4j | Puede relacionar jugadores y partidos, pero no almacenar eficientemente miles de coordenadas temporales. |
| IRIS | Descartado globalmente; no aporta una ventaja clara para series temporales. |

**Propuesta:** InfluxDB como fuente de las series; Redis para últimos valores o rankings; eventos oficiales como fuente de goles y asistencias.

### 6.8 Rankings

| Motor | Evaluación |
|---|---|
| MongoDB | Adecuado para guardar snapshots finales e históricos. |
| Redis | Sorted sets y operaciones atómicas lo hacen ideal para el ranking vivo. |
| Cassandra | Viable si se consulta por competencia y tipo, pero ordenar globalmente requiere modelado específico. |
| InfluxDB | Puede calcular rankings desde métricas agregadas, aunque no es la mejor capa de serving. |
| Neo4j | No aporta a un ranking simple. |
| IRIS | Descartado globalmente. |

**Propuesta:** ranking en vivo derivado en Redis; reconstrucción desde InfluxDB y eventos; snapshot histórico opcional en MongoDB.

### 6.9 Auditoría

| Motor | Evaluación |
|---|---|
| MongoDB | Viable para documentos de auditoría, pero necesita sharding y retención cuidadosa al crecer. |
| Redis | No debe ser histórico de auditoría. Puede guardar deduplicación temporal. |
| Cassandra | Encaje fuerte para append-only, consulta por servicio/recurso/tiempo y gran volumen. |
| InfluxDB | Bueno para métricas operativas, no necesariamente para estados anterior/posterior y contexto de negocio. |
| Neo4j | Útil para investigar redes complejas, pero no para la ingesta primaria. |
| IRIS | Descartado globalmente. |

**Propuesta:** Cassandra para auditoría reciente; almacenamiento externo de objetos para archivo histórico.

### 6.10 Multimedia

| Motor | Evaluación |
|---|---|
| MongoDB | Mejor opción para metadatos flexibles y asociaciones simples. |
| Redis | Caché de metadatos y URLs demandadas. |
| Cassandra | Viable a gran escala, pero innecesaria para el alcance actual. |
| InfluxDB | No corresponde. |
| Neo4j | Solo si las relaciones multimedia fueran el centro del producto. |
| IRIS | Descartado globalmente. |

**Propuesta:** MongoDB para metadatos; object storage para archivos; Redis/CDN como aceleración futura.

---

## 7. Caso crítico — Comentarios durante semifinales y final

### 7.1 Problema de la partición caliente

La clave académica anterior:

```text
(partido_id, bucket_10min)
```

es adecuada para una demostración, pero durante una final todos los comentarios de diez minutos pueden concentrarse en la misma partición lógica y en el mismo conjunto de réplicas.

Eso produce:

- Hotspot de escritura.
- Partición demasiado grande.
- Lecturas y escrituras compitiendo sobre las mismas réplicas.
- Latencia creciente en el momento de mayor tráfico.

### 7.2 Clave propuesta para el escenario objetivo

```text
partition_key = (partido_id, bucket_1min, shard)
clustering     = (creado_en DESC, comentario_id)

shard = hash(usuario_id) mod cantidad_de_shards
```

La cantidad de shards no debe fijarse sin prueba. Se pueden evaluar 4, 8 y 16.

**Ventaja:** distribuye el pico de una final entre varios rangos y réplicas.

**Costo:** para construir el timeline global, la API debe leer varios shards y fusionar los resultados por timestamp.

### 7.3 Segunda proyección por usuario

```text
partition_key = (usuario_id, bucket_dia)
clustering     = (creado_en DESC, comentario_id)
```

No se debe forzar la consulta por usuario sobre la tabla del partido. La duplicación se acepta porque responde a dos patrones de acceso diferentes.

### 7.4 Capa caliente en Redis

Redis puede encargarse de:

- Rate limiting por usuario y dirección.
- Contadores de comentarios y likes.
- Últimas páginas del timeline.
- Identificadores recientes ordenados.
- Deduplicación temporal.
- Protección frente a reintentos excesivos.

Redis no será la única copia del comentario confirmado.

### 7.5 Degradación durante la final

Ante saturación se aplicará este orden:

1. Mantener disponible el fixture, estado del partido y eventos oficiales.
2. Mantener lectura de comentarios recientes.
3. Aplicar límites de publicación por usuario.
4. Reducir frecuencia de actualización de contadores y likes.
5. Posponer proyecciones no críticas.
6. Rechazar exceso con `429 Too Many Requests`, no con errores genéricos.
7. Pasar comentarios a solo lectura si no existe un camino durable de escritura.

No se debe confirmar un comentario que haya quedado únicamente en Redis o en memoria de la API.

### 7.6 Aislamiento de recursos

Comentarios no deben compartir todos los recursos con eventos oficiales. Una avalancha social no puede impedir:

- Consultar el marcador.
- Recibir un gol.
- Registrar una sustitución.
- Procesar estadísticas.

Se definirán pools de conexión, límites y escalado separados.

---

## 8. Estrategia CAP preliminar

CAP se analiza durante una partición de red. No significa elegir una sola estrategia para toda la plataforma.

| Dominio | Prioridad durante partición | Consistencia | Comportamiento |
|---|---|---|---|
| Fixture y estado oficial | CP | Fuerte | Rechazar cambios si no se puede confirmar el estado más reciente. Puede mostrarse una copia marcada como desactualizada. |
| Alineaciones | CP | Fuerte | No confirmar una alineación si no puede persistirse de manera segura. |
| Sustituciones y eventos oficiales | CP al confirmar; proyecciones AP | Fuerte/causal en fuente, eventual en copias | El evento oficial no se confirma sin durabilidad; cachés y métricas convergen después. |
| Comentarios | AP | Eventual y de sesión | Priorizar publicación y lectura aun con réplicas temporalmente desactualizadas. Resolver convergencia posteriormente. |
| Estadísticas y mapas | AP | Eventual | Mostrar el último timestamp y completar/reprocesar datos al recuperarse. |
| Rankings | AP | Eventual | Servir la última versión y recalcular. |
| Catálogo | AP para lectura; CP para cambios maestros | Eventual en copias | Servir caché y suspender modificaciones si la fuente no está disponible. |
| Usuarios y roles | CP | Fuerte | No aceptar cambios de identidad o privilegios inconsistentes. |
| Sesiones protegidas | CP seguro | De sesión | Si no puede validarse, rechazar la operación protegida. |
| Auditoría | CP en durabilidad; escritura diferida segura | Causal por recurso | Conservar un registro pendiente durable y completar la proyección posteriormente. |
| Multimedia | AP | Eventual salvo derechos | La indisponibilidad del archivo no detiene el resto del sistema. |

### 8.1 MongoDB para operaciones oficiales

El replica set objetivo utilizará, como punto de partida:

```text
factor de replicación  = 3
writeConcern           = majority
readConcern oficial    = majority
readPreference oficial = primary
```

Consecuencias:

- Durante una partición, solo el lado con mayoría puede confirmar cambios oficiales.
- El lado minoritario no acepta goles, sustituciones, cambios de estado ni modificaciones de roles.
- Las lecturas públicas pueden continuar desde Redis con el último valor conocido y una marca temporal.
- Una operación oficial confirmada queda en una mayoría antes de responder al proveedor.
- La aplicación debe usar identificadores idempotentes y versión del agregado para impedir reintentos duplicados y escrituras perdidas.
- La caída del `primary` requiere elegir uno nuevo; durante ese intervalo se admite una pausa breve de escritura, no una confirmación insegura.

### 8.2 Cassandra para comentarios

Propuesta académica inicial:

```text
N = 3 réplicas
W = 1 réplica para confirmar escritura
R = 2 réplicas para lectura
```

Consecuencias:

- Una escritura puede continuar aunque dos réplicas no respondan inmediatamente.
- Una lectura consulta dos réplicas y tolera la caída de un nodo.
- `W + R = N`, no `W + R > N`; por lo tanto no se promete consistencia fuerte.
- Un comentario recién aceptado puede tardar brevemente en aparecer desde otra réplica.
- Como los comentarios son append-only y toleran consistencia eventual, el trade-off es aceptable.
- `R = 2` no maximiza la disponibilidad de lectura: en una partición de red aislada con un solo nodo, ese lado podría aceptar una escritura con `W = 1`, pero no responder una lectura que exige dos réplicas. Si se quisiera disponibilidad máxima de lectura se evaluaría `R = 1`, aceptando mayor probabilidad de leer datos atrasados.

Esta configuración debe validarse con pruebas. En producción se elegirían niveles locales según regiones, latencia y disponibilidad real.

### 8.3 Consistencia de sesión para comentarios

Aunque la plataforma sea eventual, el autor debería ver inmediatamente su propio comentario. Esto puede lograrse mediante:

- Respuesta de la API que incluya el comentario confirmado.
- Caché temporal del comentario del autor.
- Token o cursor que garantice no retroceder dentro de su sesión.

No hace falta imponer consistencia fuerte global para ofrecer una buena experiencia individual.

---

## 9. Mapa preliminar de responsabilidades

### 9.1 Roles de persistencia

No se utilizará la expresión genérica **motor de apoyo**, porque confunde responsabilidades diferentes:

| Rol | Significado | ¿Puede eliminarse y reconstruirse? | Ejemplo |
|---|---|---|---|
| Fuente de verdad durable | Copia autoritativa que decide cuál es el estado válido. Una confirmación implica persistencia y replicación. | No, salvo restauración desde backup o réplica. | Partido y evento oficial en MongoDB; comentario en Cassandra. |
| Fuente autoritativa temporal | El dato existe deliberadamente durante un período limitado. Mientras está vigente, esa base decide si es válido. | No se reconstruye necesariamente; su pérdida produce una consecuencia aceptada. | Sesión activa en Redis; si se pierde, el usuario vuelve a autenticarse. |
| Proyección durable derivada | Copia persistente optimizada para otra consulta, generada desde una fuente oficial. | Sí, mediante reprocesamiento. | Timeline histórico de eventos en Cassandra o navegación en Neo4j. |
| Capa caliente temporal | Copia en memoria para responder rápido, aplicar TTL, rate limiting o mantener últimos valores. | Sí. Nunca debe ser la única copia de un dato permanente. | Marcador, últimos eventos y comentarios recientes en Redis. |
| Archivo histórico | Conservación económica de largo plazo, no destinada a servir la operación en vivo. | Se restaura o reprocesa cuando sea necesario. | Auditoría antigua o archivos multimedia en object storage. |

Que Redis disponga de AOF o replicación no convierte automáticamente una caché en fuente histórica. La responsabilidad la define el diseño: los datos permanentes en Redis deben poder reconstruirse; las sesiones son la excepción porque son datos temporalmente autoritativos y su expiración es parte de la regla funcional.

### 9.2 Asignación por funcionalidad

| Funcionalidad | Fuente de verdad | Proyección durable o histórico | Capa temporal en memoria | Recuperación prevista |
|---|---|---|---|---|
| Equipos y jugadores | MongoDB | Neo4j, solo con consultas de grafo justificadas | Redis opcional | Recargar Redis/Neo4j desde MongoDB. |
| Usuarios | MongoDB | — | Redis para sesión y caché de perfil | Recargar caché; una sesión perdida exige reautenticación. |
| Fixture, partido y alineación | MongoDB | Neo4j para cruces y navegación justificada | Redis para estado y marcador visibles | Reconstruir Redis y Neo4j desde MongoDB y el `outbox`. |
| Sustituciones y eventos oficiales | MongoDB | Cassandra para timeline histórico; Neo4j e InfluxDB solo como derivados | Redis para eventos recientes | Reprocesar el `outbox` o releer eventos de MongoDB. |
| Sesiones | Redis como fuente autoritativa temporal | No requiere histórico completo | Redis | Expiración o pérdida obliga a iniciar una nueva sesión. |
| Comentarios | Cassandra | Tabla adicional por usuario; archivo futuro si se define | Redis para páginas recientes, rate limiting y contadores | Reconstruir Redis desde Cassandra. |
| Estadísticas | InfluxDB | Agregados de 15 minutos dentro de InfluxDB | Redis para último valor | Recalcular caché desde la serie o sus agregados. |
| Mapas de calor | InfluxDB | Celdas agregadas históricas | Redis opcional para el tramo en vivo | Recalcular desde posiciones retenidas; si expiraron, usar agregados. |
| Rankings | Derivables desde eventos y estadísticas | Snapshot histórico opcional en MongoDB | Redis para ranking en vivo | Recalcular desde MongoDB e InfluxDB. |
| Auditoría | Cassandra | Object storage para archivo | — | Restaurar archivo o consultar la ventana reciente en Cassandra. |
| Multimedia | MongoDB para metadatos; object storage para archivos | Archivo externo | Redis y CDN futura | Recargar caché desde MongoDB/object storage. |

---

## 10. Decisiones propuestas para aprobar

1. MongoDB será fuente de equipos, jugadores, usuarios y metadatos multimedia.
2. IRIS queda completamente excluido de la arquitectura objetivo.
3. MongoDB será fuente oficial de fixture, partido, alineaciones, sustituciones y eventos, usando transacciones y `outbox`.
4. Cassandra será fuente durable de comentarios y auditoría reciente, y podrá servir como proyección histórica de eventos.
5. Redis administrará sesiones y capas calientes, pero no será la fuente permanente de eventos o comentarios.
6. InfluxDB almacenará estadísticas temporales y mapas de calor.
7. Neo4j será una proyección, no una fuente universal; deberá justificarse con consultas de varios saltos.
8. Los rankings en vivo se mantendrán en Redis y podrán reconstruirse.
9. Los comentarios se diseñarán para el pico de semifinales y final, no para el promedio.
10. La partición objetivo de comentarios incorporará bucket temporal pequeño y shard.
11. La estrategia CAP se decidirá por dominio, no para toda la plataforma.

---

## 11. Decisiones todavía abiertas

- Determinar las consultas concretas que justifican Neo4j.
- Definir cantidad de shards para comentarios mediante pruebas de carga.
- Definir niveles de consistencia Cassandra definitivos.
- Definir regiones, datacenters y factor de replicación por entorno.
- Definir la implementación concreta del patrón `outbox` y el transporte de sus mensajes.
- Establecer RPO y RTO por dominio.
- Definir retención definitiva de comentarios y auditoría.
- Confirmar si el profesor acepta un proveedor de datos simulado.

---

## 12. Riesgos reconocidos

| Riesgo | Mitigación propuesta |
|---|---|
| Inconsistencia entre MongoDB y sus proyecciones | `Outbox` transaccional, idempotencia, secuencia, reintentos y reconciliación. |
| MongoDB como agregado oficial demasiado grande | Eventos en colección separada, documentos acotados, índices y límites explícitos. |
| Hotspot de comentarios en la final | Buckets pequeños, shards, rate limiting, caché y aislamiento de recursos. |
| Redis tratado como fuente permanente | Reconstrucción desde fuentes durables y políticas claras de TTL. |
| Neo4j sin preguntas reales de grafo | Exigir consultas de varios saltos antes de mantener la proyección. |
| Cardinalidad excesiva en InfluxDB | Elegir tags estables y evitar campos de alta cardinalidad innecesarios. |
| Documentación distinta de la implementación | Mantener frecuencia de 10 segundos y agregados de 15 minutos o actualizar ambos conjuntamente. |
| Afirmar escalabilidad no probada | Separar resultados locales de proyecciones y realizar pruebas `1x`, `5x` y `10x`. |

---

## 13. Próxima etapa

Después de aprobar o corregir este mapa se diseñará la arquitectura distribuida:

- Clústeres y nodos.
- Réplicas.
- Claves de partición.
- Consistencia de lectura y escritura.
- Regiones y zonas.
- Fallo de un nodo y de una región.
- Recuperación, backups, RPO y RTO.
- Sincronización entre motores.
- Reconstrucción de cachés y proyecciones.

El diagrama deberá permitir reconstruir visualmente las decisiones de CAP y el comportamiento ante fallos, tal como indicó el profesor en la devolución del Hito 3.

---

## 14. Historial de cambios

### Versión 1.0 — 30 de octubre de 2026

- Comparación de los seis motores para todas las necesidades.
- Incorporación del criterio operativo y de disponibilidad de profesionales.
- Propuesta de responsabilidades por fuente, capa caliente y proyección.
- Análisis especial del pico de comentarios en semifinales y final.
- Propuesta de bucketing y sharding para evitar una partición caliente.
- Estrategia CAP preliminar por dominio.
- Registro de riesgos, trade-offs y decisiones abiertas.

### Versión 1.1 — 30 de octubre de 2026

- Exclusión definitiva de InterSystems IRIS de la arquitectura objetivo.
- MongoDB adoptado como fuente oficial de fixture, partidos, alineaciones, sustituciones y eventos.
- Incorporación de transacciones MongoDB y patrón `outbox` para actualizar proyecciones.
- Redis definido como serving caliente y Cassandra como histórico distribuido opcional de eventos.
- Estrategia CAP inicial de MongoDB documentada con mayoría de tres réplicas.

### Versión 1.2 — 30 de octubre de 2026

- Reemplazo del concepto ambiguo `motor de apoyo` por roles explícitos de persistencia.
- Distinción entre fuente durable, fuente temporal, proyección durable, caché en memoria y archivo histórico.
- Documentación de la recuperación o reconstrucción prevista para cada funcionalidad.


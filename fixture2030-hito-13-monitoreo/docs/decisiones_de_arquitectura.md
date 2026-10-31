# Decisiones de arquitectura y análisis transversal (RF12, RF14, RF15)

Este documento reúne **por qué** el Fixture 2030 usa seis modelos NoSQL, qué costo tiene cada uno y qué mostró el monitoreo sobre el sistema construido. Cada afirmación lleva su fuente: un hito anterior, una medición del Hito 13 o, si no se midió, la palabra **propuesta**.

## 1. Por qué no una única estructura para todo el Fixture

El Fixture mezcla datos con patrones de acceso opuestos. Forzarlos a un solo modelo obliga a pagar, en cada consulta, el costo del modelo que no corresponde:

| Dato | Cómo se lee y se escribe | Qué haría mal un modelo único |
|---|---|---|
| Comentarios de un partido | Escritura masiva en ráfagas (gol), lectura de "los últimos N en esta ventana" | Un documental o relacional centralizado concentra las escrituras del pico en un solo primario |
| Relaciones partido–equipos–sede–eventos | Recorridos de varios saltos | En documental: referencias resueltas a mano en la aplicación; en relacional: varios JOIN por consulta |
| Sesiones | Lectura por clave, vencen solas | En cualquier otro motor, el vencimiento es una tarea de borrado periódica |
| Estadísticas cada 10 s | Ventanas de tiempo, agregación, retención | En documental o relacional: índices de tiempo y borrado manual de lo viejo |
| Equipos y jugadores | Perfil flexible, lectura por id y filtros | Un grafo o una serie temporal no aportan nada aquí |
| Partido con árbitro y eventos (objeto) | Navegación de objetos, herencia (Persona → Árbitro/Técnico) | En documental se pierde la integridad de la relación padre-hijo |

**Decisión:** persistencia políglota, con **una fuente de verdad por tipo de dato** y una API que integra. La comparación con un modelo relacional único, medida sobre el flujo del Hito 12, está en [`../../fixture2030-hito-12-carga-optimizacion/docs/comparacion_relacional.md`](../../fixture2030-hito-12-carga-optimizacion/docs/comparacion_relacional.md).

## 2. Cada base: problema, patrón, estructura, distribución y evidencia

| | MongoDB | Neo4j | Cassandra | Redis | InfluxDB 3 | IRIS |
|---|---|---|---|---|---|---|
| **Tipo de dato** | Equipos (64) y jugadores (1.024) | Partidos (96), sedes, equipos, eventos (192) | Comentarios por partido | Sesiones de usuario | Estadísticas de equipo cada 10 s | Partido + árbitro + eventos como objetos |
| **Consulta que motivó la elección** | "Dame el equipo X" / "jugadores del equipo X, paginados" | "Eventos del partido con sus equipos y sede" | "Últimos 20 comentarios del partido P en la ventana de 10 min B" | "¿Esta sesión sigue vigente?" | "Posesión de ARG entre 20:00 y 20:01" / resumen de 15 min | "Detalle del partido con su árbitro y eventos" |
| **Modelo** | Documental | Grafo de propiedades | Wide-column (particionado) | Clave-valor en memoria | Series temporales | Objetos persistentes (multimodelo) |
| **Estructura implementada** | Colecciones `equipos` y `jugadores` con `$jsonSchema`; índice `jugadores.equipo_id` | Nodos `Equipo`, `Jugador`, `Partido`, `Sede`, `Evento`; relaciones `PERTENECE_A`, `DISPUTA`, `SE_JUEGA_EN`, `OCURRE_EN`; unicidad por `codigo` | `comentarios_por_partido` con clave `((partido_id, bucket_10min), creado_en DESC, comentario_id)` + tabla por usuario | Hash `sesion:{id}` con `EXPIRE` (30 min) | Bases `fixture2030_detalle` (7 d) y `fixture2030_historico` (365 d); tags `partido_id`, `equipo_id` | Clases `Persona` → `Arbitro`/`Tecnico`, `Partido` 1-N `EventoPartido`, índice único `Codigo` |
| **Cómo carga / recupera** | `bulkWrite` con upsert / `find_one`, paginación por cursor | `MERGE` idempotente / un `MATCH` + `OPTIONAL MATCH` | `INSERT` (upsert) / una sola partición, `fetch_size` + `page_state` | `HSET` + `EXPIRE` / `HGETALL` + `TTL` en pipeline | line protocol / SQL con ventana y `LIMIT` | objetos `%Save()` / 3 SQL por Superserver con pool de 5 (Hito 12) |
| **Escala / distribución (laboratorio)** | 1 nodo | 1 nodo | 1 nodo, `SimpleStrategy` RF=1 | 1 nodo, `maxmemory 256mb`, `noeviction`, AOF | 1 nodo | 1 nodo, Community (8 conexiones) |
| **Escala / distribución (propuesta 2030)** | Replica set de 3; sharding innecesario (datos chicos y estables) | Cluster con réplicas de lectura; el grafo del torneo es chico | `NetworkTopologyStrategy`, 3 réplicas por región (Europa, África, Sudamérica); partición por `(partido, bucket)` | Redis con réplicas (Sentinel) o Cluster por hash de la clave | Retención por base; una instancia por región | Mirroring (primario + espejo) y licencia Enterprise |
| **Consistencia necesaria** | Fuerte en escritura (cambios de plantel poco frecuentes) | Fuerte (el resultado de un partido no puede diferir) | **Eventual** aceptable: un comentario puede aparecer 1 s más tarde | Fuerte por clave (una sesión cerrada no puede seguir válida) | Eventual aceptable para estadísticas en vivo | Fuerte (transacciones del objeto partido) |
| **Ante una falla** (medido: aislamiento) | Sus rutas devuelven 503; el resto sigue (Hito 11) | Ídem | Ídem | **Probado en el Hito 13:** 503 en sesiones, 0 errores en las otras 5 bases | Ídem | Ídem; el incidente real de IRIS solo afectó al detalle |
| **Trade-off que introduce** | Sin JOIN: el plantel completo se arma en la aplicación | Otro lenguaje (Cypher) y otro motor que operar | Hay que conocer la consulta **antes** de diseñar la tabla; tablas duplicadas por patrón | La memoria es el límite: con `noeviction`, al llenarse rechaza escrituras | Sin UPDATE natural; la retención borra el detalle a los 7 días | Licencia: 8 conexiones en Community (obligó al pool del Hito 12) |
| **Evidencia** | Hito 4: `explain` antes/después del índice; P95 interno ~5 ms (Hito 13) | Hito 5; P95 ~7-9 ms | Hito 6 (1.000.000 de filas); P95 ~24 ms, la más lenta del flujo | Hito 7; prueba de falla del Hito 13 | Hito 8: 1.080 puntos → 12 resúmenes; P95 ~15-20 ms | Hito 9; Hito 12: pool −84 % de tiempo de IRIS |

## 3. Distribución, consistencia y CAP (RF15)

**Laboratorio (medido):** cada base es **un solo nodo** en una notebook. No hay replicación ni particionamiento real entre máquinas, así que la tolerancia a fallos que se demostró es la de la **arquitectura de la API** (aislamiento por adaptador + corte rápido), no la de cada motor. Esto se dice explícitamente en la defensa.

**Propuesta para el Mundial 2030** (no medida). El torneo se juega en España, Portugal y Marruecos, con partidos inaugurales en Uruguay, Argentina y Paraguay: tres regiones con mucha distancia de red.

| Base | Ante una partición de red (CAP) | Qué se pierde o se retrasa si cae una región | Por qué es aceptable |
|---|---|---|---|
| Cassandra | **AP:** cada región sigue aceptando comentarios (`LOCAL_QUORUM`) y se reconcilia después | Los comentarios de la otra región llegan con retraso | Un comentario no es un dato crítico; perderlo es peor que verlo tarde |
| Redis | **CP por región:** sesiones locales a la región del usuario | Usuarios de la región caída deben volver a iniciar sesión | La sesión es efímera (TTL 30 min) |
| MongoDB | **CP:** el primario está en una región; las otras leen de secundarios | No se pueden **editar** planteles hasta elegir un nuevo primario (segundos) | Los planteles casi no cambian durante el torneo |
| Neo4j / IRIS | **CP:** el primario decide el resultado del partido | Escrituras de eventos frenadas hasta la recuperación | Un resultado inconsistente es inaceptable; mejor esperar |
| InfluxDB | Por región, sin replicación cruzada | Estadísticas en vivo de esa región; el histórico se regenera | Se pueden recalcular a partir del detalle |

**Qué parte de la respuesta puede ser eventual:** comentarios y estadísticas en vivo. **Qué no:** resultado y eventos del partido, sesiones cerradas.

## 4. Integración mediante la API

`Cliente → Ruta → Servicio → Adaptador → Base`. Cada base tiene su adaptador, su driver y su manejo de errores. Decisiones transversales que el monitoreo confirmó:

- **Aislamiento:** una base caída afecta solo a sus rutas. Medido en el Hito 11 (MongoDB) y en el Hito 13 (Redis, 3 veces): **0 errores** en las otras 5 bases.
- **Diagnóstico sin carga extra:** `/health/dependencias` (Hito 11) cachea el resultado 15 s; Prometheus lee ese resultado sin multiplicar los pings.
- **Contrato de errores uniforme:** 503 = base no disponible; el monitoreo cuenta 5xx sin mirar el cuerpo.
- **Cómo se evita que una consulta de alto volumen bloquee todo:** las consultas están acotadas por diseño (una partición de Cassandra, `LIMIT` en InfluxDB y Cassandra, paginación por cursor en MongoDB, búsqueda por índice único en IRIS); cada driver tiene timeout; y desde este hito el **corte rápido** impide que una base caída ocupe los hilos de la API.

## 5. Cómo se distingue si el problema está en la API o en la base

| Señal en el dashboard | Interpretación |
|---|---|
| Sube el P95 de **todas** las bases a la vez y la CPU del proceso de la API está alta | El límite es la API (un solo proceso uvicorn). Es lo que pasó en el Hito 12 con 80 usuarios |
| Sube el P95 de **una** base y su ping (`fixture_dependencia_chequeo_segundos`) también sube | El motor está lento |
| Sube el P95 de una base pero su ping sigue bajo | La consulta es pesada (no el motor): revisar la estructura de esa consulta |
| `probe_success` = 0 y `fixture_dependencia_up` = 0 | La base o su contenedor están caídos (infraestructura) |
| `probe_success` = 1 y `fixture_dependencia_up` = 0 | La base escucha pero no se puede usar: credenciales, namespace o motor que no terminó de arrancar (incidente de IRIS) |
| Errores 5xx en una sola base | Problema de esa dependencia; el resto sigue |
| Errores 5xx en todas | Problema de la API |
| **Primera métrica a mirar ante un aumento de latencia:** "Latencia P95 por base" → identifica el motor; después "CPU del proceso de la API" → separa API de base | |

## 6. Mejora transversal: corte rápido por base (RF12)

### Evidencia que la motivó

En la primera prueba controlada (sin corte rápido) se detuvo Redis durante 120 s. Las otras 5 bases respondieron sin errores, **pero el throughput total cayó de 133 a 47 req/s (−65 %)** y el P95 global de la API subió de 21 ms a ~2 s.

El panel "Latencia P95 por base" mostró la causa: las rutas de Redis tardaban **2,4-2,8 s en devolver el 503**. En Windows, conectarse a un puerto local cerrado tarda ~2 s en fallar (la pila TCP reintenta antes de aceptar el rechazo). Cada solicitud de sesión ocupaba un hilo de la API y a un usuario durante ese tiempo. Una base caída degradaba a todas: el aislamiento era funcional (sin errores) pero **no de rendimiento**.

### Cambio

[`app/services/corte_rapido.py`](../../app/services/corte_rapido.py). Cuando un adaptador falla por indisponibilidad o timeout, durante `CORTE_RAPIDO_SEGUNDOS` (10 s) las solicitudes a **esa** base responden 503 al instante, sin intentar conectarse (circuito "abierto"). Al vencer la ventana, una solicitud prueba de nuevo: si funciona, el circuito se cierra. El ping del diagnóstico de salud también lo cierra apenas la base responde. El contrato HTTP no cambia y con `CORTE_RAPIDO_SEGUNDOS=0` el comportamiento es el anterior.

- **v1:** al vencer la ventana dejaba pasar a todas las solicitudes que llegaban, y cada una volvía a esperar ~2,4 s. El monitoreo lo mostró: P95 de Redis 1,6 s (captura `09_grafana_latencia_corte_v1.png`).
- **v2 (adoptada):** al vencer la ventana pasa **una sola** solicitud de prueba; las demás siguen rechazadas hasta conocer el resultado.

### Resultado medido (mismo escenario, tres corridas)

| Durante la falla de Redis | Sin corte | Corte v1 | **Corte v2** |
|---|---:|---:|---:|
| Throughput total | 47 req/s | 115 req/s | **138 req/s** (igual que sin falla) |
| P95 máximo de las rutas de Redis | 2.812 ms | 1.592 ms | **4,9 ms** |
| Errores en las otras 5 bases | 0 | 0 | 0 |
| Datos intactos antes/después | 6/6 | 6/6 | 6/6 |

Detalle, commits y gráfico: [`../evidencia/comparacion_corte_rapido.md`](../evidencia/comparacion_corte_rapido.md). Pruebas automáticas: `tests/unit/test_corte_rapido.py`.

### Trade-offs

- Tras recuperarse la base, la API puede tardar hasta una ventana (10 s) en volver a usarla. Medido: 6-14 s después del `docker start`. Para sesiones es aceptable; para una base crítica se usaría una ventana menor.
- Las solicitudes rechazadas durante la ventana podrían haber funcionado si la base volvió antes. Es el costo de no castigar a todos los usuarios.
- Es por instancia de la API: con varias instancias, cada una aprende la falla por su cuenta.

## 7. Otras mejoras transversales analizadas

| Mejora | Área | Estado | Evidencia o razón |
|---|---|---|---|
| Pool de conexiones de IRIS (5) | Conexiones | **Adoptada en el Hito 12**; el Hito 13 la monitorea | −84 % de tiempo de IRIS. Hoy usa el 13 % de licencias (gauge de IRIS) |
| Corte rápido por base | API / resiliencia | **Adoptada en este hito** | Sección 6 |
| Varios procesos de la API (`uvicorn --workers N`) | API / carga | **Propuesta** | Con un solo proceso, la API es el primer límite (Hito 12: 70-86 % de CPU). Costo: cada proceso tiene su pool de IRIS (5 × N ≤ 8 licencias) y su propio corte rápido |
| Exporter JMX para Cassandra | Observabilidad | **Propuesta** | Hoy Cassandra solo se ve "desde afuera" y es la base más lenta del flujo (P95 ~24 ms) |
| Réplicas de lectura para Neo4j y MongoDB | Réplica | **Propuesta** | Lecturas dominantes en el flujo; sin medir en el laboratorio |
| Caché en Redis del detalle del partido | Caché | **Descartada por ahora** | IRIS ya responde en ~7 ms con el pool; agregaría invalidación sin beneficio medido |
| Data Mart para la pregunta analítica | Analítica | Prototipo del Hito 12 | 8,7 s → 0,57 ms; no se monta en la operación en vivo |

## 8. Operacional vs. analítico, y caché

- **Operacional:** las seis bases atienden el partido en vivo (lecturas por clave, ventanas acotadas).
- **Analítico:** preguntas que cruzan bases ("¿en qué ventanas de 10 min se concentran los comentarios y qué eventos ocurrieron?") se proyectan a un Data Mart (Hito 12) y no se calculan contra las bases operacionales.
- **Caché:** Redis guarda sesiones con TTL de 30 min: se invalidan solas al vencer o con `DELETE /sesiones/{id}` (cierre). `noeviction` garantiza que la presión de memoria nunca borre una sesión vigente. La alerta `RedisMemoriaCercaDelLimite` vigila el costo de esa decisión.

## 9. Costo operativo de mantener seis productos

| Costo | Cómo se ve en este proyecto | Cómo se mitiga |
|---|---|---|
| Seis motores que instalar, actualizar y respaldar | Seis compose distintos; volúmenes en dos lugares (WSL y Docker) | `entorno-local/` (Hito 11) los unifica; scripts idempotentes |
| Seis formas de monitorear | Exporter en dos, métricas nativas en dos, **nada interno** en Neo4j y Cassandra | Capa común: sondas TCP + métricas de la API, iguales para las seis |
| Fallas de entorno que no son del código | **Incidente real de IRIS:** arrancó sin su carpeta de datos (ver limitaciones) | `iniciar_monitoreo.ps1` despierta WSL y reinicia bases `unhealthy` |
| Seis lenguajes de consulta | MQL, Cypher, CQL, comandos Redis, SQL de InfluxDB, SQL/ObjectScript de IRIS | La API los encapsula; el front y Swagger ven un solo contrato |
| Sin transacciones entre bases | Un evento en Neo4j y su comentario en Cassandra no se confirman juntos | Cada dato tiene una sola fuente de verdad; el Data Mart detecta inconsistencias (Hito 12) |

**Conclusión:** el costo es real y se paga en operación y en monitoreo. Se justifica porque cada base resuelve un patrón que en un modelo único sería caro (sección 1), y porque la API más el monitoreo limitan el impacto de una falla a la porción del Fixture que depende de esa base.

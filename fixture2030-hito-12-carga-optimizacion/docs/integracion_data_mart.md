# Integración analítica: propuesta de Data Mart (RF12, RF13, RNF12, punto 5.7)

Además de la propuesta, se construyó un **prototipo funcional y medido** (`scripts/construir_data_mart.py` y `scripts/consultar_data_mart.py`). El enunciado no exige construirlo; se hizo para medir la diferencia entre consultar las fuentes operacionales y consultar la proyección, en lugar de solo afirmarla.

## 1. Pregunta analítica

> **¿En qué ventanas de 10 minutos de cada partido se concentra la actividad de los hinchas (comentarios, likes, moderación) y qué eventos del partido (goles, tarjetas) ocurrieron en esas ventanas?**

Usuarios de la respuesta: el equipo de análisis (tablero postpartido, "momentos calientes" del torneo) y el equipo de operación, para dimensionar recursos en partidos parecidos. Es un caso típico de Big Data del Fixture: combina el dato masivo (comentarios) con el dato de dominio (eventos) y no tiene sentido resolverlo en cada request de usuario.

Preguntas derivadas que responde la misma estructura: top de ventanas del torneo, evolución minuto a minuto de un partido, actividad promedio después de un gol frente a ventanas sin eventos, comparación por fase o sede.

## 2. Fuentes operacionales y qué aporta cada una

| Fuente | Dato operacional | Qué se proyecta | Se incluye | Precaución |
|---|---|---|---|---|
| **Cassandra** (`comentarios_por_partido`) | Comentarios por `(partido_id, bucket_10min)` | Conteo de comentarios, visibles, pendientes de moderación y suma de likes por ventana | Sí | No leer todo el histórico en cada carga: se lee por partición conocida |
| **Neo4j** | `(:Partido)-[:DISPUTA]->(:Equipo)`, `-[:SE_JUEGA_EN]->(:Sede)`, `(:Evento)-[:OCURRE_EN]->(:Partido)` | Dimensión partido (fecha, fase, sede, equipos) y eventos por ventana (por `minuto`) | Sí | Al aplanar la relación evento→partido se pierde el recorrido; se conservan los tipos de evento |
| **MongoDB** (`equipos`) | Atributos flexibles del equipo | Confederación y ranking en la dimensión equipo | Sí | El nombre no coincide con Neo4j (ver sección 7) |
| **InfluxDB** (`estadisticas_equipo`) | Posesión, pases, tiros cada 10 s | Hecho secundario agregado a 10 min (promedio de posesión, suma de pases, máx. de tiros) | Sí, separado | Usa otro código de equipo (`ARG`, `MEX`) y otro horario |
| **Redis** | Sesiones con TTL | — | **No** | Es estado efímero: expira (TTL), no permite reconstruir históricos. Para medir audiencia habría que emitir eventos de sesión a un log persistente |
| **IRIS** | Detalle del partido como objeto (árbitro, eventos) | — | **No en el prototipo** | Solo tiene `PAR-DEMO` y los partidos sintéticos `PAR-H12*`, sin correspondencia con los 96 de Neo4j. En producción aportaría el árbitro y la hora exacta de inicio (`FechaHora`) |

## 3. Modelo dimensional y grano

```text
dim_equipo (equipo_id PK, nombre, nombre_mongodb, conflicto_nombre, confederacion, ranking, lote_id)
      ▲  ▲
      │  └───────────────┐
dim_partido (partido_id PK, fecha_neo4j, dia_actividad, fase, sede, equipo_a_id FK, equipo_b_id FK, lote_id)
      ▲
      │
fact_actividad_ventana                                  ← HECHO PRINCIPAL
  PK (partido_id, ventana)                              grano: 1 fila = 1 partido × 1 ventana de 10 min
  bucket_10min        (clave de origen en Cassandra → procedencia)
  comentarios, comentarios_visibles, comentarios_pendientes, likes      (Cassandra)
  eventos, goles, tarjetas, tipos_evento                                (Neo4j)
  fuentes, lote_id

fact_estadistica_ventana                                ← HECHO SECUNDARIO
  PK (partido_id, ventana_inicio, equipo_fuente)        grano: partido × ventana de 10 min × equipo
  posesion_promedio, pases, tiros_max, muestras, equipo_conciliado, fuentes, lote_id   (InfluxDB)

control_lotes (lote_id PK, inicio, fin, estado, conteos_fuente, conteos_destino, validaciones, duracion_s)
```

- **Grano** del hecho principal: una fila por partido y ventana de 10 minutos. Coincide con el bucket de Cassandra (no hay que partir particiones) y es lo bastante fino para ver el "momento" de un gol.
- **Medidas aditivas:** comentarios, likes, eventos, goles, tarjetas (se pueden sumar por partido, fase o torneo). **No aditivas:** `posesion_promedio`, que se promedia y no se suma, y `tiros_max`, que es un máximo.
- **Ventanas:** 15 por partido (0 a 14, de 18:00 a 20:30): 120 minutos de actividad más 30 de margen para alargue y datos tardíos. Estadísticas de InfluxDB se guardan aparte porque su eje temporal no coincide (sección 7).

## 4. Transformaciones y claves de unión

| Paso | Transformación |
|---|---|
| Partido → ventana | `bucket_10min` de Cassandra = día de actividad + `18:00 + 10 × ventana`, con la regla del generador del Hito 6 (8 partidos por día) |
| Evento → ventana | `ventana = min(minuto // 10, 14)`. **Supuesto:** el minuto 0 del partido coincide con el inicio de la ventana de actividad (18:00). Ver sección 7 |
| Tipos de evento | `Gol` y `Penal` → `goles`; `Tarjeta amarilla` y `Tarjeta roja` → `tarjetas`; el resto cuenta en `eventos` |
| Comentarios | conteo total, conteo por `estado_moderacion` (`visible` / `pendiente`), suma de `likes` (nulos = 0) |
| Equipo | clave común `EQ-01…EQ-64` entre Neo4j y MongoDB. Nombre: **fuente de verdad Neo4j**; el de MongoDB se conserva en `nombre_mongodb` y se marca `conflicto_nombre` |
| Estadísticas | `date_bin(10 minutes)` en InfluxDB (la agregación la hace el motor de series temporales); `equipo_conciliado = 1` si las 3 primeras letras del código coinciden con un equipo del partido en Neo4j (regla heurística) |

## 5. Flujo de extracción, transformación y carga (RF13)

| Aspecto | Prototipo (medido) | Propuesta para producción |
|---|---|---|
| Tipo | ETL por lotes: extraer → transformar en Python → cargar en SQLite | ETL incremental por ventana cerrada |
| Origen | Drivers nativos directo a las bases, **no** a través de la API operacional (no compite con los usuarios por la API, que es el cuello medido) | Idem, idealmente desde réplicas de lectura o un log de eventos de la API |
| Frecuencia | A demanda (`construir_data_mart.py`), ~3,9 s por lote completo | Cada 10 minutos durante los partidos (al cerrar cada bucket) + recarga completa nocturna |
| Retraso aceptable | Antigüedad del último lote (`control_lotes.fin`) | **12 minutos**: la ventana de 10 min + 2 min de espera para datos tardíos. Para un tablero postpartido es suficiente; para "en vivo" se usaría la API operacional |
| Marca de agua / checkpoint | No hace falta: recarga completa | Último `bucket_10min` cerrado y publicado por partido, guardado en `control_lotes` |
| Idempotencia | Recarga completa dentro de **una transacción** con `lote_id`; volver a correr reemplaza todo | `INSERT … ON CONFLICT (partido_id, ventana) DO UPDATE`: recargar una ventana no duplica, la reemplaza |
| Duplicados | Imposibles por la PK `(partido_id, ventana)`; además en la fuente el comentario tiene clave `(creado_en, comentario_id)` y Cassandra hace upsert | Igual. Reintentos de la API que reescriban el mismo comentario no cambian el conteo |
| Datos tardíos | Se cubren con 30 min de margen (ventanas 12 a 14) | Una ventana ya publicada se **reprocesa** si llegan comentarios con `creado_en` dentro de ella hasta 2 h después del partido; pasado eso, se registra la corrección en `control_lotes` |
| Datos faltantes | Una ventana sin comentarios se carga con 0 (es un dato válido: no hubo actividad). Una fuente caída aborta el lote (Neo4j, MongoDB, Cassandra) o lo publica marcado sin estadísticas (InfluxDB) | Igual, con alerta |
| Falla parcial | Si algo falla a mitad de la carga, la transacción hace **rollback**: el Data Mart sigue mostrando el lote anterior completo, nunca uno a medias | Por ventana: o se publica completa o no se publica |
| Validación | Antes de publicar: comentarios fuente = destino, eventos fuente = destino, exactamente 1 fila por partido y ventana, sin hechos huérfanos. Si falla, **no se publica** | Igual + umbrales de variación contra el lote anterior |

## 6. Procedencia (RNF12)

Cada fila del Data Mart responde las cuatro preguntas de la Clase 13:

| Pregunta | Dónde está |
|---|---|
| ¿De qué fuente provino? | Columna `fuentes` (`cassandra+neo4j`, `influxdb`) y `bucket_10min` (clave exacta de origen en Cassandra) |
| ¿Cuándo se extrajo? | `control_lotes.inicio` / `fin` del `lote_id` de la fila |
| ¿Con qué transformación? | Este documento (sección 4) y el código versionado de `construir_data_mart.py` (commit) |
| ¿Qué lote la produjo? | Columna `lote_id` en todas las tablas |

## 7. Resultado de la construcción (medido, lote `DM-20261024-203358-5374c1`)

| Conteo | Fuente | Data Mart |
|---|---:|---:|
| Comentarios | 28.809 (1.440 particiones de Cassandra) | 28.809 |
| Eventos | 192 (Neo4j) | 192 (96 goles, 96 tarjetas) |
| Partidos | 96 | 96 |
| Equipos | 64 | 64 |
| Filas del hecho principal | — | 1.440 (= 96 × 15), 0 duplicadas, 0 huérfanas |
| Estadísticas | 18 filas agregadas (InfluxDB) | 18 |

Las cuatro validaciones dieron OK y el lote se publicó en **3,9 s**.

**Problemas de calidad detectados por la integración** (se registran, no se ocultan):

| Observación | Cantidad | Tratamiento |
|---|---:|---|
| Equipos con nombre distinto en Neo4j y MongoDB (`Argentina` vs. `Equipo 01`) | 64 de 64 | Neo4j como fuente de verdad del nombre; MongoDB se conserva para auditoría |
| Partidos cuya `fecha` en Neo4j (todas `2030-06-13`) no coincide con el día de sus comentarios en Cassandra (regla de 8 partidos por día) | 92 de 96 | Se guardan las dos (`fecha_neo4j`, `dia_actividad`); hace falta una fuente de verdad del calendario |
| Filas de InfluxDB cuyo equipo no pertenece al partido según Neo4j (PAR-0001 es Argentina–Países Bajos en Neo4j y ARG–MEX en InfluxDB) | 9 de 18 | Se marcan `equipo_conciliado = 0` y no se cruzan con la dimensión equipo |
| Horario: InfluxDB registra PAR-0001 de 20:00 a 21:30, Cassandra concentra la actividad de 18:00 a 20:00 | — | Las estadísticas quedan en un hecho separado con su propia hora; no se fuerzan a la ventana de comentarios |

Estas inconsistencias vienen de que cada hito generó sus datos de prueba por separado. Es exactamente el riesgo "Conflicto: dos fuentes informan atributos diferentes" de la Clase 13, y muestra por qué un Data Mart necesita reglas de fuente de verdad y no puede ser una copia sin dueño.

## 8. Fuentes operacionales vs. proyección analítica (medido)

`scripts/consultar_data_mart.py` responde la misma pregunta (top 10 de ventanas del torneo + evolución de PAR-0001) por dos caminos, con la API levantada y sin carga (24/10/2026, `docs/evidencia/data_mart_comparacion.json`):

| | Camino operacional | Camino Data Mart |
|---|---|---|
| Cómo | Por cada partido: 15 `GET /comentarios` (uno por bucket, paginando) + 1 `GET /eventos`; agregación en el cliente | 2 consultas SQL con `JOIN` sobre `fact_actividad_ventana` y `dim_partido` |
| Solicitudes | **1.536 llamadas HTTP** a la API (que a su vez consultan Cassandra y Neo4j) | 2 consultas locales |
| Tiempo (mediana) | **8.723 ms** (3 repeticiones: 8.822 / 8.723 / 8.666 ms) con 8 llamadas en paralelo | **0,574 ms** (P95 0,739 ms, 50 repeticiones) |
| Respuesta | top 10 + 15 ventanas de PAR-0001 | **idéntica** (comparada fila por fila) |
| Frescura | al instante | la del último lote (en producción, ≤ 12 min) |
| Carga sobre el sistema operacional | 1.536 solicitudes sobre la API, que ya es el cuello de botella medido | ninguna al consultar; un lote cada 10 min que lee directo de las bases |

La proyección responde unas **15.000 veces más rápido** y no consume la API. El costo es el retraso controlado y el proceso de carga. La coincidencia exacta de las dos respuestas es la validación de **consistencia entre fuente operacional y proyección** que pide el punto 5.8.

Ejemplo de respuesta (top 3): `PAR-0094` ventana 3 (minutos 30–39) 25 comentarios / 921 likes / 1 evento; `PAR-0093` ventana 3, 820 likes, 1 evento; `PAR-0002` ventana 2, 819 likes, 1 evento.

> Con los datos sintéticos todas las ventanas tienen 25 comentarios, así que el orden lo deciden los likes. Con datos reales la distribución sería desigual y la pregunta más interesante. El objetivo del prototipo es la integración y la medición, no el análisis en sí.

## 9. Por qué no consultar las seis bases en cada request

Hacerlo convertiría cada vista del tablero en 1.500 llamadas encadenadas a la parte del sistema que ya demostró ser el límite (la API al 82–98 % de CPU en el pico). Con 100 analistas mirando el tablero a la vez serían 150.000 solicitudes extra, compitiendo con los hinchas. La proyección separa el camino analítico del operacional, que es la recomendación de la Clase 13 ("el antipatrón de la consulta universal").

# Comparación con una estructura relacional (RF14, punto 5.6)

La comparación está **atada al flujo probado** ("consulta del partido en vivo", 6 lecturas) y a la **pregunta analítica** del Data Mart. Se separa lo **medido** (sección 6) de lo **conceptual** (secciones 1 a 5).

## 1. Unidad de información en un modelo relacional

| Hoy (NoSQL, por producto) | Unidad equivalente en relacional |
|---|---|
| Documento `equipo` (MongoDB) | Fila de `equipo` |
| Nodos `Partido`, `Equipo`, `Sede`, `Evento` y sus relaciones (Neo4j) | Filas de `partido`, `sede`, `evento` + claves foráneas |
| Fila de `comentarios_por_partido` en la partición `(partido, bucket)` (Cassandra) | Fila de `comentario` |
| Hash `sesion:{id}` con TTL (Redis) | Fila de `sesion` con columna `expira_en` |
| Punto `estadisticas_equipo` cada 10 s (InfluxDB) | Fila de `estadistica` con `(partido, equipo, ts)` |
| Objeto `Fixture.Partido` con hijos `EventoPartido` (IRIS) | `partido` + `evento` + `arbitro` |

## 2. Esquema relacional que reemplazaría al flujo

```sql
CREATE TABLE equipo  (equipo_id CHAR(5) PRIMARY KEY, nombre TEXT NOT NULL, confederacion TEXT, ranking INT);
CREATE TABLE sede    (sede_id   CHAR(6) PRIMARY KEY, nombre TEXT NOT NULL);
CREATE TABLE arbitro (arbitro_id INT PRIMARY KEY, documento TEXT UNIQUE, nombre TEXT, nacionalidad TEXT, licencia_fifa BOOL);
CREATE TABLE partido (
  partido_id CHAR(8) PRIMARY KEY, fecha_hora TIMESTAMP NOT NULL, fase TEXT, estado TEXT,
  sede_id CHAR(6) REFERENCES sede, arbitro_id INT REFERENCES arbitro,
  equipo_local CHAR(5) REFERENCES equipo, equipo_visitante CHAR(5) REFERENCES equipo,
  CHECK (equipo_local <> equipo_visitante));
CREATE TABLE evento (
  evento_id TEXT PRIMARY KEY, partido_id CHAR(8) NOT NULL REFERENCES partido,
  minuto SMALLINT CHECK (minuto BETWEEN 0 AND 130), tipo TEXT NOT NULL, detalle TEXT);
CREATE INDEX ix_evento_partido ON evento (partido_id, minuto);
CREATE TABLE comentario (
  comentario_id UUID, partido_id CHAR(8) NOT NULL REFERENCES partido, creado_en TIMESTAMP NOT NULL,
  usuario_id TEXT NOT NULL, contenido TEXT, estado_moderacion TEXT, likes INT DEFAULT 0,
  PRIMARY KEY (partido_id, creado_en, comentario_id)
) PARTITION BY RANGE (creado_en);                         -- una partición por día de torneo
CREATE TABLE sesion (sesion_id TEXT PRIMARY KEY, usuario_id TEXT, rol TEXT, partido_actual CHAR(8),
  acciones INT, ultimo_acceso TIMESTAMP, expira_en TIMESTAMP NOT NULL);
CREATE INDEX ix_sesion_expira ON sesion (expira_en);      -- para el borrado periódico
CREATE TABLE estadistica (partido_id CHAR(8) REFERENCES partido, equipo_id CHAR(5) REFERENCES equipo,
  ts TIMESTAMP, posesion_pct NUMERIC(5,2), pases INT, tiros INT,
  PRIMARY KEY (partido_id, equipo_id, ts)) PARTITION BY RANGE (ts);
```

## 3. Operaciones del flujo en la alternativa relacional

| Endpoint | Hoy | Relacional |
|---|---|---|
| Equipo | `find_one({_id})` en MongoDB | `SELECT … FROM equipo WHERE equipo_id = $1` (PK) |
| Eventos | Recorrido Cypher partido → equipos, sede, eventos | 1 consulta con `JOIN partido, equipo ×2, sede` + `evento WHERE partido_id = $1 ORDER BY minuto` |
| Comentarios | 1 partición `(partido, bucket)`, paginación con `page_state` | `WHERE partido_id = $1 AND creado_en >= $2 AND creado_en < $2 + 10 min ORDER BY creado_en DESC LIMIT 20` con paginación por cursor `(creado_en, comentario_id)` |
| Sesión | `HGETALL` + `TTL` | `SELECT … WHERE sesion_id = $1 AND expira_en > now()` + tarea que borre las vencidas |
| Estadísticas | SQL de InfluxDB sobre la ventana | `WHERE partido_id = $1 AND equipo_id = $2 AND ts BETWEEN …` sobre la partición del día |
| Detalle | 3 consultas SQL a IRIS **con conexión nueva por solicitud** (antes del pool) | 1 consulta con `JOIN partido-arbitro` + eventos, **desde un pool** del único motor |

## 4. Garantías esperadas

- **ACID en un solo motor:** un partido, sus eventos y sus comentarios pueden escribirse en una transacción. Hoy, si Neo4j confirma un evento y Cassandra falla, no hay transacción que abarque los dos.
- **Integridad referencial:** las claves foráneas habrían **impedido** los problemas que encontró el Data Mart: un equipo con dos nombres distintos según la fuente, o estadísticas de "MEX" en un partido que según el grafo es Argentina–Países Bajos.
- **Consistencia fuerte en lecturas** del primario; en réplicas de lectura, consistencia eventual (retraso de replicación).
- Cassandra con `CONSISTENCY ONE` (como en el Hito 6) prioriza disponibilidad y velocidad de escritura sobre consistencia: un relacional ofrece lo contrario por defecto.

## 5. Cómo crecería y qué parte sería más simple o más compleja

| Aspecto | Más simple en relacional | Más complejo en relacional |
|---|---|---|
| Operación | Un solo motor, un solo driver, **un solo pool** (hoy son 6 drivers y 6 configuraciones de conexión) | — |
| Consultas que cruzan entidades | Un `JOIN` en lugar de pedir a 2–3 bases y unir en la API | — |
| Comentarios masivos (1 M+, picos post-gol) | — | Todas las escrituras van al nodo primario; cada inserción actualiza índices B-tree. Escalar escritura requiere particionado o sharding (Citus u otro), que Cassandra trae de fábrica por clave de partición |
| Sesiones con expiración | — | No hay TTL nativo: hace falta un job de limpieza y la tabla crece con filas muertas mientras tanto |
| Series temporales (10 M+ puntos) | Particionado por rango funciona bien a esta escala | La reducción de resolución (downsampling) y la retención hay que programarlas; en InfluxDB son parte del motor |
| Recorridos profundos (por ejemplo, jugador → equipo → partidos → eventos) | — | `JOIN` recursivos o varias consultas; en Neo4j es un patrón de recorrido |
| Concurrencia de lectura (2–3 M usuarios) | Réplicas de lectura + caché | El primario sigue siendo único para escrituras |

## 6. Lo que sí se midió (experimental)

El prototipo de Data Mart es **una estructura relacional** (SQLite, esquema estrella con `JOIN`). Para la pregunta analítica, con la misma notebook y los mismos datos, y comprobando que las dos respuestas fueran idénticas:

| Camino | Modelo | Tiempo (mediana) | Operaciones |
|---|---|---:|---:|
| Fuentes operacionales a través de la API | NoSQL (Cassandra + Neo4j) | 8.723 ms | 1.536 solicitudes HTTP |
| Data Mart | Relacional dimensional | 0,574 ms | 2 consultas SQL |

**Equivalencias y diferencias declaradas:** mismos datos (lote del 24/10/2026 20:33), mismo hardware y misma respuesta. **No son condiciones equivalentes en todo:** el camino operacional pasa por HTTP, la API y dos motores con datos organizados para lecturas por partición; el Data Mart es un archivo local, embebido, sin red, con los datos ya agregados. La comparación mide el beneficio de **tener una proyección relacional para esa pregunta**, no que "relacional sea más rápido que NoSQL".

Del lado operacional también hay un dato medido que vale para cualquier modelo: **el costo de abrir conexiones por solicitud** (19 ms contra 3 ms de consulta en IRIS). Un PostgreSQL usado así tendría el mismo problema y la misma solución (pool, por ejemplo PgBouncer).

## 7. Cuándo conviene cada alternativa (condicionado al caso)

**Conviene la solución NoSQL / políglota actual cuando:**
- el volumen de escrituras de comentarios en picos supera lo que absorbe un primario relacional, y el acceso es siempre "por partido y ventana" (patrón conocido de Cassandra);
- las sesiones necesitan expiración automática y lecturas de < 1 ms (Redis: 3 ms dentro de la API, el más rápido medido);
- las estadísticas son series temporales con retención y downsampling;
- se necesitan recorridos del grafo de relaciones sin una cota fija de profundidad.

**Conviene una estructura relacional cuando:**
- la pregunta cruza entidades y se responde con agregaciones y `JOIN` (el Data Mart medido);
- la integridad entre entidades importa más que la escala de escritura (calendario, equipos, árbitros: datos chicos y muy relacionados);
- el volumen y la concurrencia de escritura son moderados (por ejemplo, el plantel y el fixture: 64 equipos, 1.500 jugadores, 127 partidos);
- se quiere operar un solo motor con un solo equipo de soporte.

Conclusión del equipo: para este flujo, **un modelo híbrido**. Datos maestros chicos y relacionados (equipos, partidos, sedes, árbitros) y la capa analítica en relacional; comentarios, sesiones y series temporales en los motores NoSQL elegidos en el Hito 2. Ninguna de las dos es superior en términos absolutos.

## 8. Qué no se pudo medir en el laboratorio

- No se implementó ni se cargó una versión relacional **operacional** del flujo (PostgreSQL con los mismos endpoints). La sección 3 es conceptual.
- No se probó escritura masiva concurrente en ningún modelo (el flujo elegido es de lectura).
- SQLite es embebido y de un solo proceso escritor: sus tiempos no representan un servidor relacional con 2–3 M de usuarios.
- No se probaron réplicas, particionado real ni distribución en varios nodos, en ningún modelo: todo corre en un nodo por producto, en la misma notebook.

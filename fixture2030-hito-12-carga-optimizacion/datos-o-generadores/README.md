# Datos de prueba del Hito 12

Todos los datos son **sintéticos o de laboratorio** (no hay datos personales reales) y se generan de forma determinista con la semilla `2030` de `config/configuracion-ejemplo.json`. Los crea `scripts/preparar_datos.py`, que es idempotente: correrlo de nuevo no duplica nada.

## 1. Datos que se generan

| Base | Qué se crea | Cantidad | Identificación | Limpieza |
|---|---|---:|---|---|
| Redis | Sesiones `sesion:SES-H12-0001` … `SES-H12-0300` (hash con usuario, rol, partido, acciones; `ultimo_acceso` fijo) | 300 | prefijo `SES-H12-` | `DEL` de esas claves; además expiran a las 4 h |
| IRIS | Partidos `PAR-H12001` … `PAR-H12100` con 6–12 eventos cada uno, estado `Finalizado` | 100 partidos / 907 eventos | prefijo `PAR-H12` | `DELETE` por prefijo |
| Cassandra | 25 comentarios por bucket de 10 min × 12 buckets × 96 partidos, en `comentarios_por_partido` y `comentarios_por_usuario` | 28.800 por tabla | UUID v5 determinista + texto "(sintético H12)" | `DELETE` por clave primaria exacta, recalculada |

Por qué hizo falta generarlos:

- **Cassandra** en esta notebook solo tenía los 11 comentarios de muestra del Hito 6 (2 buckets). Con eso el 30 % de la carga hubiese leído siempre las mismas 2 particiones. Los comentarios sintéticos siguen **la misma regla de fechas del generador del Hito 6** (8 partidos por día, actividad de 120 min desde las 18:00, buckets de 10 min).
- **IRIS** solo tenía `PAR-DEMO`. Con 100 partidos más, la lectura se reparte entre 101 claves.
- **Redis**: sesiones propias con TTL largo para que no expiren a mitad de la prueba.

MongoDB (64 equipos), Neo4j (96 partidos, 192 eventos) e InfluxDB (PAR-0001, 1.080 puntos cada 10 s para ARG y MEX) se usan **tal como quedaron de los hitos anteriores**, sin modificarlos.

## 2. Catálogo de claves (`catalogo_claves.json`)

`preparar_datos.py` recorre la API **con concurrencia 1** y guarda cada clave que devuelve datos, junto con la **huella** (SHA-256 del JSON canónico, sin campos volátiles como `ttl_segundos`) de la respuesta correcta. Cada clave se lee dos veces para detectar respuestas no deterministas (resultado: 0).

| Operación | Claves | Elementos devueltos | Clave caliente (50 % de las lecturas de ese tipo) |
|---|---:|---:|---|
| `comentarios_cassandra` | 1.154 | 28.809 | partido `PAR-0001` (14 buckets) |
| `estadisticas_influxdb` | 180 | 1.080 | `PAR-0001` (todas sus claves) |
| `sesion_redis` | 300 | 300 | — (uniforme) |
| `eventos_neo4j` | 96 | 192 | `PAR-0001` |
| `detalle_iris` | 101 | 908 | — (IRIS no tiene `PAR-0001`; uniforme) |
| `equipo_mongodb` | 64 | 64 | `EQ-01` |
| **Total** | **1.895** | | |

Durante la carga, cada respuesta 200 se compara con la huella del catálogo: así se verifica que el contenido no se haya alterado, cortado o mezclado bajo concurrencia.

## 3. Distribución de la carga

- Mezcla de operaciones (pesos): comentarios 30 %, estadísticas 20 %, sesión 15 %, eventos 15 %, detalle IRIS 10 %, equipo 10 %.
- Clave caliente: con probabilidad 0,5 se elige una clave del "partido en vivo" (`PAR-0001` / `EQ-01`); si no, una clave al azar uniforme del tipo.
- Aleatoriedad reproducible: cada usuario virtual usa `random.Random(2030 * 10000 + número_de_VU)`.

## 4. Relación con el volumen proyectado

| Dimensión | Probado en el laboratorio | Proyectado en la clase para el Fixture |
|---|---:|---:|
| Comentarios | 28.809 | 1.000.000+ |
| Puntos temporales | 1.080 (1 partido) | 10.000.000+ |
| Partidos | 96 (Neo4j) / 101 (IRIS) | 127 |
| Usuarios simultáneos | 80 VUs (≈ 360 req/s) | 2–3 millones |

El volumen probado es **varias órdenes de magnitud menor** que el proyectado. Las lecturas probadas son por clave/partición (acceso puntual), cuyo costo depende poco del volumen total almacenado en Cassandra, Redis o MongoDB, pero eso **no se midió**. La extrapolación y sus límites están en `docs/integridad_y_limitaciones.md`.

## 5. Data Mart

`scripts/construir_data_mart.py` genera `data_mart_fixture.sqlite` en esta carpeta a partir de las fuentes. Es un artefacto derivado: no se versiona (`.gitignore`) y se reconstruye en ~4 s.

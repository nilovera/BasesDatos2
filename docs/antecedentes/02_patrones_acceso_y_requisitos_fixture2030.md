# Fixture 2030 — Patrones de acceso y requisitos de datos

## Criterio de diseño

El modelo se selecciona a partir de las operaciones dominantes: qué se escribe,
con qué frecuencia, mediante qué clave se consulta y qué ocurre si la información
se retrasa o no puede confirmarse. Tener relaciones entre datos no obliga a usar
un grafo; Neo4j se justifica cuando la consulta recorre esas relaciones.

Separar datos oficiales, interacción social y telemetría permite aplicar
garantías diferentes. Un comentario atrasado afecta la experiencia social; un
gol duplicado altera el estado oficial. Por ello las escrituras deportivas
necesitan control de versión e idempotencia, mientras sus vistas pueden converger
de forma eventual.

## Matriz de patrones implementados

| Necesidad | Escritura y consulta principal | Propietario | Garantía o límite |
|---|---|---|---|
| Equipos y jugadores | Catálogo por ID y pertenencia a equipo | MongoDB | IDs únicos y validación de referencias |
| Partido y marcador oficial | Actualizar estado y consultar partido por ID | MongoDB | Transacción y control de versión |
| Eventos y correcciones | Agregar un hecho; recorrer secuencia de un partido | MongoDB | Idempotencia; original conservado al corregir |
| Marcador caliente | Leer por clave, invalidar y proyectar eventos | Redis | Copia eventual; fallback oficial cuando la secuencia no coincide |
| Sesión | Crear, consultar y revocar por identificador | Redis | Expiración; identidad de laboratorio |
| Comentarios de partido | Publicar y leer por partido, tiempo y shard | Cassandra | Bucket temporal, cuatro shards y paginación |
| Comentarios de usuario | Leer por usuario y día | Cassandra | Vista duplicada intencionalmente para esa consulta |
| Moderación | Ocultar o mostrar comentario y conservar la acción | Cassandra | Estado actual más historial de auditoría del incremento 15 |
| Posiciones y mapas | Ingresar muestras y consultar rangos temporales | InfluxDB | Series por partido, equipo y jugador |
| Estadísticas y resúmenes | Medir por tiempo y consultar ventanas de 15 minutos | InfluxDB | Ingesta y agregación explícitas; no migración automática a MongoDB |
| Recomendaciones y caminos | Recorrer pertenencias, partidos y confederaciones | Neo4j | Proyección derivada con retraso posible |
| Analítica | Agregar goles y estadísticas a un grano definido | Data Mart | ETL separado y frescura dependiente del refresh |
| Auditoría | Actividad de un actor o recurso durante un día UTC | Cassandra | Una fila por acción confirmada; replay sin duplicación |

## Dependencias y orden causal

El catálogo precede a la creación de un partido. El inicio precede a los eventos
que requieren estado `EN_CURSO`. Una sustitución cambia los participantes que
el simulador utiliza para generar posiciones. La corrección referencia un evento
del mismo partido y reconstruye el agregado oficial sin borrar el original.

Las operaciones manuales y el simulador no tienen idéntico alcance de validación:
el simulador controla su alineación y sus sustituciones; la API de telemetría
valida referencias y pertenencia, sin reconstruir toda la participación histórica
para cada muestra manual.

## Acceso social y particiones calientes

Particionar comentarios solo por partido concentra toda la final en una clave.
El modelo incorpora buckets temporales y cuatro shards deterministas para
repartir escrituras dentro de un mismo partido. La lectura consulta esas
particiones acotadas y ordena los resultados. La vista por usuario evita un
escaneo global para reconstruir su actividad.

El factor de cuatro shards es una decisión del laboratorio. El perfil de carga
mixta de lectura no demuestra que sea óptimo para una ráfaga masiva de escritura.
Su evaluación requiere comparar distribución, tamaño de partición, latencia y
costo de combinar resultados con una carga representativa.

## Degradación y confirmación

- MongoDB indisponible impide confirmar nuevos hechos oficiales.
- Redis indisponible permite bypass del caché, pero afecta sesiones y temporales.
- Cassandra indisponible degrada comentarios y auditoría; la cola de auditoría
  oficial en MongoDB conserva los envíos no confirmados.
- InfluxDB indisponible degrada posiciones, estadísticas y mapas de calor.
- Neo4j indisponible degrada recorridos y retrasa la proyección de Outbox.
- Data Mart indisponible degrada analítica y ETL sin convertirse en autoridad deportiva.

La lectura oficial puede continuar ante la falla de un motor derivado cuando
MongoDB está disponible. Esto no implica que el simulador continúe sin cambios:
un error de dependencia durante su trabajo puede llevarlo a estado `ERROR`.

## Alcance diferenciado

El proyecto usa datos de demostración reproducibles. La agenda generada no es
un fixture oficial validado y las posiciones no proceden de un proveedor real.
Los perfiles persistentes, la autenticación de producción, la entrega multimedia
y los mecanismos multirregión no forman parte de la implementación ejecutada.
No se presentan como funciones terminadas ni como bloqueos de los módulos que
sí cuentan con evidencia.

La [comparación de motores](03_comparacion_motores_y_estrategia_cap.md) desarrolla
la selección y el [estado de validación](../estado_validacion.md) identifica
qué resultados se comprobaron en el laboratorio.

# Hito 6 - Rendimiento y distribución

## 1. Objetivo de la medición

La prueba tuvo como objetivo generar y cargar más de 1.000.000 de comentarios reproducibles en Apache Cassandra, registrar la tasa real obtenida y verificar que el particionamiento elegido mantuviera acotada la cantidad de filas recuperadas por partición.

El objetivo de referencia del hito era alcanzar 10.000 o más escrituras por segundo cuando el hardware lo permitiera. Los resultados de este documento corresponden únicamente al laboratorio local y no representan una prueba de producción.

## 2. Ambiente de prueba

| Elemento | Valor observado |
|---|---|
| Fecha de ejecución | 12/09/2026 |
| Sistema anfitrión | Windows, arquitectura amd64 |
| Procesador | Intel(R) Core(TM) 5 120U |
| Núcleos físicos | 10 |
| Procesadores lógicos | 12 |
| Memoria RAM | 13,7 GB |
| Docker | Docker Desktop, cliente 29.7.2 |
| Docker Compose | 5.4.0 |
| Imagen | `cassandra:latest` |
| Cassandra observada | 5.0.9 |
| cqlsh | 6.2.0 |
| Especificación CQL | 3.4.7 |
| Protocolo nativo | v5 |
| Topología | Un nodo local |
| Estado del nodo | `UN` (`Up/Normal`) |
| Consistencia de la carga | `ONE` |
| Replicación del laboratorio | `SimpleStrategy`, factor 1 |
| Procesos utilizados por `COPY` | 11 |

## 3. Datos generados

El script `scripts/carga_o_prueba.ps1` generó archivos CSV de manera determinista. Una nueva ejecución con la misma cantidad reemplaza los archivos y vuelve a producir las mismas claves, por lo que el proceso es reproducible.

| Dato | Resultado |
|---|---:|
| Comentarios únicos | 1.000.128 |
| Filas físicas preparadas | 2.000.256 |
| Partidos utilizados | 96 |
| Usuarios posibles | 50.000 |
| Archivo para `comentarios_por_partido` | 158,09 MB |
| Archivo para `comentarios_por_usuario` | 154,28 MB |
| Tiempo de generación | 62,3 segundos |

Las 2.000.256 filas físicas se explican por la duplicación controlada: cada comentario se prepara una vez para la consulta por partido y otra vez para la consulta por usuario.

## 4. Método de carga

La carga se ejecutó mediante `cqlsh` y el script `scripts/carga_masiva.cql`. El script realizó dos operaciones `COPY`, una por cada tabla de acceso, con nivel de consistencia `ONE`.

```powershell
docker exec -it fixture2030-cassandra cqlsh -f /scripts/carga_masiva.cql
```

Antes de la carga completa se utilizó una muestra de 1.000 comentarios para comprobar las rutas, las columnas, los tipos de dato y la importación. La prueba pequeña terminó con cero filas omitidas. Después, el generador reemplazó los CSV de prueba por los archivos de 1.000.128 comentarios.

## 5. Resultados observados

| Tabla | Filas importadas | Tiempo | Tasa promedio | Filas omitidas |
|---|---:|---:|---:|---:|
| `comentarios_por_partido` | 1.000.128 | 22,398 s | 44.652 filas/s | 0 |
| `comentarios_por_usuario` | 1.000.128 | 23,782 s | 42.054 filas/s | 0 |
| **Total físico** | **2.000.256** | **46,180 s** | **aprox. 43.314 filas/s** | **0** |

La tasa total aproximada se calculó dividiendo las 2.000.256 filas físicas por los 46,180 segundos acumulados de las dos cargas secuenciales.

El resultado superó el objetivo de referencia de 10.000 escrituras por segundo en ambas tablas. No se modificó la cifra observada ni se proyectó una tasa diferente para producción.

## 6. Distribución y tamaño de las particiones

El conjunto distribuye exactamente 1.000.128 comentarios entre 96 partidos, lo que equivale a 10.418 comentarios por partido. La tabla principal también utiliza un bucket de diez minutos dentro de una ventana de actividad de 120 minutos.

El promedio teórico es de aproximadamente 868 comentarios por partición de partido y bucket. Como verificación concreta, la partición formada por `PAR-0001` y el bucket `203006131800` devolvió 1.200 filas.

La clave de partición `(partido_id, bucket_10min)` evita almacenar toda la actividad de un partido en una sola partición. La tabla secundaria utiliza `(usuario_id, bucket_dia)`, por lo que el historial completo de un usuario tampoco crece dentro de una única partición ilimitada.

## 7. Interpretación

- La carga de la tabla principal alcanzó una tasa promedio de 44.652 filas por segundo.
- La tabla secundaria alcanzó 42.054 filas por segundo y resultó levemente más lenta en esta ejecución.
- La duplicación controlada duplica la cantidad de escrituras físicas, pero permite responder las consultas por partido y por usuario sin `ALLOW FILTERING`.
- Las dos importaciones finalizaron con cero filas omitidas.
- La comprobación de 1.200 filas muestra que el bucket mantiene una partición acotada dentro del conjunto generado.

## 8. Limitaciones

- Cassandra se ejecutó en un único contenedor y con factor de replicación 1. La prueba no demuestra alta disponibilidad, tolerancia a fallas ni distribución multirregional.
- Docker Desktop comparte CPU, memoria y almacenamiento con Windows y con otros procesos del equipo.
- `COPY` incluye lectura de los archivos CSV, procesamiento del cliente y envío de datos a Cassandra. Por lo tanto, la cifra representa este método de carga completo y no una medición aislada del motor.
- La prueba registra throughput de carga, pero no latencias percentiles de lectura o escritura.
- El nivel `CONSISTENCY ONE` y la ausencia de réplicas adicionales reducen el trabajo respecto de una topología productiva.
- Los resultados pueden variar según la carga del equipo, el estado del disco, la memoria disponible y la configuración de Docker.

## 9. Evidencia asociada

- `15_generacion_millon.png`: generación reproducible, cantidad, distribución, tamaños y tiempo.
- `16_carga_masiva_completa.png`: filas importadas, tiempos, tasas, cero omitidas y verificación de la partición.
- `17_recursos_equipo.png`: procesador, núcleos, procesadores lógicos y memoria RAM.
- Las evidencias previas registran la versión de Cassandra, el estado `UN`, la creación del esquema, su segunda ejecución, la carga de muestra repetida, las consultas y las operaciones CRUD.

## 10. Conclusión

El mecanismo produjo más de un millón de comentarios únicos y cargó 2.000.256 filas físicas de forma reproducible. La tasa promedio observada superó el objetivo de referencia y no se omitieron filas. El resultado valida el procedimiento dentro del laboratorio de un nodo, pero no debe interpretarse como una garantía de rendimiento productivo.

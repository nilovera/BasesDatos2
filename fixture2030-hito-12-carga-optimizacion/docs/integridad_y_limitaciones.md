# Integridad, anomalías, limitaciones y próximos pasos (RF15, RNF4, RNF6, RNF14, punto 5.8)

## 1. Cómo se valida la integridad

Un HTTP 200 no se toma como prueba de que el dato llegó bien. `scripts/validar_integridad.py` corre después de cada prueba y hace 8 controles en 4 capas:

| # | Control | Qué detecta | Capa |
|---|---|---|---|
| 1 | Ningún `request_id` repetido | Solicitudes duplicadas por el generador (reintentos, errores de concurrencia) | Generador |
| 2 | Ninguna respuesta con huella distinta a la del catálogo | Datos alterados, cortados, mezclados entre solicitudes concurrentes o de otra clave | Contenido |
| 3 | Todos los `request_id` con respuesta aparecen en el log de la API | Que la API haya atendido realmente lo que el generador dice haber enviado | API |
| 4 | El código HTTP del log de la API coincide con el que recibió el cliente | Respuestas cambiadas en el camino | API |
| 5 | Relectura completa del catálogo (1.895 claves) con concurrencia 1 después de la carga | Que la prueba no haya modificado ni perdido datos en las fuentes | Fuentes, vía API |
| 6 | Conteo directo en Redis: 300 sesiones `SES-H12-*` | Pérdida o expiración de sesiones | Fuente (driver nativo) |
| 7 | Conteo directo en IRIS: 100 partidos `PAR-H12*` (y 907 eventos) | Pérdida de objetos | Fuente (driver nativo) |
| 8 | Conteo directo en Cassandra: 28.800 comentarios sintéticos, buscados por su clave exacta en 1.152 particiones | Pérdida o duplicación de comentarios | Fuente (driver nativo) |

Además, el generador registra para cada solicitud si fue **exitosa**, **rechazada** (con causa: `http_4xx/5xx`, `timeout`, `conexion_*`), **alterada** o **no verificable**.

## 2. Resultados de integridad de todas las corridas

| Corrida | Generadas | Con respuesta | Exitosas y correctas | Rechazadas | Alteradas | Duplicadas | En log API | Catálogo después | Redis / IRIS / Cassandra | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `humo_20261024-193640` | 341 | 341 | 341 | 0 | 0 | 0 | 341 | idéntico | 300 / 100 / 28.800 | APROBADO |
| `v1_linea_base_generador_1proceso` | 32.503 | 32.503 | 32.503 | 0 | 0 | 0 | 32.503 | idéntico | 300 / 100 / 28.800 | APROBADO |
| `linea_base_20261024-195501` | 81.000 | 81.000 | 81.000 | 0 | 0 | 0 | 81.000 | idéntico | 300 / 100 / 28.800 | APROBADO |
| `optimizada_20261024-200735` | 81.364 | 81.364 | 81.364 | 0 | 0 | 0 | 81.364 | idéntico | 300 / 100 / 28.800 | APROBADO |
| `linea_base_20261024-201624` | 80.481 | 80.481 | 80.481 | 0 | 0 | 0 | 80.481 | idéntico | 300 / 100 / 28.800 | APROBADO |
| `optimizada_20261024-202348` | 82.860 | 82.860 | 82.860 | 0 | 0 | 0 | 82.860 | idéntico | 300 / 100 / 28.800 | APROBADO |

(Las cifras de "Generadas" incluyen el calentamiento, por eso son mayores que las "solicitudes medidas" de los resúmenes.)

Integridad del Data Mart (lote `DM-20261024-203358-5374c1`): comentarios 28.809 = 28.809, eventos 192 = 192, 1.440 filas = 96 × 15, 0 duplicadas, 0 huérfanas. Las respuestas por fuente operacional y por Data Mart fueron **idénticas** (ver `integracion_data_mart.md`).

**Recuperación luego de una interrupción:** el corte seguro se probó contra un servidor que se apagaba a mitad de la prueba: el generador detectó > 50 % de errores, detuvo los 4 procesos y guardó todo lo medido hasta ese momento con la causa (`conexion_ConnectError`). En el Data Mart, una falla a mitad de la carga hace rollback y deja publicado el lote anterior completo.

## 3. Anomalía observada: congelamientos de 3,5–4 s de la API

En 2 de las 6 corridas largas la API se detuvo por completo durante unos segundos:

| Corrida | Momento | Duración | Señales |
|---|---|---|---|
| v1 (sin pool) | t ≈ 177 s, sostenimiento | ~3,6 s | 41 solicitudes > 2 s, de las **6** operaciones (incluso Redis y MongoDB). Todas las que estaban en curso terminaron en el mismo instante (t = 180,97 s). Tiempo dentro de la API de hasta 3.577 ms. CPU de la API: 34 % → 8 % → 2 % |
| OPT1 (con pool) | t ≈ 276 s, pico | ~4 s | 80 solicitudes > 2 s, de todas las operaciones. CPU de la API = **0 %** y CPU de todo el sistema = 7 % durante la pausa. Hilos de la API: 57 → 73 al reanudar |

Lo que se sabe:

- **No depende de la optimización:** ocurrió con y sin pool, y no ocurrió en las otras 4 corridas.
- **No es CPU:** durante la pausa la CPU de la API y de todo el sistema cae casi a 0. El proceso está **bloqueado esperando algo** (E/S o un lock), no calculando.
- **No es una base en particular:** se detienen a la vez operaciones de las seis bases.
- No hubo errores ni pérdida de datos: las solicitudes terminaron bien, solo tarde.

Hipótesis principal: la API escribe **dos líneas de log por solicitud** de forma sincrónica (el log de la aplicación en `logs/api.stderr.log`, que se escribe desde el middleware asíncrono, o sea dentro del event loop, y el log de acceso de uvicorn en `logs/api.stdout.log`). En una corrida esos archivos crecen a ~25 MB y ~10 MB. Si Windows bloquea la escritura un par de segundos (por ejemplo, el antivirus escaneando un archivo que crece rápido), el event loop de la API se detiene y con él todas las solicitudes. Es el caso "Observabilidad: logs excesivos" de la Clase 13.

**Prueba propuesta (no ejecutada):** repetir el escenario 3 veces con el log por solicitud desactivado (o con la carpeta `logs` excluida del antivirus) y comparar la frecuencia de congelamientos. Si desaparecen, mover el log a un handler asíncrono (`QueueHandler`) que no bloquee el event loop. **Costo:** la validación de integridad cruza `request_id` contra ese log, así que habría que mantenerlo de otra forma.

Efecto en los resultados: estos eventos inflan el máximo y el P99 de la fase en que ocurren (OPT1: P99 del pico 614 ms, máx. 4.510 ms). Por eso cada versión se corrió dos veces, se informan las dos y no se saca la mejora del pico de una sola corrida.

## 4. Limitaciones del laboratorio

| Limitación | Consecuencia |
|---|---|
| **Una sola notebook** para el generador, la API y las 6 bases | Compiten por CPU, RAM y disco. Se mitigó midiendo la CPU de cada parte por separado, pero no hay aislamiento real |
| Red local (loopback) | Sin latencia ni pérdida de red real; en producción, cada salto agrega milisegundos |
| **RAM al 68–77 %** (≈ 94 % antes de cerrar aplicaciones) | Riesgo de paginación. Se pidió cerrar aplicaciones y se registró la RAM en cada muestra |
| API con **1 proceso** de uvicorn | El techo medido (~330–364 req/s) es el de un núcleo de Python con esta mezcla, no el de la arquitectura |
| Modelo cerrado con think time de 50–150 ms | El throughput depende de VUs y espera; no se probó un modelo abierto (tasa fija de llegada), que mostraría colas si la tasa supera la capacidad |
| Solo lecturas | No se midió el costo de escritura ni la competencia lectura/escritura del "partido en vivo" |
| Datos sintéticos, distribución uniforme de comentarios (25 por ventana) | Particiones parejas; no aparecen particiones calientes reales de Cassandra |
| Volumen probado muy inferior al proyectado (sección 5) | Las lecturas por clave probadas dependen poco del volumen total, pero no se verificó |
| IRIS Community limitado a **8 conexiones** | Limita el pool y la escala horizontal de la API en el laboratorio; una licencia comercial no tendría ese tope |
| Imágenes `latest` (Neo4j, Cassandra, Redis, IRIS) | Una actualización de imagen puede cambiar resultados; la versión observada queda en `metadatos.json` |
| Resolución del temporizador de Windows (~15 ms) | El retraso del event loop del generador nunca baja de ~20 ms; se usa para ver si crece, no como valor absoluto |
| `docker stats` cada 2 s | Muestreo grueso: un pico de CPU de menos de 2 s puede no verse |
| Percentiles por fase con interpolación lineal | P99 de fases cortas (30 s, ~2.500 solicitudes en la recuperación) es sensible a pocas solicitudes lentas |

## 5. Volumen probado vs. capacidad proyectada (RNF6)

**Medido:**

- Un proceso de API con esta mezcla de 6 operaciones atiende **~310 req/s con P95 ≈ 65–70 ms** (40 VUs) y llega a **~334–364 req/s** con 80 VUs, ya con un núcleo saturado y P95 ≈ 290–330 ms.
- Con el pool, el tiempo dentro de la API por solicitud es P50 = 8,4 ms promedio entre operaciones.

**Estimado (no medido, solo orden de magnitud):** si cada uno de 2–3 millones de usuarios simultáneos hiciera una solicitud cada 10 s, la plataforma recibiría **200.000–300.000 req/s**. A ~300 req/s por proceso de API, harían falta del orden de **700–1.000 procesos de API**, además de escalar cada base. Este cálculo **supone escalado lineal**, que en la realidad no se cumple:

- las bases tienen su propio límite: Cassandra y MongoDB escalan horizontalmente, pero IRIS Community no pasa de 8 conexiones en total;
- respuestas iguales para millones de usuarios (equipos, eventos del partido) se resolverían con caché o CDN y no llegarían a la API;
- el congelamiento por E/S de logs a esa escala sería un problema serio.

La conclusión válida es la **relativa**: con la misma notebook y la misma carga, el pool de IRIS bajó 84 % el tiempo de esa operación y liberó 19 % de CPU del componente que limita el sistema. **No se puede concluir** que la plataforma soporte el escenario del Mundial.

## 6. Qué es medido, qué es estimado y qué es diseño (RNF14)

| Tipo | Ejemplos en este hito |
|---|---|
| **Medido** | Todas las tablas de `linea_base.md`, `hipotesis_y_optimizacion.md` (secciones 3 y 6), los conteos de integridad, la construcción y la consulta del Data Mart. Cada número tiene su archivo en `docs/evidencia/` |
| **Estimado** | La sección 5 de este documento (procesos necesarios para 2–3 M de usuarios) y la capacidad teórica del pool (~1.000 req/s de IRIS con 5 conexiones) |
| **Diseño / propuesta** | El ETL incremental de producción, la frescura de 12 minutos, el esquema relacional operacional de `comparacion_relacional.md` |
| **Hipótesis no verificada** | La causa de los congelamientos (log sincrónico / antivirus) |

## 7. Próximos pasos

1. Probar la hipótesis de los congelamientos (log asíncrono o desactivado) con 3 repeticiones.
2. Escalar la API a varios procesos (`--workers`), repartiendo el pool de IRIS (p. ej. 2 por proceso, sin pasar de 8 en total), y medir si el techo pasa de ~360 req/s.
3. Agregar un escenario de **escritura** (alta de comentarios) para medir competencia lectura/escritura en el "partido en vivo".
4. Escenario de modelo abierto (tasa fija) para encontrar la capacidad y el punto de saturación con colas.
5. Exponer estas métricas a Prometheus y verlas en Grafana (Clase 14), en lugar de `psutil` y `docker stats`.
6. Data Mart: pasar a carga incremental por ventana cerrada y acordar una fuente de verdad para el calendario y los equipos (hoy hay inconsistencias entre Neo4j, MongoDB, Cassandra e InfluxDB).

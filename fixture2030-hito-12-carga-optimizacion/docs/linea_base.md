# Línea base (RF4, RF5, RF6, punto 5.4)

Todas las cifras de este documento son **mediciones reales** tomadas en la notebook descripta en `compose-o-instrucciones-del-entorno.md`. Cada corrida tiene su carpeta en `docs/evidencia/` con los datos crudos.

## 1. Condiciones registradas

| Elemento | Línea base 1 | Línea base 2 (repetición) |
|---|---|---|
| Carpeta de evidencia | `linea_base_20261024-195501` | `linea_base_20261024-201624` |
| Fecha y hora | 24/10/2026 19:55:01 – 20:00:38 (UTC-3) | 24/10/2026 20:16:24 – 20:22:02 (UTC-3) |
| Commit de la API | `657a285` (rama `Conectividad`, código original) | `542a1d8` (código con pool, **apagado**: `IRIS_POOL_SIZE=0`) |
| Configuración API | 1 proceso uvicorn, timeout de dependencias 5 s, IRIS sin pool | igual |
| Imágenes / clientes | ver `metadatos.json → contenedores` y `→ versiones` | igual |
| Datos | catálogo de 1.895 claves, semilla 2030 | igual |
| Escenario | `completo`: 330 s, 5→40→80→10 VUs, generador de 4 procesos | igual |

La línea base 2 corre sobre el **código nuevo con el pool desactivado**. Que dé lo mismo que la línea base 1 (sección 3) demuestra que la variable `IRIS_POOL_SIZE=0` reproduce el comportamiento original y que la única diferencia con la versión optimizada es el pool.

## 2. Primer intento (v1): el generador era el cuello de botella

Antes de la línea base válida se corrió el mismo escenario con un generador de **un solo proceso** (`docs/evidencia/v1_linea_base_generador_1proceso_20261024-194009`). Se conserva como evidencia porque muestra una lección central del hito (Clase 13: "una caída del throughput puede ser culpa del generador y no de la base").

| Fase | VUs | req/s | P50 cliente | P95 cliente | P95 **dentro de la API** |
|---|---|---:|---:|---:|---:|
| Calentamiento | 5 | 43,6 | 16,5 ms | 34,6 ms | 25,7 ms |
| Rampa | 5→40 | 112,0 | 61,2 ms | 350,3 ms | 25,6 ms |
| Sostenimiento | 40 | 106,4 | 200,5 ms | 690,9 ms | 25,5 ms |
| Pico post-gol | 80 | 101,8 | 499,0 ms | 1.817,2 ms | 25,5 ms |

Lectura:

- El throughput **se clavó en ~110 req/s** a partir de ~22 VUs. Duplicar los usuarios en el pico no aumentó el throughput, solo la espera (P50 de 200 a 499 ms).
- El tiempo **dentro de la API no cambió en ninguna fase** (P95 ≈ 25,5 ms). La API y las bases no estaban cargadas: la espera se formaba afuera.
- El proceso generador estaba al **100,9 % de un núcleo** durante el sostenimiento (máx. 105 %), mientras la API usaba 32 %.

Conclusión: se medía el límite del generador, no el del sistema. **Corrección:** el generador se reparte en 4 procesos con un reloj común (`procesos_generador: 4`). No es una optimización del sistema bajo prueba, sino del instrumento de medición; por eso v1 no se usa para comparar.

## 3. Línea base válida (v2): resultados por fase

| Fase | VUs | Solicitudes (LB1 / LB2) | req/s | P50 | P95 | P99 | Máx | P95 dentro de la API |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Calentamiento* | 5 | 1.276 / 1.280 | 42,5 / 42,7 | 11,7 / 11,4 | 30,3 / 30,7 | 36,1 / 35,1 | 66 / 67 | 25,5 / 25,5 |
| Rampa | 5→40 | 11.115 / 11.117 | 185,3 / 185,3 | 20,7 / 20,8 | 50,8 / 50,7 | 71,0 / 68,6 | 122 / 123 | 29,6 / 29,8 |
| Sostenimiento | 40 | 56.037 / 55.731 | 311,3 / 309,6 | 29,7 / 30,4 | 69,9 / 70,3 | 93,5 / 92,9 | 531 / 152 | 35,7 / 35,9 |
| Pico post-gol | 80 | 10.017 / 10.022 | 333,9 / 334,1 | 113,9 / 112,7 | 325,8 / 332,6 | 478,0 / 477,0 | 921 / 959 | 41,9 / 47,3 |
| Recuperación | 10 | 2.555 / 2.331 | 85,2 / 77,7 | 13,2 / 18,5 | 31,9 / 66,0 | 37,4 / 207,1 | 83 / 509 | 25,4 / 44,7 |

Latencias en ms. \*El calentamiento no entra en el resultado global.

Resultado global de las fases medidas: **79.724 / 79.201 solicitudes, 0 errores, 265,8 / 264,0 req/s, P50 30,6 / 31,5 ms, P95 135,4 / 135,2 ms, P99 285,2 / 292,3 ms.**

Las dos corridas coinciden dentro del 1–3 % en throughput y percentiles del sostenimiento y del pico, por lo que la línea base es **reproducible**.

## 4. Por operación durante el sostenimiento (40 VUs, 180 s)

| Operación | P50 cliente (LB1 / LB2) | P95 cliente | P50 **dentro de la API** | P95 dentro de la API (LB1) |
|---|---:|---:|---:|---:|
| Comentarios — Cassandra | 31,6 / 32,0 | 67,6 / 67,9 | 13,0 / 13,0 | 24,8 |
| Estadísticas — InfluxDB | 30,2 / 30,7 | 67,5 / 68,4 | 11,5 / 11,5 | 23,3 |
| Sesión — Redis | 21,7 / 22,3 | 56,7 / 60,1 | 3,0 / 3,0 | 12,8 |
| Eventos — Neo4j | 24,7 / 25,1 | 64,9 / 64,5 | 5,6 / 5,7 | 20,2 |
| **Detalle — IRIS** | **52,6 / 53,1** | **89,1 / 90,7** | **33,9 / 34,1** | **51,2** |
| Equipo — MongoDB | 22,9 / 23,7 | 62,7 / 61,9 | 4,1 / 4,3 | 17,0 |

(ms)

- Dentro de la API, **IRIS tarda 34 ms**, entre 2,6 y 11 veces más que el resto.
- La diferencia entre cliente y API (~18–20 ms para todas las operaciones) es cola antes de la API: con 40 VUs, el único proceso de la API ya está cerca de saturarse (sección 5).

## 5. Recursos (promedio por fase; CPU 100 % = 1 núcleo)

| Fase | CPU API | CPU contenedor IRIS | CPU Cassandra | CPU InfluxDB | CPU Neo4j | CPU generador (4 proc.) | RAM sistema |
|---|---:|---:|---:|---:|---:|---:|---:|
| Rampa | 45,6 / 46,2 % | 31,7 / 30,9 % | 22,5 % | 20,5 % | 4,5 % | 73,6 / 76,5 % | 69–74 % |
| Sostenimiento | **85,3 / 86,1 %** | **56,8 / 58,0 %** | 32,9 % | 37,4 % | 5,8 % | 170,9 / 172,6 % | 70–74 % |
| Pico post-gol | **93,7 / 98,0 %** (máx. 106 %) | 70,1 / 66,0 % | 35,0 % | 41,1 % | 4,5 % | 368,6 / 370,3 % | 70–74 % |

Valores de LB1 / LB2 cuando se tienen los dos; el resto, de LB1. MongoDB y Redis < 1 %. El retraso del event loop del generador se mantuvo en 18–33 ms (≈ resolución del temporizador de Windows), sin crecer con la carga.

Lectura (triangulación entre capas):

1. **Generador:** usa 3,7 de sus 12 núcleos disponibles en el pico y su event loop no se atrasa → **ya no limita**.
2. **API:** un solo proceso Python al 94–106 % de un núcleo en el pico → **es el límite del sistema** en este laboratorio. Por eso el throughput pasa de 311 req/s (40 VUs) a solo 334 req/s (80 VUs) mientras la latencia P50 se cuadruplica: con 80 VUs las solicitudes hacen cola para entrar a la API.
3. **IRIS:** el contenedor gasta **57–70 % de CPU para atender solo ~31–33 req/s** (10 % de la mezcla). Ninguna otra base gasta tanto por solicitud: Cassandra atiende ~95 req/s con 33 %. Es la primera señal de que algo caro ocurre en cada pedido a IRIS.

## 6. Integridad y errores de la línea base

| | LB1 | LB2 |
|---|---:|---:|
| Solicitudes generadas (incluye calentamiento) | 81.000 | 80.481 |
| Con respuesta / exitosas y con contenido correcto | 81.000 / 81.000 | 80.481 / 80.481 |
| Rechazadas, timeouts, errores de conexión | 0 | 0 |
| Respuestas alteradas | 0 | 0 |
| `request_id` duplicados | 0 | 0 |
| Respuestas encontradas en el log de la API / código HTTP distinto | 81.000 / 0 | 80.481 / 0 |
| Relectura del catálogo tras la carga (1.895 claves) | idéntico | idéntico |
| Redis / IRIS / Cassandra (conteo directo de datos H12) | 300 / 100 / 28.800 | 300 / 100 / 28.800 |

## 7. Estabilidad

- Las dos líneas base válidas fueron estables: sin errores, sin cortes y con series de 5 s sin saltos (ver `serie_tiempo.csv`).
- La recuperación de la LB2 tuvo un P99 más alto (207 ms). La serie de 5 s muestra que no fue la cola del pico vaciándose (los primeros 10 s de la fase fueron normales, P95 33–38 ms), sino un aumento posterior del tiempo **dentro de la API** (P95 45–74 ms entre t=310 y 330 s) con solo 10 VUs. Con tan poca carga no hay cola, por lo que se atribuye a una perturbación del entorno compartido (tareas de fondo de Windows/Docker o escritura del log). Lo mismo se ve en la optimizada 1 en t=320 s. Por eso la fase de recuperación se compara con cautela.
- En la corrida v1 se observó un **congelamiento de ~3,5 s** de la API en t≈177 s (todas las solicitudes en curso, de las 6 bases, terminaron juntas). Se repitió una vez en una corrida optimizada. Se analiza en `integridad_y_limitaciones.md`.

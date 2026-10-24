# Resultados de la línea base

Generado por `scripts/resumir_evidencia.py` el 2026-10-24T20:46:29-03:00 a partir de las carpetas de corrida. Los datos crudos de cada corrida (una fila por solicitud) están en su carpeta.

Configuración: API sin pool de IRIS (`IRIS_POOL_SIZE=0`). Escenario `completo` con el generador de 4 procesos.

## `linea_base_20261024-195501`

| Dato | Valor |
|---|---|
| Inicio / fin | 2026-10-24T19:55:01-03:00 / 2026-10-24T20:00:38-03:00 |
| Commit API (rama) | `657a285` (Carga), cambios sin commit en `app/`: False |
| IRIS_POOL_SIZE | 0 |
| Escenario / generador | completo / generador propio asyncio + httpx, modelo cerrado, 4 procesos |
| Corte seguro | no |
| Hardware | AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD, 6/12 núcleos, 15.9 GB |
| /health/ready previo | HTTP 200 |
| Global medido | 79724 solicitudes, 79724 exitosas, error 0.0 %, 265.75 req/s, P50 30.62 ms, P95 135.39 ms, P99 285.15 ms, máx 920.63 ms |
| Integridad | APROBADO — generadas 81000, exitosas y correctas 81000, alteradas 0, duplicadas 0 |

| Fase | Solicitudes | req/s | P50 | P95 | P99 | Máx | API P50 | API P95 | Errores | CPU API | CPU IRIS | CPU generador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| calentamiento | 1276 | 42.53 | 11.68 | 30.28 | 36.08 | 66.37 | 7.23 | 25.46 | 0 | 6.9 | 6.9 | 11.4 |
| rampa | 11115 | 185.25 | 20.65 | 50.78 | 71.02 | 122.25 | 8.33 | 29.63 | 0 | 45.6 | 31.7 | 73.6 |
| sostenimiento | 56037 | 311.32 | 29.74 | 69.89 | 93.46 | 530.54 | 10.14 | 35.7 | 0 | 85.3 | 56.8 | 170.9 |
| pico_post_gol | 10017 | 333.9 | 113.93 | 325.84 | 477.99 | 920.63 | 10.23 | 41.85 | 0 | 93.7 | 70.1 | 368.6 |
| recuperacion | 2555 | 85.17 | 13.24 | 31.92 | 37.36 | 82.56 | 7.13 | 25.37 | 0 | 22.3 | 11.7 | 34.9 |

Por operación en el sostenimiento:

| Operación | Solicitudes | P50 | P95 | P99 | API P50 | API P95 |
|---|---:|---:|---:|---:|---:|---:|
| comentarios_cassandra | 16661 | 31.61 | 67.55 | 91.43 | 13.0 | 24.83 |
| estadisticas_influxdb | 11351 | 30.15 | 67.45 | 89.78 | 11.45 | 23.28 |
| sesion_redis | 8340 | 21.66 | 56.68 | 78.59 | 3.04 | 12.76 |
| eventos_neo4j | 8498 | 24.66 | 64.89 | 88.27 | 5.64 | 20.16 |
| detalle_iris | 5591 | 52.6 | 89.12 | 111.93 | 33.85 | 51.23 |
| equipo_mongodb | 5596 | 22.91 | 62.68 | 87.43 | 4.11 | 16.97 |

Latencias en ms (cliente). CPU: promedio de la fase, 100 % = 1 núcleo.

## `linea_base_20261024-201624`

| Dato | Valor |
|---|---|
| Inicio / fin | 2026-10-24T20:16:24-03:00 / 2026-10-24T20:22:02-03:00 |
| Commit API (rama) | `542a1d8` (Carga), cambios sin commit en `app/`: False |
| IRIS_POOL_SIZE | 0 |
| Escenario / generador | completo / generador propio asyncio + httpx, modelo cerrado, 4 procesos |
| Corte seguro | no |
| Hardware | AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD, 6/12 núcleos, 15.9 GB |
| /health/ready previo | HTTP 200 |
| Global medido | 79201 solicitudes, 79201 exitosas, error 0.0 %, 264.0 req/s, P50 31.5 ms, P95 135.16 ms, P99 292.31 ms, máx 958.55 ms |
| Integridad | APROBADO — generadas 80481, exitosas y correctas 80481, alteradas 0, duplicadas 0 |

| Fase | Solicitudes | req/s | P50 | P95 | P99 | Máx | API P50 | API P95 | Errores | CPU API | CPU IRIS | CPU generador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| calentamiento | 1280 | 42.67 | 11.37 | 30.73 | 35.13 | 66.76 | 6.91 | 25.53 | 0 | 7.8 | 6.4 | 12.3 |
| rampa | 11117 | 185.28 | 20.83 | 50.7 | 68.63 | 122.64 | 8.35 | 29.77 | 0 | 46.2 | 30.9 | 76.5 |
| sostenimiento | 55731 | 309.62 | 30.35 | 70.28 | 92.86 | 151.96 | 10.2 | 35.91 | 0 | 86.1 | 58.0 | 172.6 |
| pico_post_gol | 10022 | 334.07 | 112.69 | 332.61 | 476.97 | 958.55 | 10.9 | 47.29 | 0 | 98.0 | 66.0 | 370.3 |
| recuperacion | 2331 | 77.7 | 18.5 | 65.99 | 207.05 | 509.29 | 7.72 | 44.66 | 0 | 20.5 | 10.4 | 31.4 |

Por operación en el sostenimiento:

| Operación | Solicitudes | P50 | P95 | P99 | API P50 | API P95 |
|---|---:|---:|---:|---:|---:|---:|
| comentarios_cassandra | 16567 | 31.99 | 67.88 | 89.33 | 13.01 | 25.04 |
| estadisticas_influxdb | 11290 | 30.65 | 68.43 | 89.29 | 11.51 | 23.99 |
| sesion_redis | 8296 | 22.26 | 60.14 | 79.62 | 3.04 | 13.39 |
| eventos_neo4j | 8452 | 25.06 | 64.52 | 87.34 | 5.66 | 20.02 |
| detalle_iris | 5562 | 53.06 | 90.66 | 111.29 | 34.09 | 50.94 |
| equipo_mongodb | 5564 | 23.66 | 61.9 | 86.92 | 4.25 | 17.17 |

Latencias en ms (cliente). CPU: promedio de la fase, 100 % = 1 núcleo.


---

### Corrida descartada como línea base (se conserva como evidencia)

## `v1_linea_base_generador_1proceso_20261024-194009`

| Dato | Valor |
|---|---|
| Inicio / fin | 2026-10-24T19:40:09-03:00 / 2026-10-24T19:45:42-03:00 |
| Commit API (rama) | `657a285` (Carga), cambios sin commit en `app/`: False |
| IRIS_POOL_SIZE | 0 |
| Escenario / generador | completo / generador propio asyncio + httpx (modelo cerrado de usuarios virtuales) |
| Corte seguro | no |
| Hardware | AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD, 6/12 núcleos, 15.9 GB |
| /health/ready previo | HTTP 200 |
| Global medido | 31191 solicitudes, 31191 exitosas, error 0.0 %, 103.8 req/s, P50 164.02 ms, P95 801.5 ms, P99 1542.01 ms, máx 4447.86 ms |
| Integridad | APROBADO — generadas 32503, exitosas y correctas 32503, alteradas 0, duplicadas 0 |

| Fase | Solicitudes | req/s | P50 | P95 | P99 | Máx | API P50 | API P95 | Errores | CPU API | CPU IRIS | CPU generador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| calentamiento | 1312 | 43.59 | 16.45 | 34.64 | 40.08 | 75.09 | 7.11 | 25.72 | 0 | 11.7 | 7.9 | 14.3 |
| rampa | 6731 | 112.0 | 61.18 | 350.3 | 597.3 | 1474.06 | 6.56 | 25.63 | 0 | 31.7 | 18.3 | 76.3 |
| sostenimiento | 19166 | 106.36 | 200.47 | 690.94 | 1092.98 | 4447.86 | 6.55 | 25.54 | 0 | 32.1 | 16.4 | 100.9 |
| pico_post_gol | 3063 | 101.76 | 499.0 | 1817.23 | 2819.9 | 4139.53 | 6.51 | 25.5 | 0 | 31.4 | 14.8 | 103.3 |
| recuperacion | 2231 | 74.12 | 20.6 | 47.33 | 101.76 | 3774.53 | 6.66 | 25.59 | 0 | 22.5 | 8.9 | 32.0 |

Por operación en el sostenimiento:

| Operación | Solicitudes | P50 | P95 | P99 | API P50 | API P95 |
|---|---:|---:|---:|---:|---:|---:|
| comentarios_cassandra | 5634 | 204.37 | 696.23 | 1179.16 | 10.8 | 21.65 |
| estadisticas_influxdb | 3898 | 197.94 | 682.98 | 1054.34 | 6.96 | 8.97 |
| sesion_redis | 2902 | 189.32 | 711.24 | 1043.88 | 1.26 | 2.18 |
| eventos_neo4j | 2945 | 196.4 | 659.19 | 1024.78 | 2.65 | 4.26 |
| detalle_iris | 1883 | 222.48 | 711.89 | 1099.92 | 25.28 | 31.04 |
| equipo_mongodb | 1904 | 195.12 | 646.71 | 1139.3 | 1.69 | 2.76 |

Latencias en ms (cliente). CPU: promedio de la fase, 100 % = 1 núcleo.


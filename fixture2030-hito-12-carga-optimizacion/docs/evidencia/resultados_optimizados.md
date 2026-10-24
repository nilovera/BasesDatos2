# Resultados de la versión optimizada

Generado por `scripts/resumir_evidencia.py` el 2026-10-24T20:46:29-03:00 a partir de las carpetas de corrida. Los datos crudos de cada corrida (una fila por solicitud) están en su carpeta.

Configuración: API con pool de IRIS (`IRIS_POOL_SIZE=5`, commit `542a1d8`). Mismo escenario, datos y semilla que la línea base.

## `optimizada_20261024-200735`

| Dato | Valor |
|---|---|
| Inicio / fin | 2026-10-24T20:07:35-03:00 / 2026-10-24T20:13:13-03:00 |
| Commit API (rama) | `542a1d8` (Carga), cambios sin commit en `app/`: False |
| IRIS_POOL_SIZE | 5 |
| Escenario / generador | completo / generador propio asyncio + httpx, modelo cerrado, 4 procesos |
| Corte seguro | no |
| Hardware | AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD, 6/12 núcleos, 15.9 GB |
| /health/ready previo | HTTP 200 |
| Global medido | 80063 solicitudes, 80063 exitosas, error 0.0 %, 266.88 req/s, P50 27.76 ms, P95 119.88 ms, P99 264.49 ms, máx 4509.83 ms |
| Integridad | APROBADO — generadas 81364, exitosas y correctas 81364, alteradas 0, duplicadas 0 |

| Fase | Solicitudes | req/s | P50 | P95 | P99 | Máx | API P50 | API P95 | Errores | CPU API | CPU IRIS | CPU generador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| calentamiento | 1301 | 43.37 | 10.29 | 24.27 | 33.49 | 80.73 | 6.36 | 19.98 | 0 | 6.6 | 0.9 | 10.5 |
| rampa | 11259 | 187.65 | 19.29 | 45.22 | 67.5 | 141.6 | 7.14 | 19.7 | 0 | 37.2 | 1.2 | 71.3 |
| sostenimiento | 57223 | 317.91 | 27.35 | 62.73 | 83.71 | 206.12 | 8.56 | 22.54 | 0 | 69.4 | 2.5 | 164.6 |
| pico_post_gol | 9208 | 306.93 | 105.9 | 312.27 | 614.33 | 4509.83 | 10.89 | 111.59 | 0 | 70.1 | 2.3 | 302.5 |
| recuperacion | 2373 | 79.1 | 13.12 | 60.61 | 266.35 | 727.46 | 6.59 | 40.06 | 0 | 16.5 | 0.3 | 31.1 |

Por operación en el sostenimiento:

| Operación | Solicitudes | P50 | P95 | P99 | API P50 | API P95 |
|---|---:|---:|---:|---:|---:|---:|
| comentarios_cassandra | 17042 | 31.57 | 65.83 | 86.52 | 13.18 | 25.6 |
| estadisticas_influxdb | 11592 | 29.41 | 65.3 | 86.28 | 10.96 | 23.4 |
| sesion_redis | 8505 | 21.78 | 58.19 | 77.9 | 2.92 | 13.55 |
| eventos_neo4j | 8677 | 24.71 | 60.98 | 84.29 | 5.3 | 19.87 |
| detalle_iris | 5684 | 24.07 | 58.72 | 77.08 | 5.26 | 15.8 |
| equipo_mongodb | 5723 | 22.74 | 60.52 | 81.14 | 3.87 | 17.34 |

Latencias en ms (cliente). CPU: promedio de la fase, 100 % = 1 núcleo.

## `optimizada_20261024-202348`

| Dato | Valor |
|---|---|
| Inicio / fin | 2026-10-24T20:23:48-03:00 / 2026-10-24T20:29:25-03:00 |
| Commit API (rama) | `542a1d8` (Carga), cambios sin commit en `app/`: False |
| IRIS_POOL_SIZE | 5 |
| Escenario / generador | completo / generador propio asyncio + httpx, modelo cerrado, 4 procesos |
| Corte seguro | no |
| Hardware | AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD, 6/12 núcleos, 15.9 GB |
| /health/ready previo | HTTP 200 |
| Global medido | 81554 solicitudes, 81554 exitosas, error 0.0 %, 271.85 req/s, P50 28.13 ms, P95 124.4 ms, P99 256.13 ms, máx 1021.4 ms |
| Integridad | APROBADO — generadas 82860, exitosas y correctas 82860, alteradas 0, duplicadas 0 |

| Fase | Solicitudes | req/s | P50 | P95 | P99 | Máx | API P50 | API P95 | Errores | CPU API | CPU IRIS | CPU generador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| calentamiento | 1306 | 43.53 | 9.94 | 26.42 | 33.74 | 67.36 | 4.56 | 21.34 | 0 | 5.8 | 0.9 | 12.0 |
| rampa | 11060 | 184.33 | 19.15 | 47.24 | 80.86 | 733.6 | 7.1 | 20.39 | 0 | 36.0 | 1.4 | 74.0 |
| sostenimiento | 57004 | 316.69 | 27.52 | 64.84 | 90.11 | 346.65 | 8.7 | 22.85 | 0 | 70.1 | 1.9 | 164.8 |
| pico_post_gol | 10919 | 363.97 | 98.38 | 286.61 | 432.12 | 1021.4 | 8.99 | 40.11 | 0 | 81.7 | 2.4 | 367.0 |
| recuperacion | 2571 | 85.7 | 11.55 | 26.75 | 36.01 | 185.6 | 5.81 | 19.88 | 0 | 17.2 | 1.0 | 35.6 |

Por operación en el sostenimiento:

| Operación | Solicitudes | P50 | P95 | P99 | API P50 | API P95 |
|---|---:|---:|---:|---:|---:|---:|
| comentarios_cassandra | 16960 | 31.74 | 67.71 | 91.4 | 13.13 | 25.83 |
| estadisticas_influxdb | 11555 | 29.87 | 67.64 | 94.04 | 11.2 | 23.79 |
| sesion_redis | 8465 | 21.85 | 58.11 | 82.14 | 2.98 | 13.44 |
| eventos_neo4j | 8659 | 24.74 | 64.54 | 91.68 | 5.5 | 20.51 |
| detalle_iris | 5673 | 24.56 | 63.39 | 88.73 | 5.42 | 16.79 |
| equipo_mongodb | 5692 | 22.82 | 60.44 | 84.27 | 3.87 | 16.98 |

Latencias en ms (cliente). CPU: promedio de la fase, 100 % = 1 núcleo.


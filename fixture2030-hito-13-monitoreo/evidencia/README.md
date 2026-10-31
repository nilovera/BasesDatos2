# Evidencia del Hito 13

Toda la evidencia se generó en la notebook del grupo el 30/10/2026 (rama `monitoreo`) con los scripts de `../scripts/`, salvo las capturas, que tomó el equipo. No contiene contraseñas, tokens ni URI con credenciales.

| Archivo o carpeta | Qué contiene | Generado por |
|---|---|---|
| [`prometheus_targets.md`](prometheus_targets.md) / `.json` | Estado de los 15 targets (14 esperados + cAdvisor opcional), disponibilidad en 3 capas, reglas cargadas | `verificar_targets.py` |
| [`resultados_sin_secretos/metricas_disponibles.json`](resultados_sin_secretos/metricas_disponibles.json) | Nombre de cada métrica que entrega cada job | `verificar_targets.py` |
| `resultados_sin_secretos/integridad_datos_antes.json` / `_despues.json` | 15 claves por base comparadas con las huellas del Hito 12 (última corrida: 6/6 intactas antes y después) | `verificar_datos.py` |
| [`prueba_de_falla.md`](prueba_de_falla.md) | **Resumen de la prueba de falla** (RF10) y enlaces a las tres corridas | — |
| `prueba_de_falla_redis_corte0_20261030-233034/` | Corrida 1: Redis detenido, **sin** corte rápido | `ejecutar_prueba_controlada.py` |
| `prueba_de_falla_redis_corte10v1_20261030-235008/` | Corrida 2: corte rápido v1 | ídem |
| `prueba_de_falla_redis_corte10v2_20261030-235942/` | Corrida 3: corte rápido v2 (adoptado) | ídem |
| [`comparacion_corte_rapido.md`](comparacion_corte_rapido.md) / `.png` | Tabla y gráfico antes/después de la mejora | `comparar_pruebas.py` |
| [`dashboards/`](dashboards/) | Capturas de Grafana y Prometheus | Equipo |

## Contenido de cada carpeta de prueba

| Archivo | Contenido |
|---|---|
| `README.md` | Resumen legible: tramos (antes/falla/después), detalle por base, línea de tiempo, alertas, gráfico |
| `resumen.json` | Métricas del lado cliente por tramo y por base, configuración de la API (`fixture_api_info`), conclusión de aislamiento |
| `linea_de_tiempo.json` | Momentos de `docker stop`/`start`, detección y recuperación, alertas (s desde el inicio) |
| `prometheus_series.json` | Resultado de 10 consultas PromQL cada 5 s durante toda la prueba (las consultas están en el mismo archivo) |
| `salud_dependencias.json` | `/health/dependencias` antes, durante y después |
| `solicitudes_por_segundo.csv` | Conteo por segundo, base y código HTTP (lado cliente) |
| `prueba_controlada.png` | Disponibilidad, throughput, errores y P95 en el tiempo, con la falla sombreada |

## Capturas (`dashboards/`)

| Captura | Muestra |
|---|---|
| `00a_incidente_iris_caida_verificacion.png` | Incidente real: puerto de IRIS OK pero la API no puede usarlo; target `iris` DOWN |
| `00b_incidente_iris_logs_durable.png` | Causa en los logs: `/durable/mgr: No such file or directory` |
| `01_grafana_estado_normal.png` | Sección 1 con todo en verde |
| `02_grafana_redis_caido_disponibilidad.png` | Redis CAÍDA en las dos capas, el resto OK |
| `03_grafana_errores_circuito_abierto.png` | Sección 4 al inicio de la falla: circuito de Redis ABIERTO |
| `04_prometheus_alerta_base_no_disponible.png` | `FixtureBaseNoDisponibleParaLaApi` en *firing*, con impacto y acción |
| `05_prometheus_alerta_puerto_cerrado.png` | `FixturePuertoDeBaseCerrado` en *firing* |
| `06_prometheus_alerta_errores_5xx.png` | `FixtureErrores5xxAltos` en *firing* con 12,93 % |
| `07_grafana_recuperacion.png` | Redis de nuevo en verde; tramo rojo en la línea de tiempo |
| `08_grafana_throughput_durante_falla.png` | Solicitudes por base y totales |
| `09_grafana_latencia_corte_v1.png` | Pico de latencia de Redis con el corte v1 (motivó la v2) |
| `10_grafana_comparacion_bases.png` | Métricas internas de MongoDB, Redis, IRIS e InfluxDB |
| `11_grafana_recursos.png` | CPU de la API y de la máquina Docker |
| `12_grafana_latencia_corte_v1_y_v2.png` | Latencia: pico con v1 (23:46) y sin pico con v2 (23:56) |
| `13_grafana_errores_corte_v1_y_v2.png` | Errores y 503 inmediatos del corte rápido en ambas corridas |

## Trazabilidad (RNF2)

Cada `resumen.json` registra el commit de la API (`2303e8c` = corte v1, `c2363f2` = corte v2) y su configuración (`iris_pool_size`, `corte_rapido_segundos`). La marca "con cambios sin commitear" se debe a que la carpeta `evidencia/` todavía no estaba versionada durante las corridas. Las capturas se relacionan con cada corrida por la hora visible en el eje de Grafana: corrida 2 de 23:44 a 23:50 y corrida 3 de 23:54 a 23:59.

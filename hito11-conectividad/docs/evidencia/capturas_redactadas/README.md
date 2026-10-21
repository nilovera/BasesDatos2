# Capturas redactadas

Capturas de la ejecución del Hito 11 del 21/10/2026 en la notebook de Valentino (entorno local consolidado, commit `d2bed7c`, que en el historial actual figura como `f9c389d` con el mismo contenido). Ninguna muestra passwords, tokens, URI con credenciales ni archivos `.env` (RNF7, RNF8).

| Archivo | Qué muestra | Evidencia en texto relacionada |
|---|---|---|
| `01_resumen_disponible.png` | Resumen de estados de `evaluar_conectividad.ps1`: los seis productos y la API en **disponible**; ninguna capa requerida en FALLA | `../../matriz_de_conectividad.md` |
| `02_pruebas_api.png` | Las 19 rutas de la API: operaciones exitosas (200), recursos inexistentes (404), validaciones (422) y respuestas vacías válidas, con `X-Request-ID` y `X-Process-Time-Ms` | `../resultados_api.txt` |
| `03_falla_controlada.JPG` | Falla controlada completa con MongoDB detenido: condición inicial, `docker stop`, respuesta 503 en 5,4 s con su log, ruta de control (Redis) en 200, `docker start`, recuperación y datos conservados | `../falla_controlada_detenida_mongodb.md` |
| `04_falla_cambio_de_estado.JPG` | Tabla de cambio de estado (RF20): inicial 200/ready → durante 503/degraded → después 200/ready; 64 equipos y 1.024 jugadores antes y después | `../falla_controlada_detenida_mongodb.md` |
| `05_health_dependencias_1.JPG` | `GET /health/dependencias` en Swagger: `estado_general = ready`; MongoDB, Neo4j y Cassandra en `up` | `../resultados_api.txt` |
| `06_health_dependencias_2.JPG` | Continuación: Redis, InfluxDB e InterSystems IRIS en `up`, con duración de cada chequeo | `../resultados_api.txt` |

Criterio para agregar nuevas capturas: tapar con un rectángulo sólido cualquier secreto y mantener visibles fecha, comando, host:puerto, estado y request ID, que son necesarios para interpretar el diagnóstico.

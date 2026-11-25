# Matriz de cumplimiento del Hito 13

Esta matriz separa lo que ya existe en la rama de lo que todavía debe medirse o
prepararse para la entrega final. **Implementado** no equivale a **medido** y un
objetivo no se presenta como resultado.

| Requisito de la consigna | Estado | Implementación o evidencia | Pendiente para cerrarlo |
|---|---|---|---|
| Prometheus y Grafana reproducibles | Implementado | Servicios versionados en `docker-compose.yml`, provisioning y dashboard en `infra/` | Captura final sobre el commit de entrega |
| Monitorear al menos tres componentes | Implementado | API y los cinco motores; Redis usa exporter, InfluxDB target directo y las otras dependencias salud funcional | Exporters internos de MongoDB/Cassandra/Neo4j son una mejora, no se simulan métricas que no existen |
| Disponibilidad | Implementado | `up`, `redis_up` y `fixture2030_dependency_up` | Conservar evidencia de estado normal y fallas |
| Latencia | Medido | Histograma HTTP, panel p95 y p50/p95/p99 de humo, normal, estrés y recuperación | Incorporar los resultados finales al guion de defensa |
| Volumen o throughput | Medido | 20 req/s en normal y 79,932 req/s en estrés, sin pérdida significativa | El límite máximo de capacidad no fue determinado |
| Errores | Medido | HTTP 5xx, errores por dominio y 0 errores en 8.460 requests medidos después de la corrección | Conservar captura final de la ventana de carga |
| Comparación entre componentes | Implementado | Panel temporal conjunto MongoDB/Redis/Cassandra/InfluxDB/Neo4j/Data Mart | Conservar captura final de la misma ventana temporal |
| Dos o más consultas PromQL útiles | Implementado | Consultas documentadas en `metricas_y_consultas.md` y capturadas por script | Guardar sus resultados en la ejecución final |
| Dos o más alertas justificadas | Implementado | Reglas de API, latencia, errores y cinco dependencias con umbral, duración, severidad y responsable | Verificar las alertas de Neo4j en el runtime final |
| Falla controlada y recuperación | Implementado | Scripts aislados para API, cinco motores y Data Mart con `finally`, alerta y recuperación; resultados versionados | Conservar capturas finales de Grafana de las mismas ventanas temporales |
| Inventario técnico | Implementado | `inventario_componentes.md` registra modelo, función, endpoint, mecanismo, métricas, riesgo y limitación de los cinco motores | Revisarlo ante cambios del runtime final |
| Reproducibilidad y trazabilidad | Implementado | Compose, versiones fijadas, `sourceCommit`, rama, escenario, estado de servicios y manifiesto SHA-256 | Ejecutar la captura final y revisar secretos antes del commit |
| Pruebas de humo, tráfico normal y estrés | Medido | Semillas 2029/2030/2031; 30, 3.600 y 4.800 requests; recursos y resultados reproducibles | Agregar captura de Grafana de las ventanas elegidas |
| SLI, SLO, límites y recuperación | Medido | Humo y normal cumplieron error rate/p95/p99; estrés sostuvo 79,932 req/s y el humo posterior validó recuperación | El SLA continúa como propuesta, no como compromiso contractual |
| Defensa de 20 minutos y plan alternativo | Pendiente | Los archivos de evidencia permiten una demostración sin depender solo de la interfaz | Preparar guion, capturas y resultados legibles si Grafana no estuviera disponible |
| Ausencia de secretos | Implementado como control | La captura no exporta variables de entorno ni `docker inspect`; `.env` no se versiona | Revisión humana de JSON, TXT y capturas antes de cada commit |

## Criterio de cierre

El Hito 13 no se declara completamente cerrado mientras falten las capturas
finales y el guion de defensa. La evidencia funcional, de fallas y de carga ya
fue medida. Se demuestra capacidad de al menos 80 req/s en el laboratorio, no
un límite máximo ni un SLA contractual.

# Matriz de cumplimiento del Hito 13

Esta matriz separa lo que ya existe en la rama de lo que todavía debe medirse o
prepararse para la entrega final. **Implementado** no equivale a **medido** y un
objetivo no se presenta como resultado.

| Requisito de la consigna | Estado | Implementación o evidencia | Pendiente para cerrarlo |
|---|---|---|---|
| Prometheus y Grafana reproducibles | Implementado | Servicios versionados en `docker-compose.yml`, provisioning y dashboard en `infra/` | Captura final sobre el commit de entrega |
| Monitorear al menos tres componentes | Implementado | API y los cinco motores; Redis usa exporter, InfluxDB target directo y las otras dependencias salud funcional | Exporters internos de MongoDB/Cassandra/Neo4j son una mejora, no se simulan métricas que no existen |
| Disponibilidad | Implementado | `up`, `redis_up` y `fixture2030_dependency_up` | Conservar evidencia de estado normal y fallas |
| Latencia | Implementado | Histograma HTTP y panel p95 | Medir p50/p95/p99 en los tres escenarios de carga |
| Volumen o throughput | Implementado | Tasa de solicitudes y contadores de dominio | Fijar intensidad y duración del workload final |
| Errores | Implementado | HTTP 5xx en ventana de 5 minutos y errores por dominio | Validar razón de errores bajo tráfico normal y estrés |
| Comparación entre componentes | Implementado | Panel temporal conjunto MongoDB/Redis/Cassandra/InfluxDB/Neo4j/Data Mart | Conservar captura final de la misma ventana temporal |
| Dos o más consultas PromQL útiles | Implementado | Consultas documentadas en `metricas_y_consultas.md` y capturadas por script | Guardar sus resultados en la ejecución final |
| Dos o más alertas justificadas | Implementado | Reglas de API, latencia, errores y cinco dependencias con umbral, duración, severidad y responsable | Verificar las alertas de Neo4j en el runtime final |
| Falla controlada y recuperación | Implementado | Scripts aislados para API, cinco motores y Data Mart con `finally`, alerta y recuperación; resultados versionados | Conservar capturas finales de Grafana de las mismas ventanas temporales |
| Inventario técnico | Implementado | `inventario_componentes.md` registra modelo, función, endpoint, mecanismo, métricas, riesgo y limitación de los cinco motores | Revisarlo ante cambios del runtime final |
| Reproducibilidad y trazabilidad | Implementado | Compose, versiones fijadas, `sourceCommit`, rama, escenario, estado de servicios y manifiesto SHA-256 | Ejecutar la captura final y revisar secretos antes del commit |
| Pruebas de humo, tráfico normal y estrés | Implementado; ejecución pendiente | Simulador reproducible con semillas 2029/2030/2031, mezcla versionada, concurrencia y recursos | Ejecutar desde commit limpio y conservar resultados comparables |
| SLI, SLO, límites y recuperación | Implementado; ejecución pendiente | Error rate, p95, p99, throughput, CPU y memoria; SLO de laboratorio separados del SLA | Medir los tres perfiles, ejecutar humo después del estrés y revisar objetivos |
| Defensa de 20 minutos y plan alternativo | Pendiente | Los archivos de evidencia permiten una demostración sin depender solo de la interfaz | Preparar guion, capturas y resultados legibles si Grafana no estuviera disponible |
| Ausencia de secretos | Implementado como control | La captura no exporta variables de entorno ni `docker inspect`; `.env` no se versiona | Revisión humana de JSON, TXT y capturas antes de cada commit |

## Criterio de cierre

El Hito 13 no se declara completamente cerrado mientras falten las pruebas de
carga y el guion de defensa. La evidencia funcional y de fallas ya está
versionada; los resultados de capacidad siguen pendientes y no se reemplazan
por objetivos.

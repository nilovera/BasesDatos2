# Matriz de cumplimiento del Hito 13

Esta matriz separa lo que ya existe en la rama de lo que todavía debe medirse o
prepararse para la entrega final. **Implementado** no equivale a **medido** y un
objetivo no se presenta como resultado.

| Requisito de la consigna | Estado | Implementación o evidencia | Pendiente para cerrarlo |
|---|---|---|---|
| Prometheus y Grafana reproducibles | Implementado | Servicios versionados en `docker-compose.yml`, provisioning y dashboard en `infra/` | Captura final sobre el commit de entrega |
| Monitorear al menos tres componentes | Implementado | API, MongoDB, Redis, Cassandra e InfluxDB; Redis usa exporter, InfluxDB target directo y las otras dependencias salud funcional | Exporters internos de MongoDB/Cassandra son una mejora, no se simulan métricas que no existen |
| Disponibilidad | Implementado | `up`, `redis_up` y `fixture2030_dependency_up` | Conservar evidencia de estado normal y fallas |
| Latencia | Implementado | Histograma HTTP y panel p95 | Medir p50/p95/p99 en los tres escenarios de carga |
| Volumen o throughput | Implementado | Tasa de solicitudes y contadores de dominio | Fijar intensidad y duración del workload final |
| Errores | Implementado | HTTP 5xx en ventana de 5 minutos y errores por dominio | Validar razón de errores bajo tráfico normal y estrés |
| Comparación entre componentes | Implementado | Panel temporal conjunto MongoDB/Redis/Cassandra/InfluxDB | Agregar Neo4j al incorporarlo |
| Dos o más consultas PromQL útiles | Implementado | Consultas documentadas en `metricas_y_consultas.md` y capturadas por script | Guardar sus resultados en la ejecución final |
| Dos o más alertas justificadas | Implementado | Reglas de API, latencia, errores y cuatro dependencias con umbral, duración, severidad y responsable | Verificar las alertas nuevas en el runtime final |
| Falla controlada y recuperación | Implementado; evidencia InfluxDB pendiente | Scripts aislados para API, MongoDB, Redis, Cassandra e InfluxDB con `finally`, alerta y recuperación | Ejecutar InfluxDB desde un commit limpio y versionar `resultado.json` y captura |
| Inventario técnico | Implementado | `inventario_componentes.md` registra modelo, función, endpoint, mecanismo, métricas, riesgo y limitación | Extenderlo al sumar Neo4j |
| Reproducibilidad y trazabilidad | Implementado | Compose, versiones fijadas, `sourceCommit`, rama, escenario, estado de servicios y manifiesto SHA-256 | Ejecutar la captura final y revisar secretos antes del commit |
| Pruebas de humo, tráfico normal y estrés | Diseñado | T04-T05 definen semillas y datos mínimos | Implementar simulador, ejecutar y conservar resultados comparables |
| SLI, SLO, límites y recuperación | Diseñado | T06 y antecedentes de capacidad separan objetivo, estimación y medición | Obtener resultados después de integrar los cinco motores |
| Defensa de 20 minutos y plan alternativo | Pendiente | Los archivos de evidencia permiten una demostración sin depender solo de la interfaz | Preparar guion, capturas y resultados legibles si Grafana no estuviera disponible |
| Ausencia de secretos | Implementado como control | La captura no exporta variables de entorno ni `docker inspect`; `.env` no se versiona | Revisión humana de JSON, TXT y capturas antes de cada commit |

## Criterio de cierre

El Hito 13 no se declara completamente cerrado mientras falten la ejecución y
evidencia de InfluxDB, Neo4j, las pruebas de carga y el guion de defensa. El
estado actual deja una base verificable para incorporar el motor restante sin
arrastrar errores de observabilidad o trazabilidad.

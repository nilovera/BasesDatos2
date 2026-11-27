# Integración de la rama final

La rama `trabajo-final` integra selectivamente los componentes de los hitos.
No hereda mediante merges completos configuraciones, credenciales o catálogos
incompatibles. La procedencia se conserva en [fuentes](fuentes.md).

| Área | Estado vigente | Justificación y validación |
|---|---|---|
| Fundamentación y alcance | Revisados | Responsabilidades y límites coherentes con la implementación |
| Identidad común | Implementada | Catálogo reproducible de 64 equipos y 1.024 jugadores |
| MongoDB | Implementado y ejecutado en Docker | Replica set local, validadores, índices y transacción oficial |
| Redis | Implementado y ejecutado en Docker | Caché, sesiones, persistencia y falla controlada |
| Cassandra | Comentarios y auditoría ejecutados en Docker | Vistas por consulta, buckets e idempotencia; resultado de auditoría registrado |
| InfluxDB | Implementado y ejecutado en Docker | Series, retención, ingesta y consultas temporales |
| Neo4j | Implementado y ejecutado en Docker | Catálogo, recorridos y relaciones deportivas proyectadas |
| Data Mart | Implementado y ejecutado en Docker | Estrella, ETL, pool y comparaciones registradas |
| Outbox | Implementado y con convergencia registrada | Entrega idempotente a Redis y Neo4j |
| Observabilidad | Implementada y ejecutada | Salud, métricas, alertas y fallas controladas |
| Carga y simulación | Ejecutadas | Lectura mixta y partido reproducible con front |
| Auditoría | Implementada y comprobada con HTTP en Docker | 25 pruebas específicas dentro de 170 y resultado integrado OK con cero duplicados |

IRIS no integra el despliegue, conforme a
[ADR-001](diseno/ADR-001-exclusion-iris.md). Los estados anteriores se respaldan
en el [registro de validación](estado_validacion.md), que conserva versiones y
límites de cada ejecución.

## Política de evolución

Cada incorporación identifica su origen, adapta IDs y contratos, elimina
dependencias ajenas y registra las pruebas pertinentes. El diseño, la
implementación, la ejecución y la medición constituyen evidencias distintas.
La evaluación de producción requiere topologías redundantes, autenticación
real y recuperación probada, además de mediciones representativas.

Las extensiones y los puntos revisados se detallan en
[tareas de integración](tareas_integracion_final.md) y
[registro de trazabilidad](pendientes.md). La preparación de la defensa no se
presenta como acreditación de una exposición realizada o una aprobación externa.

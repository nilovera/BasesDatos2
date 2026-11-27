# Matriz de cobertura del Hito 13

Implementado no equivale a medido: cada fila relaciona una capacidad con su
resultado registrado y su alcance. El
[estado de validación](../estado_validacion.md) enlaza las ejecuciones.

| Área | Estado y evidencia | Alcance o límite |
|---|---|---|
| Prometheus y Grafana reproducibles | Compose, provisioning, salud y captura integrada registrados | Una instancia local de cada servicio |
| Monitoreo de componentes | API, cinco motores, Outbox y Data Mart instrumentados | Se distingue target directo, collector nativo y salud funcional |
| Disponibilidad | Valores de salud y cambios 1–0–1 en fallas controladas | No es porcentaje anual ni HA |
| Latencia | Histogramas HTTP y percentiles del cliente de carga | Ventanas y métodos de cálculo distintos |
| Throughput | Normal 19,998 req/s; estrés 79,932 req/s | Capacidad máxima no determinada |
| Errores | Cero en 8.460 solicitudes de los perfiles corregidos y recuperación | El humo diagnóstico falló latencia y se conserva por separado |
| Comparación entre componentes | Salud temporal y panel operativo de API/MongoDB/Redis/Cassandra/InfluxDB/Neo4j | Outbox y Data Mart conservan métricas aunque no aparezcan en todos los paneles |
| Consultas PromQL | Consultas documentadas y resultados de captura integrada | Métricas internas completas no disponibles para todos los motores |
| Alertas justificadas | Reglas versionadas, umbrales y estados firing registrados | La prueba no acredita que se hayan disparado todas las reglas de saturación |
| Falla y recuperación | Pruebas de API, motores y worker Outbox registradas | Parada/reinicio con volúmenes; sin failover regional |
| Reproducibilidad | Commit, escenario, servicios y manifiestos | La evidencia identifica su versión de origen |
| Pruebas de humo, tráfico normal y estrés | Ejecutadas con semillas 2029/2030/2031; recursos y resultados conservados | Mezcla de lecturas, no benchmark de escrituras masivas |
| SLI y SLO | Humo cumplió cero errores, p95 ≤750 ms y p99 ≤1.500 ms; normal, error ≤1 %, p95 ≤500 ms y p99 ≤1.000 ms | Estrés informativo; sin SLA contractual |
| Defensa de 20 minutos y alternativa de demostración | Documentación, guías y evidencias disponibles para preparar la exposición | No se acredita una exposición realizada ni su evaluación |
| Protección de datos | Captura sin volcado del entorno y revisión de artefactos | Revisar también cada evidencia nueva antes de publicarla |

## Evaluación del alcance

La cobertura técnica tiene evidencia funcional, de fallas y de carga. Los
resultados se conservan por ejecución y commit, con límites explícitos de
interpretación. La aceptación externa de la entrega no
se deduce automáticamente de esta matriz.

El incremento 15 agrega auditoría con validación unitaria y prueba HTTP
integrada exitosa en Docker. Su resultado se conserva con fecha, acciones y
comprobaciones de idempotencia, acceso y entrega. Ese escenario no amplía
las conclusiones de capacidad o distribución de las evidencias anteriores.

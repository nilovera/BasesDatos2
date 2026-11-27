# Metricas y consultas PromQL

Prometheus recolecta cada 5 segundos. Las ventanas siguientes son decisiones
de laboratorio y deben conservarse junto con la fecha, commit y escenario de
cada ejecucion.

## Simulador de partido

- `fixture2030_simulation_running`: `1` mientras avanza el reloj lógico.
- `fixture2030_simulation_second`: segundo alcanzado entre `0` y `5400`.
- `fixture2030_simulation_speed`: multiplicador activo (`30` en la demo).
- `increase(fixture2030_simulation_errors_total[5m])`: fallas recuperables del motor.

## Disponibilidad de la API

```promql
up{job="fixture2030-api"}
```

- Unidad: booleano (`1` disponible, `0` no disponible).
- Periodo: ultimo scrape, con frecuencia de 5 segundos.
- Uso: panel de disponibilidad y alerta `Fixture2030ApiDown`.

## Latencia p95

```promql
histogram_quantile(0.95, sum by (le) (rate(fixture2030_http_request_duration_seconds_bucket[5m])))
```

- Unidad: segundos.
- Periodo: ventana movil de 5 minutos.
- Uso: observar la latencia del 95 % de las solicitudes sin confundirla con un
  promedio. Las ejecuciones de carga ya registran latencia; esta consulta estima el
  percentil del histograma en su ventana, sin sustituir los percentiles del cliente.

## Volumen de solicitudes

```promql
sum(rate(fixture2030_http_requests_total[1m]))
```

- Unidad: solicitudes por segundo.
- Periodo: ventana movil de 1 minuto.
- Uso: correlacionar carga con latencia y errores.

## Proporcion de errores 5xx

```promql
sum(rate(fixture2030_http_requests_total{route!="/health",status=~"5.."}[2m]))
/
clamp_min(sum(rate(fixture2030_http_requests_total{route!="/health"}[2m])), 0.001)
```

- Unidad: proporcion entre 0 y 1; multiplicar por 100 para porcentaje.
- Periodo: ventana movil de 2 minutos.
- Uso: alerta de tasa de error superior al 5 %. Se excluye `/health` para que
  los sondeos internos no oculten errores de tráfico funcional.

## Disponibilidad funcional de MongoDB

```promql
fixture2030_dependency_up{dependency="mongodb"}
```

- Unidad: booleano (`1` existe PRIMARY, `0` no está disponible).
- Periodo: último chequeo de `/health`, ejecutado también por el healthcheck.
- Uso: diferenciar una API viva de la imposibilidad de confirmar eventos
  oficiales. Se complementa con el collector nativo de la API descrito más abajo.

## Disponibilidad de Redis

```promql
redis_up{job="fixture2030-redis"}
```

- Unidad: booleano (`1` disponible, `0` no disponible).
- Periodo: ultimo scrape, cada 5 segundos.
- Uso: distinguir una clave ausente de una dependencia Redis caida.

## Convergencia de Outbox

```promql
up{job="fixture2030-outbox"}
```

Informa si Prometheus puede recolectar al consumidor separado de la API.

```promql
fixture2030_outbox_pending{consumer="redis"}
fixture2030_outbox_oldest_pending_seconds{consumer="redis"}
fixture2030_outbox_failed{consumer="redis"}
```

Estas consultas separan profundidad, edad y agotamiento de reintentos. Una cola
temporalmente mayor que cero es válida; el riesgo aparece cuando no converge o
el mensaje más antiguo supera el objetivo local de 30 segundos. La etiqueta histórica `consumer="redis"`
se conserva, aunque el worker también proyecta Neo4j.

## Presion de memoria Redis

```promql
redis_memory_used_bytes / redis_memory_max_bytes
```

- Unidad: proporcion de memoria configurada.
- Periodo: valor instantaneo recolectado cada 5 segundos.
- Uso: anticipar la activacion de `allkeys-lfu`; el umbral inicial es 85 %.

## Tasa de aciertos del cache

```promql
sum(rate(redis_keyspace_hits_total[5m]))
/
clamp_min(sum(rate(redis_keyspace_hits_total[5m])) + sum(rate(redis_keyspace_misses_total[5m])), 0.001)
```

- Unidad: proporcion entre 0 y 1.
- Periodo: ventana movil de 5 minutos.
- Uso: evaluar Cache-Aside junto con latencia, consistencia y memoria; una tasa
  alta por si sola no garantiza un diseño correcto.

## Disponibilidad funcional de Cassandra

```promql
fixture2030_dependency_up{dependency="cassandra"}
```

- Unidad: booleano (`1` disponible, `0` no disponible).
- Periodo: se actualiza cuando la API ejecuta `/health`.
- Uso: distinguir una API disponible de comentarios temporalmente degradados.

## Operaciones de comentarios

```promql
sum by (operation, result) (rate(fixture2030_comment_operations_total[5m]))
```

- Unidad: operaciones por segundo.
- Periodo: ventana móvil de 5 minutos.
- Uso: observar publicaciones, replays, lecturas, moderaciones y errores.
- Límite: compactions, tombstones y latencia interna requieren JMX en el
  escenario Cassandra RF=3.

## Comparación de dependencias

```promql
fixture2030_dependency_up{dependency=~"mongodb|redis|cassandra|influxdb|neo4j|datamart"}
```

- Unidad: booleano por dependencia.
- Periodo: último chequeo funcional de la API.
- Uso: comparar en una misma ventana qué subsistema se degradó sin confundirlo
  con la disponibilidad del proceso HTTP.

## Disponibilidad de InfluxDB

```promql
fixture2030_dependency_up{dependency="influxdb"}
```

- Unidad: booleano (`1` responde con autenticación, `0` no disponible).
- Periodo: último chequeo de `/health` de la API.
- Uso: demostrar degradación aislada de telemetría sin confundirla con la
  continuidad del partido oficial.

El target directo también se consulta con:

```promql
up{job="fixture2030-influxdb"}
```

## Operaciones de telemetría

```promql
sum by (operation, result) (rate(fixture2030_telemetry_operations_total[5m]))
```

- Unidad: operaciones por segundo.
- Periodo: ventana móvil de 5 minutos.
- Uso: observar escrituras de posiciones/estadísticas, consultas, mapas de
  calor, agregaciones y errores.

## Disponibilidad y operaciones de Neo4j

```promql
fixture2030_dependency_up{dependency="neo4j"}
```

La métrica vale `1` cuando la API puede ejecutar una consulta Bolt y `0` cuando
los recorridos están degradados. No equivale a métricas internas del proceso.

```promql
sum by (operation, result) (rate(fixture2030_graph_operations_total[5m]))
```

Permite observar resúmenes, rivales, recomendaciones, caminos y errores por
segundo durante una ventana móvil de cinco minutos.

## Disponibilidad y operaciones del Data Mart

```promql
fixture2030_dependency_up{dependency="datamart"}
```

```promql
sum by (operation, result) (rate(fixture2030_datamart_operations_total[5m]))
```

Miden la salud funcional de PostgreSQL y la tasa de refresh/consultas. No son
métricas internas de PostgreSQL; CPU, buffers y locks requieren un exporter.

Prometheus conserva siete días en el laboratorio. Esa retención permite revisar
la demostración local, pero no representa una política productiva ni sustituye
la evidencia versionada por ejecución.


## Métricas nativas de MongoDB

El collector de la API consulta `serverStatus` y `dbStats` durante el scrape.
No expone documentos ni credenciales y no requiere un exporter separado.

```promql
fixture2030_mongodb_metrics_up
fixture2030_mongodb_connections
sum by (operation) (rate(fixture2030_mongodb_operations_total[5m]))
fixture2030_mongodb_data_bytes
fixture2030_mongodb_storage_bytes
fixture2030_mongodb_index_bytes
```

La disponibilidad del collector se interpreta por separado de la de la API.
Los tamaños son valores instantáneos, no tasas. Los IDs de usuario o solicitud
no se agregan como etiquetas de estas métricas.

Resultados de ejecución y límites: [estado de validación](../estado_validacion.md).

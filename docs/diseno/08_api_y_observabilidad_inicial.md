# Paso 8 — API y observabilidad inicial

## Decisión

El primer recorrido ejecutable usa FastAPI y PyMongo. MongoDB sigue siendo la
fuente oficial: una única transacción actualiza el partido, inserta el evento e
inserta la Outbox. Cassandra, Redis, InfluxDB y Neo4j serán proyecciones o
servicios especializados y no confirmarán el hecho deportivo.

## Idempotencia

La API calcula SHA-256 sobre método, ruta, partido y JSON canónico. La clave y
el hash quedan almacenados dentro del evento.

| Caso | Resultado |
|---|---|
| Clave nueva | `201`, evento y Outbox creados |
| Misma clave y body | `200`, respuesta original, sin nueva escritura |
| Misma clave y otro body | `409 IDEMPOTENCY_KEY_REUSED` |
| Conflicto concurrente | reintento transaccional o `409 VERSION_CONFLICT` |

El contador global produce IDs `EVE-000001`. La secuencia por partido y la
versión del agregado se incrementan dentro de la misma transacción.

## Observabilidad

Prometheus consulta `/metrics` cada cinco segundos. Grafana recibe la fuente y
el dashboard mediante provisioning versionado. La primera vista incluye:

- disponibilidad de la API;
- solicitudes por segundo;
- latencia HTTP p95;
- errores 5xx;
- eventos confirmados por tipo;
- profundidad pendiente de Outbox.

InfluxDB no reemplazará a Prometheus: InfluxDB guardará telemetría deportiva;
Prometheus, indicadores técnicos del sistema. Grafana podrá consultar ambos.

## Seguridad de laboratorio

Los puertos se enlazan a `127.0.0.1`. No hay autenticación MongoDB ni TLS en
este incremento. Grafana utiliza una credencial local reemplazable. Estas
decisiones reducen fricción para la demostración y no representan un despliegue
productivo.

## Limitaciones declaradas

- MongoDB tiene un solo miembro: transacciones sin tolerancia a caída del nodo.
- La API usa un worker; el escalado se decidirá después de medir.
- La participación se valida por plantel activo, todavía no por intervalo exacto.
- La Outbox se escribe pero aún no tiene consumidores.
- El dashboard no demuestra por sí solo un SLO.

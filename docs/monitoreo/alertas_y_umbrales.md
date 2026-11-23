# Alertas y umbrales iniciales

Los umbrales son hipotesis operativas para el laboratorio. Se ajustaran con
los escenarios de humo, trafico normal y estres; no constituyen por si solos un
SLA medido.

| Alerta | Condicion y duracion | Riesgo | Responsable | Accion inicial |
|---|---|---|---|---|
| `Fixture2030ApiDown` | `up == 0` durante 30 s | indisponibilidad del flujo deportivo | Plataforma | revisar contenedor, logs, MongoDB y reiniciar solo el servicio afectado |
| `Fixture2030ApiHighErrorRate` | mas de 5 % de HTTP 5xx durante 2 min | operaciones fallidas aunque el proceso siga activo | Backend | correlacionar endpoint, excepciones y estado de MongoDB |
| `Fixture2030OutboxBacklog` | mas de 100 pendientes durante 5 min | demora de convergencia entre motores | Integracion | revisar consumidor y reintentos sin eliminar mensajes |
| `Fixture2030RedisDown` | `redis_up == 0` durante 30 s | sesiones no disponibles y cache en bypass | Plataforma | revisar contenedor, volumen, configuracion y conectividad |
| `Fixture2030RedisHighMemory` | mas de 85 % de `maxmemory` durante 5 min | evicciones y perdida anticipada de claves temporales | Plataforma | revisar TTL, LFU, cardinalidad y capacidad |
| `Fixture2030RedisEvictions` | al menos una eviction en 5 min durante 1 min | presion de memoria o TTL/politica inadecuados | Backend | correlacionar hit rate, memoria y escenario de carga |

La alerta de API ya posee una prueba controlada. Redis se verificara mediante
reinicio y recuperacion; la alerta de memoria se ejercitara durante los
escenarios de carga. Outbox quedara funcionalmente verificable cuando exista
el consumidor de proyecciones.

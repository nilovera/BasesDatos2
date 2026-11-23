# Alertas y umbrales iniciales

Los umbrales son hipotesis operativas para el laboratorio. Se ajustaran con
los escenarios de humo, trafico normal y estres; no constituyen por si solos un
SLA medido.

| Alerta | Condicion y duracion | Riesgo | Responsable | Accion inicial |
|---|---|---|---|---|
| `Fixture2030ApiDown` | `up == 0` durante 30 s | indisponibilidad del flujo deportivo | Plataforma | revisar contenedor, logs, MongoDB y reiniciar solo el servicio afectado |
| `Fixture2030ApiHighErrorRate` | mas de 5 % de HTTP 5xx durante 2 min | operaciones fallidas aunque el proceso siga activo | Backend | correlacionar endpoint, excepciones y estado de MongoDB |
| `Fixture2030OutboxBacklog` | mas de 100 pendientes durante 5 min | demora de convergencia entre motores | Integracion | revisar consumidor y reintentos sin eliminar mensajes |

La primera alerta puede comprobarse ahora mediante una falla controlada. La de
Outbox quedara funcionalmente verificable cuando exista el consumidor de
proyecciones.

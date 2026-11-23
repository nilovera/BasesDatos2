# Evidencia, trazabilidad y limitaciones

Cada ejecucion debe registrar como minimo: fecha, commit, rama, escenario,
estado de contenedores, resultado de pruebas y consultas relevantes. Las
capturas deben indicar la misma ventana temporal que los archivos de la
ejecucion.

## Clasificacion obligatoria

- **Implementado:** existe configuracion o codigo versionado.
- **Medido:** una ejecucion identificada produjo el valor observado.
- **Objetivo:** valor que se pretende alcanzar; no es un resultado.
- **Estimado:** aproximacion que requiere validacion.
- **No obtenido:** la medicion fallo o el componente todavia no existe.

## Seguridad de la evidencia

No se versionan variables de entorno completas, tokens, contraseñas, cadenas
de conexion con credenciales ni archivos `.env`. Antes del commit se revisan
los JSON, TXT y capturas generados. La contraseña local predeterminada de
Grafana es solo de laboratorio y debe cambiarse si el entorno deja de ser
local.

## Limitaciones actuales

- MongoDB se observa indirectamente mediante la API; falta su exporter.
- Cassandra, InfluxDB y Neo4j aun no son parte de este incremento.
- Redis es standalone: RDB/AOF permiten recuperacion local, no alta disponibilidad.
- No hay resultados de capacidad, SLO, RPO ni RTO.
- Las alertas no tienen todavia un canal externo de notificacion.
- Un replica set MongoDB de un miembro no demuestra alta disponibilidad.

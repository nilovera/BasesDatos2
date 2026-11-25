# Evidencia, trazabilidad y limitaciones

Cada ejecucion debe registrar como minimo: fecha, commit, rama, escenario,
estado de contenedores, resultado de pruebas y consultas relevantes. Las
capturas deben indicar la misma ventana temporal que los archivos de la
ejecucion.

`capturar_evidencia.ps1` exige por defecto un árbol Git limpio, ejecuta las
verificaciones mediante procesos con stdout y stderr separados y genera un
manifiesto SHA-256. Esto evita que la salida informativa de `unittest` sea
interpretada como error por Windows PowerShell 5.1.

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

- MongoDB se observa indirectamente mediante la API; falta su exporter. La
  caída controlada verifica estado degradado, métrica y alerta específicas.
- Cassandra forma parte del entorno y expone salud funcional desde la API; las métricas JMX internas quedan pendientes para el escenario RF=3.
- InfluxDB ya forma parte del entorno, con target directo y falla controlada;
  todavía falta ejecutar y versionar su evidencia sobre el equipo del grupo.
- Neo4j forma parte del entorno mediante salud funcional y contadores de API;
  no expone métricas internas ni clustering en Community Edition.
- El Data Mart usa salud funcional y contadores de API; falta exporter de PostgreSQL
  y una medición con volumen suficiente para cerrar Hito 12.
- Redis es standalone: RDB/AOF permiten recuperacion local, no alta disponibilidad.
- No hay resultados de capacidad, SLO, RPO ni RTO.
- Las alertas no tienen todavia un canal externo de notificacion.
- Un replica set MongoDB de un miembro no demuestra alta disponibilidad.
- Las ejecuciones finales y capturas de Grafana todavía deben generarse sobre
  un commit limpio y luego versionarse sin secretos.

# Tareas posteriores a la integración de las bases

MongoDB, Cassandra, Redis, InfluxDB, Neo4j y el Data Mart ya poseen incrementos
integrados. Las siguientes tareas forman parte de la validación final y no deben
omitirse.

## T01 — Usuarios sintéticos durables

- Agregar colección `usuarios` en MongoDB.
- Generar identidades sintéticas reproducibles, sin datos personales reales.
- Mantener perfiles durables en MongoDB y sesiones con TTL en Redis.
- Validar referencias de comentarios y acciones.

**Aceptación:** recrear el laboratorio con la misma semilla produce los mismos
usuarios; iniciar y cerrar sesión no pierde el perfil durable.

## T02 — Asistencias en goles

- Agregar `asistenteJugadorId` opcional al evento `GOL`.
- Validar que goleador y asistente sean distintos, pertenezcan al equipo y estén
  participando en el minuto del evento.
- Proyectar la asistencia a estadísticas y relaciones sin duplicarla al reintentar.

**Aceptación:** un gol con asistencia válida converge en MongoDB, Redis,
InfluxDB y Neo4j; una asistencia inválida se rechaza sin escritura parcial.

## T03 — Telemetría y mapas de calor

- Endpoint de carga por lotes para posiciones `x/y`: implementado.
- Generar muestras solamente durante la participación del jugador.
- Persistencia en InfluxDB con timestamp y etiquetas controladas: implementada.
- Cursor estable para timestamps compartidos y mapa de calor: implementados.
- Falta unir alineaciones y sustituciones para rechazar muestras fuera de la
  participación real; el catálogo actual solo permite validar plantel/equipo.

**Aceptación:** sustituciones delimitan las muestras del titular y suplente; el
mapa de calor se puede reproducir desde los puntos almacenados.

## T04 — Simulador reproducible

- Usar `DATA_SEED=2030` para el dataset base.
- Separar la semilla de datos de la semilla del workload.
- Registrar `runId`, commit, escenario, semillas, duración y concurrencia.
- Enviar operaciones por la API; solamente el bootstrap puede cargar directo.

**Aceptación:** repetir escenario y semillas conserva datos y secuencia lógica;
los resultados medidos pueden compararse entre commits.

## T05 — Escenarios de carga

| Escenario | Workload seed | Propósito |
|---|---:|---|
| Humo | `203001` | Confirmar flujos críticos con carga mínima y cero errores |
| Tráfico normal | `203002` | Comprobar SLO con carga esperada y estable |
| Estrés | `203003` | Aumentar carga hasta encontrar degradación y recuperación |

La intensidad depende de usuarios virtuales, tasa, duración y mezcla de
operaciones; la semilla solo hace reproducible la selección pseudoaleatoria.

El escenario de estrés debe incluir una ejecución específica de InfluxDB hacia
el objetivo académico de 10M+ puntos, sin confundir la prueba funcional de
1.080 puntos con una prueba de escala. Debe medir batching, ingesta, consultas
acotadas, cardinalidad, recursos y efecto de la retención.

**Aceptación:** cada ejecución conserva configuración y resultados sin secretos,
expone p50/p95/p99, throughput, errores, concurrencia y retraso de Outbox.

## T06 — SLI, SLO y SLA propuesto

- Definir SLI antes de fijar umbrales.
- Validar SLO de latencia, errores, disponibilidad y propagación bajo tráfico normal.
- Presentar el SLA como compromiso propuesto, no como resultado medido.
- Documentar qué umbral se rompe durante estrés y cómo se recupera el sistema.

**Aceptación:** Grafana y la evidencia distinguen objetivo, medición, estimación y
compromiso; ninguna capacidad se presenta como observada sin ejecución.

## T07 — Evidencia automática y saneamiento de ejecuciones

- `capturar_evidencia.ps1` ya separa stdout/stderr, exige commit limpio y
  genera manifiesto SHA-256.
- Las fallas de MongoDB, Redis y Cassandra ya generan resultados persistentes
  con valores antes/durante/después y recuperación. El mismo mecanismo quedó
  implementado para InfluxDB y Neo4j; Neo4j requiere ejecución/versionado en el equipo.
- Conservar y revisar la evidencia válida de la falla controlada de API.
- Excluir o reemplazar la captura incompleta `20261123T192234Z`.
- Adjuntar capturas de Grafana con la misma ventana temporal y commit.

**Aceptación:** cada escenario crea una carpeta autocontenida con commit,
servicios, pruebas, métricas, alertas y recuperación, sin secretos.

## T08 — Cierre cuantitativo del Hito 12

- Usar el simulador de T04/T05 para cargar un volumen analítico representativo.
- Ejecutar exactamente la misma consulta operacional y de Data Mart.
- Conservar p50/p95/p99, throughput, errores, concurrencia, CPU y memoria.
- Explicar el cuello de botella, la mejora aplicada y el costo de frescura eventual.

**Aceptación:** una ejecución versionada demuestra o refuta cuantitativamente la
mejora; la línea base de un solo partido no se presenta como conclusión.

## T09 — Convergencia de Outbox

- Worker separado de la API con lease recuperable: implementado.
- Proyección Redis mediante Lua y deduplicación por `eventoId`: implementada.
- Backoff, máximo de intentos y cola `FALLIDO`: implementados.
- Métricas de profundidad, edad, reintentos, replay y fallidos: implementadas.
- Falla controlada de worker y replay posterior a la publicación: implementados.

**Aceptación:** detener el worker no impide confirmar el evento; al recuperarlo
la cola converge a cero y un replay no crea una segunda copia en Redis.

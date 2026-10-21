# Limitaciones y coherencia con el TPO

## 1. Limitaciones

### Del entorno de laboratorio

- **Origen único:** las pruebas se ejecutan desde la notebook donde corre la API. Un despliegue con la API en contenedor o en otra máquina requeriría repetir el diagnóstico desde ese origen (ver `topologia_y_entornos.md`, sección 5).
- **Sin autenticación en Cassandra y Redis:** las capas de autenticación de ambos productos se registran como `N/A`. No se simula una autenticación que no existe.
- **Puertos expuestos:** MongoDB (27017) y Redis (6379) se publican en todas las interfaces de la notebook. InfluxDB e IRIS solo en `127.0.0.1`. Es aceptable para un laboratorio local, pero no para producción.
- **Compose de Neo4j y Cassandra fuera del repositorio:** el mapeo de puertos de esos dos productos se toma de `docker inspect` en tiempo de ejecución (modo `tcp`) y no de un archivo versionado.
- **Datos sintéticos:** las pruebas leen los datos de demostración cargados en los hitos 4 a 9 (EQ-01, PAR-0001, ventana 2030-06-13 20:00–20:01). En Cassandra la partición de demostración es `203006131800` cuando está la carga masiva del Hito 6, y `203006132000` en el entorno local consolidado, que carga solo la muestra (`CASSANDRA_BUCKET_DEMO`). Si otra notebook no los tiene, las lecturas dan `ADVERTENCIA` (`recurso_inexistente`) y no `FALLA`.

### De las herramientas

- **Clientes CLI:** `mongosh`, `cypher-shell`, `cqlsh`, `redis-cli`, `influxdb3` e `iris` no se instalan en la notebook. Con `-Cli` se ejecutan dentro de cada contenedor (otro origen). Si no están disponibles, el resultado es `SKIP`.
- **Clasificación de IRIS por mensaje:** el driver DB-API resuelve handshake, autenticación y namespace en un único `connect()`. La capa se deduce del texto del error. Si una versión futura cambia los mensajes, la clasificación cae en `error_driver` y el detalle redactado queda en la evidencia para interpretarlo a mano.
- **Redacción de secretos:** el redactor reemplaza los valores exactos de passwords y tokens configurados y los patrones `usuario:clave@`, `Bearer ...` y `password=`. Una password de laboratorio muy corta o igual a una palabra común puede tapar texto que no es secreto. Se prefiere tapar de más que filtrar.
- **Escritura en Redis:** la prueba de expiración crea una clave `diag:hito11:*` con TTL de 2 s. No es dato de dominio y expira sola. Se desactiva con `-SinEscritura`.

### De alcance

- **Conectividad no es rendimiento:** las latencias registradas son de **una** operación, en reposo y desde un único cliente. No permiten concluir cuántas operaciones por segundo soporta el sistema. Eso corresponde al Hito 12.
- **OK es puntual:** un `OK` significa que esa prueba funcionó en ese momento. No garantiza disponibilidad permanente (RNF17).
- **Falla controlada:** se ejecuta sobre un producto por vez. Repetirla sobre Cassandra puede llevar más de un minuto de recuperación (el script espera hasta `-LimiteRecuperacion`, 180 s por defecto).
- **No se prueban escrituras de dominio** ni el `DELETE /api/v1/sesiones/{id}`, porque modifican datos (RNF6).

## 2. Coherencia con el TPO

| Hito | Decisión previa | Cómo la usa el Hito 11 |
|---|---|---|
| 1–2 | Clasificación de los datos del Fixture y elección de un motor por tipo de dato | Cada producto se evalúa con **su** cliente y protocolo, no con una prueba HTTP genérica (RNF4) |
| 3 | Arquitectura distribuida: replicación, particionamiento y consistencia por subsistema | La lectura de Cassandra respeta la clave de partición `(partido_id, bucket_10min)`; las particiones vacías se tratan como respuestas válidas |
| 4 | MongoDB con referencing entre `jugadores.equipo_id` y `equipos._id`; validaciones; índice `idx_jugadores_equipo` | La lectura mínima usa `equipos` por `_id`; la prueba de contexto verifica `equipos` y `jugadores` |
| 5 | Grafo de partidos, equipos, sedes y eventos en Neo4j | Cypher parametrizado sobre `(:Partido)-[:DISPUTA]->(:Equipo)` y `(:Evento)-[:OCURRE_EN]->(:Partido)` |
| 6 | Comentarios en Cassandra por partido y ventana de 10 minutos | Se valida el keyspace, la tabla y el patrón de partición real leído de `system_schema` |
| 7 | Sesiones en Redis con TTL | Se distingue clave vigente, sin expiración, ausente/expirada y Redis no disponible |
| 8 | Series temporales en InfluxDB 3 con detalle y downsampling a 15 minutos | Consulta acotada en el tiempo sobre ambas databases, con rango y agregación registrados |
| 9 | Persistencia de objetos en IRIS (`Fixture.Partido`, `Arbitro`, `EventoPartido`) | Lectura de la entidad y de los metadatos del esquema `Fixture` por el Superserver |
| 10 | API REST integrada con un adaptador por motor, errores uniformes y `X-Request-ID` | El Hito 11 ejecuta sus rutas, reutiliza el request ID para encontrar el log y agrega liveness/readiness sin cambiar el contrato de las rutas existentes |
| 12 (próximo) | Pruebas de carga | El Hito 11 deja establecido desde dónde se conecta la API, con qué host/puerto/driver/contexto y cómo se comporta ante fallas: la base para interpretar los resultados de carga |

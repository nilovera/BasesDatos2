# Evidencia, trazabilidad y limitaciones

Cada ejecución conserva fecha, commit, rama, escenario, estado de servicios y
resultados pertinentes. `capturar_evidencia.ps1` exige por defecto árbol Git
limpio, separa stdout/stderr y genera un manifiesto SHA-256. Las capturas
visuales, cuando existen, deben corresponder a la misma ventana de medición.

## Interpretación de estados

- Implementado: existe código o configuración revisable.
- Ejecutado: hay registro de la ejecución identificada.
- Medido: se obtuvo un indicador con método y escenario conocidos.
- Objetivo: valor deseado; no constituye un resultado observado.
- Limitación: condición que restringe el alcance de una conclusión.

Las verificaciones Docker, fallas, carga, comparación analítica y simulación
están registradas en el [estado de validación](../estado_validacion.md).
No corresponde mantenerlas como ejecuciones futuras. Cada evidencia se
interpreta con el commit que identifica, sin transferirla automáticamente a
modificaciones posteriores.

## Cobertura del monitoreo

MongoDB aporta salud funcional y métricas nativas `serverStatus`/`dbStats`
mediante un collector en la API. Redis tiene exporter; InfluxDB, target directo.
Cassandra, Neo4j y Data Mart tienen salud y contadores funcionales, sin colección
completa de métricas internas. Prometheus conserva siete días en el laboratorio.

Outbox proyecta Redis y Neo4j. Sus métricas conservan la etiqueta histórica
`consumer="redis"`. La auditoría nueva usa una cola y un relay independientes;
no se afirma que las reglas Outbox midan su retraso.

## Límites comprobables

- MongoDB de un miembro, Cassandra RF=1 y demás motores de un nodo: sin HA real.
- Redis RDB/AOF permite persistencia local, sin sustituir réplica o backup externo.
- Existen mediciones de lectura y cumplimiento de SLO locales; no hay capacidad
  máxima determinada, SLA contractual ni disponibilidad anual medida.
- No hay RPO/RTO medido ni restauración integral ante pérdida del host.
- Data Mart tiene comparaciones pequeñas y carga mixta; no una conclusión de
  ventaja a gran volumen ni reconciliación completa de correcciones ya cargadas.
- Las alertas locales se activaron en fallas controladas; no existe un canal
  externo de notificación configurado.
- No se conserva una captura de Grafana para cada ventana y cada prueba.
- El front tiene evidencia de respuestas; no una validación visual automatizada integral.
- La auditoría tiene resultado HTTP integrado OK, además de validación
  unitaria. El JSON original no capturó el SHA de ejecución; la procedencia
  complementaria identifica la base y los hashes observados posteriormente.
  La prueba no mide capacidad ni replicación.

## Protección de la evidencia

No se versionan tokens, sesiones, contraseñas, archivos `.env` ni volcados del
entorno. Se revisan JSON, textos y capturas antes de incorporarlos. Los logs no
incluyen cuerpos completos. El historial distingue identidad declarada de una
sesión de laboratorio y no se presenta como autenticación real o almacenamiento WORM.

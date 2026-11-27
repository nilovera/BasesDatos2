# 6.1 Convenciones comunes

## Identidad y tiempo

| Entidad | Identidad | Alcance |
|---|---|---|
| Equipo | EQ-01 | Catálogo común; 64 equipos |
| Jugador | JUG-0001 | Catálogo común; 1.024 jugadores |
| Partido | PAR-0001 | Escenario base; las simulaciones crean nuevos IDs |
| Evento | EVE-000001 | Identidad durable, con secuencia por partido |
| Usuario de laboratorio | USR-0001 | Identificador declarado; no prueba identidad real |
| Simulación | SIM- más UUID | Ejecución deportiva reproducible |
| Sesión | Identificador opaco devuelto por la API | Temporal Redis; no registrar su valor en evidencia pública |
| Comentario y auditoría | UUID estable según operación | Deduplicación de reintentos |

Las marcas de tiempo se intercambian en ISO 8601 y se normalizan a UTC. Los
buckets de auditoría usan día UTC `YYYYMMDD`. El tiempo lógico del partido y
la hora de recepción de una solicitud son magnitudes diferentes. Los registros
de ejecución conservan la fecha real de la medición.

## Propiedad y consistencia

MongoDB confirma catálogo, partido, alineaciones y hechos deportivos. Cassandra
conserva comentarios e historial de auditoría. InfluxDB conserva telemetría.
Redis mantiene sesiones y vistas temporales. Neo4j mantiene relaciones
proyectadas. PostgreSQL recibe hechos analíticos mediante ETL explícito.

Outbox proyecta eventos oficiales a Redis y Neo4j. No representa una replicación
universal de todos los datos. Los comentarios y las muestras de InfluxDB no
pasan automáticamente a MongoDB. La cola `auditoria_pendiente` de MongoDB
contiene metadatos transitorios de entrega, no una copia del contenido social
ni de la telemetría.

## Catálogo y escenario

El generador reproduce 64 equipos y 16 jugadores por equipo. Los perfiles de
jugadores son sintéticos. ARG/EQ-01 y MEX/EQ-33 son las equivalencias explícitas
del partido base. No se incorporan otros alias sin validación. PAR-0001 es un
encuentro sintético Argentina–México, no una fecha oficial del torneo.

La carga inicial no contiene eventos. Después de usar la plataforma, los conteos
y estados operativos cambian; volver a preparar el entorno no debe reiniciar el
partido. Los datos históricos de otras ramas no se mezclan por coincidencia de ID.

## Contratos y trazabilidad

La secuencia ordena eventos dentro de un partido; la versión detecta cambios
concurrentes del agregado. `Idempotency-Key` identifica un comando lógico en las
operaciones que lo admiten. `X-Request-ID` correlaciona una solicitud técnica y
no sustituye la identidad del evento. `X-Session-ID` atribuye una sesión de
laboratorio cuando se proporciona; no demuestra autenticación de producción.

Los contratos concretos se describen en
[eventos e idempotencia](07_contratos_eventos_idempotencia_outbox.md) y en
`backend/openapi.json`. Los estados de validación se consultan en el
[registro de evidencias](../estado_validacion.md).

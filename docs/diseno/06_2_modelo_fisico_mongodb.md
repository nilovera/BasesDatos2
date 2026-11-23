# Paso 6.2 — Modelo físico de MongoDB

Estado: diseño aprobado para implementación incremental. El script
`mongodb/init/01_schema.js` materializa validadores e índices; su ejecución
contra un contenedor se verificará en el incremento de Docker.

## Responsabilidad

MongoDB es la fuente autoritativa del núcleo deportivo:

- equipos y jugadores;
- partidos, estado y marcador vigente;
- alineaciones y participaciones;
- eventos oficiales;
- mensajes de Outbox asociados a esos eventos.

No almacena comentarios, sesiones ni muestras temporales de posición. Esos
datos corresponden a Cassandra, Redis e InfluxDB. Neo4j recibe relaciones
derivadas y reconstruibles.

## Decisiones de modelado

| Necesidad | Decisión | Motivo y costo |
|---|---|---|
| Catálogo de equipos | Colección `equipos` | Cambia poco y se consulta por ID; evita repetir planteles completos |
| Jugadores | Colección `jugadores` con referencia `equipoId` | Permite búsquedas individuales y por equipo; exige validar la referencia en la aplicación |
| Partido vigente | Colección `partidos` como agregado | Lectura de estado, marcador y alineaciones en una operación; el documento puede crecer y debe limitarse |
| Historial oficial | Colección `eventos_oficiales` separada | Evita un arreglo ilimitado dentro del partido y permite paginar por secuencia |
| Propagación | Colección `outbox` | La transacción confirma el dato y su intención de publicación de forma atómica |
| Duplicados | Clave idempotente única en el evento | Un mismo request no genera dos hechos; requiere conservar respuesta suficiente para reintentos |

## Colecciones

### `equipos`

Documento canónico de una selección.

Campos principales:

- `equipoId`: `EQ-01`, único e inmutable;
- `nombre`: nombre visible;
- `codigoExterno`: alias como `ARG`, cuando exista una equivalencia validada;
- `activo`: permite retirar una selección sin reutilizar el ID;
- `creadoEn` y `actualizadoEn`: timestamps UTC.

Índices:

- único por `equipoId`;
- único y parcial por `codigoExterno`.

### `jugadores`

Campos principales:

- `jugadorId`: único e inmutable;
- `equipoId`: referencia lógica a `equipos`;
- `nombre`, `posicion` y `fechaNacimiento`;
- `activo`, `creadoEn` y `actualizadoEn`.

Índices:

- único por `jugadorId`;
- compuesto por `equipoId`, `activo`, `jugadorId`.

MongoDB no aplica claves foráneas. La carga y la API deben rechazar jugadores
huérfanos; el catálogo común ya verifica esa invariante.

### `partidos`

Es el agregado de lectura y control de concurrencia. Incluye:

- `partidoId`;
- `equipos.localId` y `equipos.visitanteId`;
- `inicioProgramado`;
- `estado`;
- `marcador.local` y `marcador.visitante`;
- `alineaciones.local` y `alineaciones.visitante`;
- `ultimaSecuencia`;
- `version` para actualización optimista;
- timestamps de creación y actualización.

El historial completo no se embebe. `ultimaSecuencia` asigna un orden estable a
eventos del mismo partido y `version` evita sobrescrituras silenciosas.

Índices:

- único por `partidoId`;
- por `estado`, `inicioProgramado` y `partidoId`;
- por cada equipo e `inicioProgramado` para consultar su calendario.

### `eventos_oficiales`

Registro durable ordenado por partido. Tipos iniciales:

- `INICIO_PARTIDO`;
- `GOL`;
- `SUSTITUCION`;
- `CORRECCION_EVENTO`.

Cada documento contiene:

- `eventoId`;
- `partidoId` y `secuencia`;
- `tipo` y `datos` específicos;
- `idempotencia.clave` y `idempotencia.hashSolicitud`;
- `ocurridoEn` y `recibidoEn`;
- `versionContrato`;
- `respuestaHttp` mínima para devolver el mismo resultado ante una repetición.

Una corrección crea un evento nuevo que referencia el original. No se reescribe
la historia como si el error nunca hubiera ocurrido. El agregado `partidos` se
actualiza con el resultado vigente dentro de la misma transacción.

Índices:

- único por `eventoId`;
- único por `partidoId` y `secuencia`;
- único por `idempotencia.clave`;
- por `partidoId`, `recibidoEn` y `eventoId`.

### `outbox`

Un documento por evento confirmado:

- `outboxId` y `eventoId`;
- `tipo`, `partidoId` y `payload` versionado;
- `estado`: `PENDIENTE`, `PROCESANDO`, `PUBLICADO` o `FALLIDO`;
- `intentos`, `proximoIntentoEn` y `ultimoError` sanitizado;
- `bloqueo.hasta` y `bloqueo.workerId` para reclamo temporal;
- `creadoEn`, `actualizadoEn`, `publicadoEn` y `expiraEn`.

`expiraEn` solo se completa al publicar. El índice TTL nunca debe borrar un
mensaje pendiente o fallido antes de su resolución.

## Escritura atómica

Registrar un evento requiere una transacción MongoDB:

1. reservar la clave idempotente mediante índice único;
2. leer el partido y validar su estado/version;
3. asignar `ultimaSecuencia + 1`;
4. insertar `eventos_oficiales`;
5. actualizar el agregado `partidos`;
6. insertar el mensaje `outbox`;
7. confirmar la transacción.

El entorno local deberá iniciar MongoDB como replica set de un nodo, porque las
transacciones multidocumento no funcionan en un servidor standalone.

## Consistencia y CAP

- Dentro de MongoDB: consistencia fuerte del agregado mediante transacción y
  `writeConcern: majority` en el entorno que permita réplica.
- Respuesta de la API: confirma únicamente después del commit.
- Redis, InfluxDB y Neo4j: consistencia eventual a través de Outbox.
- Si una proyección falla, el dato oficial permanece confirmado y el mensaje se
  reintenta.
- Cassandra conserva su propia autoridad para comentarios y no participa en la
  transacción deportiva.

## Límites explícitos

- El diseño no demuestra rendimiento hasta ejecutarse y medirse.
- La réplica de un nodo habilita transacciones, pero no alta disponibilidad.
- Las alineaciones deben tener límites validados para impedir documentos sin
  crecimiento controlado.
- La paginación de eventos usa `(secuencia, eventoId)`, no `skip` para recorridos
  grandes.
- Los errores de Outbox no guardan secretos ni payloads de credenciales.

## Criterios de aceptación

1. Los validadores rechazan IDs, estados y tipos fuera del contrato.
2. Los índices únicos impiden duplicar evento, secuencia y clave idempotente.
3. Un gol crea evento, actualiza marcador y crea Outbox en una transacción.
4. Repetir la misma clave y body devuelve la respuesta previa sin nuevo evento.
5. Reutilizar la clave con otro body devuelve conflicto.
6. Una caída del consumidor no revierte el evento oficial y la Outbox converge al recuperarse.
7. Ningún archivo ejecutable contiene dependencias de IRIS.

## Referencias técnicas

- MongoDB, validación con operadores y combinación con JSON Schema: https://www.mongodb.com/docs/manual/core/schema-validation/specify-query-expression-rules/
- MongoDB, transacciones multidocumento: https://www.mongodb.com/docs/manual/core/transactions/
- MongoDB, consideraciones de transacciones y requisito de replica set: https://www.mongodb.com/docs/manual/core/transactions-production-consideration/
- MongoDB, índices parciales: https://www.mongodb.com/docs/manual/core/index-partial/
- MongoDB, índices TTL: https://www.mongodb.com/docs/manual/core/index-ttl/

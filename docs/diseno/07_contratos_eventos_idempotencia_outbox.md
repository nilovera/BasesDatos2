# Contratos de eventos, idempotencia y Outbox

## Identidades y alcance

El contrato HTTP concreto está en `backend/openapi.json`. `eventoId` identifica
el hecho, `secuencia` lo ordena dentro del partido y `versionPartido` protege
el agregado frente a concurrencia. `X-Request-ID` correlaciona una solicitud;
no reemplaza la identidad del comando ni deduplica una escritura.

| Operación | Idempotency-Key | Comportamiento |
|---|---|---|
| Registrar evento oficial | Obligatoria, de 16 a 128 caracteres | Mismo contenido devuelve la respuesta conservada; otro contenido genera conflicto |
| Publicar comentario | Obligatoria | Identidad estable y reserva Cassandra |
| Moderar comentario | Opcional en el incremento 15 | Con clave, replay sin reaplicar un estado antiguo; sin clave, cada llamada es una acción distinta |
| Crear/controlar simulación | No exige esa cabecera | La auditoría utiliza una identidad interna por operación confirmada |
| Ingresar telemetría | Identidad natural de la muestra | Tabla, tags y timestamp; no identidad de comando HTTP |

## Evento deportivo

`POST /api/v1/partidos/{partidoId}/eventos` admite `INICIO_PARTIDO`, `GOL`,
`TARJETA`, `SUSTITUCION`, `GOL_ANULADO_VAR`, `FIN_PARTIDO` y
`CORRECCION_EVENTO`. Las referencias y el estado deben satisfacer el dominio.
El gol puede incluir `asistenteJugadorId`; una corrección referencia un evento
del mismo partido, agrega otro hecho y recalcula el agregado.

El hash SHA-256 se calcula sobre el comando normalizado. La clave, el hash y
la respuesta se conservan en el evento MongoDB. Una creación devuelve `201`;
un replay confirmado devuelve `200` e `Idempotency-Replayed: true`.
La reutilización incompatible devuelve `409 IDEMPOTENCY_KEY_REUSED`.
No se promete un código especial de operación en curso que el servicio no expone.

El simulador controla alineaciones y sustituciones. Los comandos manuales
validan referencias y reglas básicas; no se declara validación completa de
participación histórica por minuto para cada entrada externa.

## Transacción y mensaje de entrega

La transacción MongoDB actualiza el partido, inserta el evento y agrega Outbox.
El incremento 15 agrega la entrega de auditoría. La respuesta oficial puede
indicar `propagacion: PENDIENTE`: el hecho ya está confirmado y sus vistas
todavía pueden estar en tránsito.

Outbox conserva `outboxId`, `eventoId`, `partidoId`, `tipo`, `secuencia`,
`versionContrato`, `payload`, estado, intentos y marcas de gestión. El payload
contiene el comando de evento, el resultado oficial y las referencias del
partido que necesita la proyección. Los nombres y tipos persistidos se definen
en `mongodb/init/01_schema.js`; no se confunden con un sobre teórico diferente.

## Consumidor y recuperación

1. `outbox-worker` reclama un mensaje disponible con `findOneAndUpdate` y lease.
2. El script Lua Redis deduplica por evento, invalida caché y proyecta la vista
   caliente y el Stream acotado.
3. El servicio Neo4j proyecta el evento mediante `MERGE` identificado por evento.
4. Solo después de ambos destinos se marca el mensaje `PUBLICADO`.
5. Un fallo reprograma el mensaje con backoff y jitter; al agotar ocho intentos
   pasa a `FALLIDO` para diagnóstico.

La entrega es al menos una vez. La idempotencia protege el efecto observable
si el destino confirma y luego falla el acuse MongoDB. Un lease vencido permite
retomar trabajo. El worker no implementa una barrera estricta n/n+1 por partido;
no se afirma orden causal total de las vistas derivadas.

La prueba registrada de Outbox conservó dos intentos y una sola copia Redis.
La simulación comprobó además relaciones deportivas Neo4j. Esto acredita esos
casos, sin demostrar reconciliación de toda corrección histórica en cada destino.

## Auditoría y logs

La entrega de auditoría usa otra cola MongoDB y un relay en la API. Su destino
consultable es Cassandra. No reemplaza Outbox deportiva ni transporta textos
de comentarios o series temporales hacia MongoDB.

Los logs HTTP incluyen correlación, ruta normalizada, método, código y duración,
sin cuerpos ni secretos. Las dependencias indicadas son las previstas por el
flujo, no spans medidos. Las métricas usan etiquetas acotadas, evitando IDs
de usuario, request o partido como dimensiones de cardinalidad abierta.

La etiqueta histórica `consumer="redis"` de las métricas Outbox se conserva en
el código y las reglas; no significa que Neo4j haya dejado de ser destino.
Profundidad, edad, reintentos y fallidos se evalúan junto con la disponibilidad
del worker. Evidencias: [estado de validación](../estado_validacion.md).

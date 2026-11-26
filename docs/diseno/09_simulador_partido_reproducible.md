# Simulador reproducible de partido

## Propósito

El simulador genera un partido completo de 90 minutos sin usar el perfil de
carga. Cada ejecución crea un agregado `PAR-xxxx` nuevo a partir de `PAR-0001`;
no reinicia ni borra la historia oficial. La semilla deportiva predeterminada
es `2030` y la velocidad `30x`, equivalente a tres minutos reales.

## Reloj lógico

`velocidad` expresa segundos simulados por segundo real. Pausar congela el
reloj, eventos, comentarios y telemetría. Reanudar continúa desde el mismo
segundo. La velocidad se puede cambiar entre `1x` y `120x` sin recalcular el
plan ni omitir eventos.

## Coherencia deportiva

- Formación inicial 1-4-4-2 y cinco suplentes.
- Dos a cuatro goles, cinco tarjetas, tres cambios por equipo, un gol anulado
  por VAR, inicio y final.
- Goleador y asistente pertenecen al equipo; son jugadores distintos.
- Los cambios son puesto por puesto y delimitan las muestras del titular y del
  suplente.
- Las posiciones se generan cada cinco segundos simulados dentro de zonas por
  puesto. El equipo con posesión adelanta sus líneas.
- En goles y VAR, la pelota adopta las mismas coordenadas que el evento oficial.

Con 90 minutos se producen 1.080 instantes, 23.760 posiciones de jugadores y
1.080 posiciones de pelota: unas 24.840 muestras por ejecución.

## Autoridad y proyecciones

| Dato | Base | Regla |
|---|---|---|
| Inicio, goles, tarjetas, cambios, VAR y final | MongoDB | Fuente oficial transaccional |
| Jugadores y pelota | InfluxDB | Series reproducibles por tags + timestamp |
| Comentarios | Cassandra | Escritura idempotente por clave de simulación |
| Marcador | Redis | Hash proyectado por Outbox |
| Autoría, asistencia y cambios | Neo4j | `MERGE` por `eventoId` |

La proyección Redis ocurre antes de confirmar la Outbox. Neo4j también usa
operaciones idempotentes; si falla luego de Redis, el mensaje se reintenta y no
duplica el marcador, Stream ni relaciones.

## API de control

- `POST /api/v1/simulaciones`
- `POST /api/v1/simulaciones/{id}/iniciar`
- `POST /api/v1/simulaciones/{id}/pausar`
- `POST /api/v1/simulaciones/{id}/reanudar`
- `PATCH /api/v1/simulaciones/{id}/velocidad`
- `GET /api/v1/simulaciones/{id}`

Para la prueba automática se usa `120x` y termina en unos 45 segundos. La demo
visual debe usar `30x` para durar aproximadamente tres minutos.

## Limitaciones declaradas

El laboratorio ejecuta una sola instancia de API y un hilo simulador. El estado
de control vive en MongoDB y puede retomarse tras una pausa, pero este incremento
no implementa elección distribuida de líder entre múltiples réplicas HTTP. Los
usuarios de comentarios siguen siendo identificadores sintéticos; la colección
durable de perfiles y autorización continúa en T01.

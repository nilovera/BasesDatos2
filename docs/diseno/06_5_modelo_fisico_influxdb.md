# 6.5 Modelo físico de InfluxDB

## Responsabilidad y origen

InfluxDB conserva observaciones temporales de alta frecuencia que no son la
fuente oficial del partido. MongoDB sigue siendo autoritativo para equipos,
jugadores, estado, marcador y eventos; InfluxDB responde recorridos, mapas de
calor, evolución estadística y resúmenes por ventana.

Se revisó la rama histórica `InfluxDB`, commit
`1668d8382d4e57ff4c458798ffa384f7c923922f`. Se conservaron su separación
detalle/histórico, la muestra cada diez segundos y la agregación de quince
minutos. Se reemplazaron `ARG/MEX` por `EQ-01/EQ-33`, el tag flotante, el bind
mount de WSL y el token manual. La rama mal escrita `InlfuxDB` no se usa.

## Bases y retención

| Base | Retención | Uso |
|---|---:|---|
| `fixture2030-detalle` | 7 días | posiciones y estadísticas de alta frecuencia |
| `fixture2030-historico` | 365 días | resúmenes de 15 minutos para análisis y defensa |

InfluxDB 3 Core fija la retención al crear la base. El inicializador consulta
primero los recursos y solo crea los faltantes; no elimina ni recrea una base
existente. Cambiar una retención requiere una migración explícita.

## Tablas

### `posiciones_jugador`

| Tipo | Columnas |
|---|---|
| tags | `partido_id`, `equipo_id`, `jugador_id` |
| fields | `x`, `y`, `periodo`, `segundo_partido` |
| tiempo | `capturadoEn` normalizado a UTC y escrito en nanosegundos |

La identidad natural de un punto es tabla + tags + timestamp. Reenviar la
misma posición no agrega una fila; escribir otros valores para la misma
identidad reemplaza el punto. Un lote rechaza dos valores distintos para el
mismo jugador y timestamp antes de enviarlos.

### `estadisticas_equipo`

| Tipo | Columnas |
|---|---|
| tags | `partido_id`, `equipo_id` |
| fields | `posesion_pct`, `pases_intervalo`, `tiros_acumulados`, `goles_acumulados`, `periodo`, `segundo_partido` |
| tiempo | timestamp de la observación en UTC |

### `resumen_equipo_15m`

| Tipo | Columnas |
|---|---|
| tags | `partido_id`, `equipo_id` |
| fields | `posesion_promedio`, `pases_total`, `tiros_finales`, `goles_finales`, `muestras` |
| tiempo | inicio de la ventana de 15 minutos |

Las magnitudes variables son fields y no tags. Esto evita crear una serie por
coordenada, marcador o valor estadístico. `jugador_id` sí es tag porque es una
dimensión de consulta acotada por el catálogo (1.024 jugadores).

## Cardinalidad, granularidad y volumen

Para un partido con 32 jugadores registrados, `posiciones_jugador` crea como
máximo 32 combinaciones de tags y `estadisticas_equipo`, dos. Aun si el fixture
creciera a 96 partidos, el orden esperado sería 3.072 series de posiciones y
192 de equipo, no una serie por punto. Timestamp, coordenadas y valores
acumulados nunca son tags.

La prueba reproducible usa estadísticas cada 10 segundos: 540 puntos por
equipo, 1.080 por partido. El endpoint admite una frecuencia independiente para
posiciones y lotes de hasta 250. Esto valida modelo, batching y resultados, pero
no demuestra el objetivo académico de 10M+ puntos ni capacidad sostenida; esa
medición pertenece a los escenarios T05 y debe registrar throughput, latencia,
errores, recursos y tamaño final antes de afirmar escalabilidad.

## Contratos de API

- `POST/GET /api/v1/partidos/{partidoId}/telemetria/posiciones`
- `GET /api/v1/partidos/{partidoId}/jugadores/{jugadorId}/mapa-calor`
- `POST /api/v1/partidos/{partidoId}/telemetria/estadisticas-equipos`
- `POST /api/v1/partidos/{partidoId}/telemetria/agregaciones/15m`
- `GET /api/v1/partidos/{partidoId}/telemetria/resumenes-equipos/15m`

Los lotes admiten entre 1 y 250 muestras y se escriben con
`accept_partial=false`: una línea inválida rechaza el lote completo. Antes de
escribir, MongoDB confirma que el partido y los equipos existen, y que cada
jugador pertenece al equipo informado.

## Cursor estable y mapa de calor

La lectura se ordena por `(time, jugador_id)`. El cursor opaco codifica ambos
valores; usar solamente el timestamp omitiría jugadores cuando comparten la
misma marca temporal. La página siguiente usa:

```sql
time > cursor_time
OR (time = cursor_time AND jugador_id > cursor_player)
```

El mapa de calor consulta puntos de un jugador, divide el campo 0–100 en una
grilla configurable de 5 a 25 celdas por eje y devuelve conteos reproducibles.
La API exige acotar la ventana si supera 10.000 puntos.

## Seguridad, persistencia y observabilidad

- imagen fijada: `influxdb:3.12.3-core`;
- volumen nombrado `fixture2030-influxdb-data`;
- token administrativo offline generado localmente en `.secretos/`;
- JSON y token crudo montados como secretos, nunca como variables ni salida;
- puerto publicado solo en `127.0.0.1:8181`;
- `/metrics` recolectado por Prometheus con credencial desde archivo;
- salud funcional `fixture2030_dependency_up{dependency="influxdb"}`;
- operaciones de dominio `fixture2030_telemetry_operations_total`;
- alerta y falla controlada que no detienen MongoDB, Redis ni Cassandra.

## Límites declarados

El catálogo actual tiene alineaciones vacías. Por eso este incremento valida
pertenencia al plantel, pero todavía no puede demostrar que el jugador estaba
en cancha en cada segundo. La aceptación completa se cerrará al incorporar
alineaciones y sustituciones al simulador (T03). Tampoco existe todavía el
consumidor de Outbox que proyectará automáticamente eventos oficiales hacia
las estadísticas; la prueba actual carga telemetría sintética mediante la API.

La instancia local es un solo nodo. El volumen demuestra reinicio persistente,
no alta disponibilidad, backup probado ni recuperación ante pérdida del host.

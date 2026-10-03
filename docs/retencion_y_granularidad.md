# Retención y granularidad

## Objetivo

El módulo conserva estadísticas detalladas durante el período necesario para la operación en vivo y mantiene una representación resumida para consultas históricas.

## Política aplicada

| Base | Contenido | Granularidad | Retención |
|---|---|---:|---:|
| `fixture2030_detalle` | Estadísticas originales del partido | Un punto cada 10 segundos por equipo | 7 días |
| `fixture2030_historico` | Resúmenes por equipo | Una ventana cada 15 minutos | 365 días |

La política se configuró al crear cada base mediante `--retention-period`. En InfluxDB 3 Core la retención se define a nivel de base y las tablas heredan esa configuración.

## Datos detallados

La tabla `estadisticas_equipo` conserva:

- `partido_id` y `equipo_id` como tags.
- `posesion_pct`, `pases_intervalo` y `tiros_acumulados` como fields.
- `time` con precisión declarada en segundos.

El detalle se utiliza para consultas operativas de ventanas recientes, evolución temporal y comparación entre equipos durante el partido.

## Resumen histórico

La tabla `resumen_equipo_minuto` conserva ventanas de 15 minutos. Para cada equipo se almacenan:

- Promedio de posesión.
- Total de pases registrados en el intervalo.
- Cantidad de muestras.
- Inicio y fin de la ventana.

El resumen reduce 1.080 puntos detallados a 12 puntos históricos.

## Semántica de las agregaciones

- `AVG(posesion_pct)`: la posesión es una muestra porcentual y se interpreta mediante promedio.
- `SUM(pases_intervalo)`: cada punto contiene los pases del intervalo, por lo que pueden sumarse.
- `MAX(tiros_acumulados)`: los tiros ya son acumulativos; sumarlos duplicaría valores.

## Ciclo de vida

1. Las fuentes generan puntos cada 10 segundos.
2. Los puntos se escriben en `fixture2030_detalle`.
3. Las consultas en vivo usan rangos temporales y filtros por partido y equipo.
4. Los puntos se agrupan en ventanas de 15 minutos.
5. Los resúmenes se guardan en `fixture2030_historico`.
6. El detalle deja de ser consultable después de 7 días.
7. El resumen histórico se conserva durante 365 días.

## Impacto

La separación permite conservar precisión para la operación inmediata sin mantener indefinidamente todo el volumen original. Esto reduce almacenamiento y costo de consultas históricas, mientras conserva información suficiente para analizar tendencias del torneo.

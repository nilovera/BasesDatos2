# Cardinalidad y escalabilidad - Estadísticas temporales del Fixture 2030

## 1. Criterio de análisis

El análisis utiliza las tablas `estadisticas_equipo` y `resumen_equipo_minuto` del modelo multidimensional. Ambas identifican el contexto mediante los tags `partido_id` y `equipo_id`.

Se distinguen dos cantidades:

- **Series:** combinaciones de tabla y valores de tags, dentro de cada base.
- **Puntos:** observaciones con un timestamp dentro de esas series.

Más muestras de un mismo equipo y partido aumentan los puntos, pero mantienen la combinación de tags. Los tres fields del detalle pertenecen a la misma observación: no se contabilizan como tres puntos ni como tres series independientes.

## 2. Variación de las dimensiones

La referencia del laboratorio es la carga de los Hitos 4 y 5: 64 equipos, con códigos `EQ-01` a `EQ-64`, y 96 partidos, con códigos `PAR-0001` a `PAR-0096`. Cassandra también utiliza esos partidos en el Hito 6.

| Dimensión | Valores del laboratorio | Restricción del dominio |
|---|---:|---|
| `partido_id` | 96 | Solamente partidos existentes en el fixture de Neo4j. |
| `equipo_id` | 64 | Solamente los dos equipos vinculados al partido mediante `DISPUTA`. |

Cada equipo participa en tres partidos de la muestra de grupos. Por ejemplo, `PAR-0001` enfrenta a `EQ-01` con `EQ-17`; otro equipo no puede generar una serie válida para ese partido.

Los 127 partidos planteados en los Hitos 1 a 3 y en la Clase 9 describen el torneo completo. Se mantienen como escenario de crecimiento, diferenciados de los 96 partidos del laboratorio.

## 3. Estimación de cardinalidad

El producto `96 × 64 = 6.144` representa combinaciones posibles de códigos, pero incluye equipos que no participan en cada partido. La estimación utiliza únicamente las relaciones deportivas válidas:

```text
series por tabla = partidos con datos × equipos participantes
series por tabla = 96 × 2 = 192
```

| Tabla | Series previstas con los 96 partidos |
|---|---:|
| `estadisticas_equipo` | 192 |
| `resumen_equipo_minuto` | 192 |
| Total de las dos tablas | 384 |

Las 384 series requieren que todos los pares válidos tengan detalle y resumen. Una prueba de un solo partido tendrá dos series en cada tabla que reciba puntos. Estas cifras son estimaciones del diseño; la cantidad efectivamente escrita se comprobará después de la carga.

Para el escenario completo de 127 partidos, cada tabla tendría hasta `127 × 2 = 254` series, y ambas sumarían 508. Antes de cargar los partidos adicionales se necesitarían sus identificadores y participantes; no se generan cruces arbitrarios para alcanzar esa cantidad.

## 4. Volumen de puntos

La captura de referencia registra una observación por segundo y por equipo. La precisión de escritura es de milisegundos; esa precisión no significa que se genere un punto cada milisegundo.

```text
puntos de detalle = partidos × 2 equipos × segundos observados × frecuencia por segundo
```

| Escenario estimado | Partidos | Tiempo observado por partido | Frecuencia por equipo | Puntos de detalle |
|---|---:|---:|---:|---:|
| Prueba pequeña | 1 | 5 minutos | 1 punto/s | 600 |
| Partido de referencia | 1 | 90 minutos | 1 punto/s | 10.800 |
| Muestra del laboratorio | 96 | 90 minutos | 1 punto/s | 1.036.800 |
| Escenario completo | 127 | 90 minutos | 1 punto/s | 1.371.600 |

Los cálculos consideran observaciones en `[inicio, fin)`, sin huecos, con ambos equipos. Para consultar tiros exactos entre esas fronteras se necesita además la muestra de `fin`; si se guarda para ambos equipos en cada partido, se agregan dos puntos por partido. No modifica la cardinalidad.

Los 90 minutos son una duración de referencia para estimar el volumen, no una medición de los encuentros. El tiempo real de captura se declarará en cada prueba. La ventana de actividad de 120 minutos utilizada por Cassandra para comentarios responde a otro fenómeno y no obliga a registrar estadísticas deportivas durante todo ese período.

### Resúmenes por minuto

Para 96 partidos, 90 minutos observados y una versión de cada resumen:

```text
resúmenes = 96 × 2 × 90 = 17.280 puntos
```

Con cobertura completa, cada resumen utiliza 60 observaciones. Si llegan datos tardíos, una nueva versión agrega un punto con otro timestamp de generación, manteniendo los mismos tags. Con dos versiones de todos los minutos serían 34.560 puntos y seguirían existiendo 192 series en la tabla de resúmenes.

## 5. Riesgos y decisiones de modelado

| Atributo o cambio | Riesgo | Decisión |
|---|---|---|
| Identificador único por observación | Cada punto podría formar una combinación nueva. | No se incorpora como tag. |
| Timestamp o inicio de ventana como tag | Las dimensiones variarían con cada instante o minuto. | Se utilizan `time` y los fields de límites del resumen. |
| Posesión, pases o tiros como tags | Mezclarían medidas cambiantes con la identidad del contexto. | Se conservan como fields numéricos. |
| Nombres, comentarios o texto libre | Variación innecesaria y ausencia de una consulta que la justifique. | Se mantienen en los módulos correspondientes. |
| Jugador, espectador o sede | Agregarían dimensiones ajenas a PA1–PA6. | No se agregan al modelo actual. |
| Múltiples fuentes independientes | Cambiarían la identidad de la observación y su interpretación. | Se revisaría el modelo antes de incorporarlas. |

Si cada par partido–equipo recibiera datos de `F` fuentes identificadas por un nuevo tag, la cota sería `192 × F` series por tabla, siempre que todas esas combinaciones existieran. Ese escenario no está implementado.

El laboratorio usa InfluxDB 3 Core. No se trasladan automáticamente los límites de cardinalidad de motores anteriores: además de las combinaciones, se consideran el número de tags, el ancho del esquema, el volumen escrito y las agrupaciones solicitadas. Excluir dimensiones sin utilidad mantiene la identidad y las consultas comprensibles.

## 6. Objetivo de 10 millones de puntos

La captura de referencia de los 96 partidos no alcanza 10 millones de puntos. Repetir exactamente la misma identidad y timestamp no crea observaciones nuevas. Tampoco se multiplican los puntos por la cantidad de fields ni por el número de tablas para afirmar que se alcanzó el objetivo.

Una proyección de esfuerzo con los mismos 96 partidos, dos equipos y 90 minutos, a diez observaciones por segundo y por equipo, produciría:

```text
96 × 2 × 5.400 × 10 = 10.368.000 puntos de detalle
```

La proyección conserva 192 combinaciones de tags y aumenta los puntos mediante timestamps separados por 100 ms. Es una carga sintética de esfuerzo y no afirma que esas observaciones ya se hayan generado o escrito.

Antes de ejecutarla debe adaptarse y documentarse la semántica del generador: en esa prueba, los pases corresponderían a intervalos de 100 ms, sin repetir diez veces el conteo de un segundo. También se ajustarían la cobertura esperada y la alineación de las consultas. Se realizaría en una base de prueba separada para conservar la captura de referencia de un segundo. Estos cambios requieren que la configuración de la prueba quede registrada y que el modelo y las consultas de esa prueba se interpreten con el mismo intervalo.

## 7. Crecimiento y límites del laboratorio

| Cambio | Efecto esperado |
|---|---|
| Más partidos válidos | Aumentan las series y los puntos. |
| Mayor frecuencia de captura | Aumentan los puntos de las mismas series. |
| Mayor duración observada | Aumentan los puntos y las ventanas resumidas. |
| Más versiones por datos tardíos | Aumentan los puntos del histórico. |
| Más consultas simultáneas | Aumenta el trabajo de lectura y agregación. |


# Modelo multidimensional - Estadísticas temporales del Fixture 2030

## 1. Criterio de diseño

El modelo se deriva de los patrones PA1 a PA6. Cada observación describe las estadísticas de un equipo en un partido y en un instante. Se distinguen tres medidas: una muestra de posesión, los pases completados durante un intervalo y un contador de tiros acumulados.

Se utilizan dos tablas: una conserva el detalle de las observaciones y otra conserva resúmenes por minuto para las consultas históricas. Las tablas pertenecen a bases diferentes para permitir distintos períodos de conservación en InfluxDB 3 Core.

| Base | Tabla | Propósito |
|---|---|---|
| `fixture2030_detalle` | `estadisticas_equipo` | Observaciones originales de posesión, pases y tiros por equipo y partido. |
| `fixture2030_historico` | `resumen_equipo_minuto` | Resúmenes de posesión y pases por minuto, con cobertura y límites explícitos. |

Para el laboratorio se definieron 7 días de retención del detalle y 365 días de retención del histórico. Su justificación se desarrolla en el análisis de retención. En Core, la retención pertenece a la base y se fija al crearla; cambiarla después requiere otra base y una migración.

## 2. Dimensiones y convención de nombres

Las tablas y columnas usan nombres en minúsculas, separados por `_`. Se mantienen los identificadores estables de partidos y equipos del Fixture; no se generan identificadores nuevos para cada muestra.

Ambas tablas comparten estos tags:

| Tag | Tipo lógico | Función | Variación esperada |
|---|---|---|---|
| `partido_id` | String | Filtrar las estadísticas de un partido. | Un valor por partido registrado. |
| `equipo_id` | String | Separar y comparar los equipos participantes. | Dos valores válidos por partido. Un equipo puede participar en varios partidos. |

Se reutilizan los equipos `EQ-01` a `EQ-64` de MongoDB y Neo4j, y los partidos `PAR-0001` a `PAR-0096` del laboratorio de Neo4j, también utilizados por Cassandra. La carga debe comprobar las relaciones `DISPUTA` del Hito 5: por ejemplo, `PAR-0001` tiene como participantes a `EQ-01` y `EQ-17`.

Los nombres y perfiles permanecen en MongoDB, y las relaciones deportivas en Neo4j. Cassandra conserva los comentarios implementados en el Hito 6. Redis conserva las sesiones, la caché, los rankings y los contadores implementados en el Hito 7. InfluxDB incorpora las estadísticas temporales sin modificar esas responsabilidades ni asumir una sincronización automática entre bases.

## 3. Tablas temporales

### 3.1. Detalle: `estadisticas_equipo`

- **Fenómeno:** estadísticas observadas de un equipo durante un partido.
- **Granularidad:** una observación por segundo y por equipo en la captura de referencia.
- **Tags:** `partido_id` y `equipo_id`.
- **Timestamp:** instante observado por la fuente, expresado en UTC y enviado como Unix timestamp en milisegundos.
- **Patrones relacionados:** PA1, PA2, PA3, PA4 y PA5; también es la fuente para construir el resumen utilizado por PA6.

| Columna | Categoría | Tipo | Significado y validación |
|---|---|---|---|
| `partido_id` | Tag | String | Identificador estable del partido. Obligatorio. |
| `equipo_id` | Tag | String | Identificador estable del equipo participante. Obligatorio. |
| `posesion_pct` | Field | Float64 | Muestra porcentual entre 0 y 100. |
| `pases_intervalo` | Field | Int64 | Pases completados en el intervalo de un segundo que comienza en `time`. Entero no negativo. |
| `tiros_acumulados` | Field | Int64 | Contador de tiros desde el inicio del partido. Entero no negativo. Una disminución requiere revisión. |
| `time` | Timestamp | Timestamp | Tiempo de observación; precisión de entrada `ms`. |

Se envían las tres medidas en cada observación válida. La validación de rangos, participación y frecuencia corresponde al generador y a la carga: declarar los tipos de las columnas no aplica por sí solo esas reglas.

Ejemplo ilustrativo de line protocol:

```text
estadisticas_equipo,partido_id=PAR-0001,equipo_id=EQ-01 posesion_pct=54.5,pases_intervalo=2i,tiros_acumulados=3i 1790960400000
```

La parte anterior al primer espacio contiene la tabla y los tags. Después aparecen los fields y, al final, el timestamp. El sufijo `i` conserva los conteos como enteros; la escritura debe indicar explícitamente `--precision ms`. El ejemplo representa una muestra del laboratorio, no una carga ya ejecutada ni una afirmación sobre el calendario del torneo.

### 3.2. Histórico: `resumen_equipo_minuto`

- **Fenómeno:** posesión promedio y pases totales de un equipo en una ventana de un minuto.
- **Granularidad lógica:** una ventana por equipo y minuto, identificada mediante sus límites.
- **Tags:** `partido_id` y `equipo_id`.
- **Timestamp:** instante UTC de generación de la versión del resumen, enviado en milisegundos. El período del partido se conserva en los fields `ventana_inicio_ms` y `ventana_fin_ms`.
- **Patrones relacionados:** PA4 y PA6.

| Columna | Categoría | Tipo | Significado |
|---|---|---|---|
| `partido_id` | Tag | String | Partido resumido. |
| `equipo_id` | Tag | String | Equipo resumido. |
| `posesion_promedio` | Field | Float64 | Promedio de las muestras válidas de posesión de la ventana. |
| `pases_total` | Field | Int64 | Suma de pases de intervalos completos, sin superposición. |
| `muestras` | Field | Int64 | Cantidad de observaciones válidas utilizadas. Permite informar cobertura. |
| `ventana_inicio_ms` | Field | Int64 | Inicio UTC del período resumido, como Unix timestamp en milisegundos. |
| `ventana_fin_ms` | Field | Int64 | Fin UTC exclusivo del período resumido, como Unix timestamp en milisegundos. |
| `time` | Timestamp | Timestamp | Instante de generación de esta versión del resumen; precisión de entrada `ms`. |

Las ventanas usan límites `[inicio, fin)`. Un minuto completo de captura a un punto por segundo espera 60 observaciones por equipo. En los bordes del partido se considera solamente el tramo activo; no se agregan ceros para completar minutos.

Un período sin observaciones no produce un resumen con valores cero. Un resumen con menos muestras que las esperadas se informa como parcial. El promedio describe las muestras disponibles y no supone que los huecos tuvieron la misma posesión.

Si llegan observaciones tardías mientras el detalle sigue disponible, se recalcula la ventana y se agrega una nueva versión con un timestamp de generación distinto. Un único escritor serializa estas versiones y garantiza timestamps crecientes y únicos dentro de cada serie. Las consultas históricas seleccionan la versión más reciente de cada combinación de partido, equipo e inicio de ventana; no suman todas sus versiones.

Esta decisión evita depender de sobrescrituras: InfluxDB 3 Core no garantiza qué valor conserva cuando dos escrituras de la misma identidad contienen valores distintos. Como la retención del resumen considera su `time`, su antigüedad se mide desde la generación de la versión. El período deportivo se filtra por los límites de ventana.

No se incluye una suma de `tiros_acumulados` en el resumen: no representa los tiros del período. PA5 conserva la necesidad de consultar ambas muestras de frontera en el detalle.

## 4. Serie resultante e identidad de los puntos

En este modelo, una serie se identifica por la tabla y la combinación de valores de sus tags, dentro de una base. Por ejemplo:

```text
fixture2030_detalle / estadisticas_equipo / partido_id=PAR-0001 / equipo_id=EQ-01
fixture2030_historico / resumen_equipo_minuto / partido_id=PAR-0001 / equipo_id=EQ-01
```

Los fields cambian a lo largo de la serie. El timestamp distingue sus puntos; no se convierte en tag.

Para `P` partidos con datos de sus dos equipos, cada tabla tendrá hasta `2 × P` combinaciones válidas de tags. No se multiplica cada partido por todos los equipos del torneo, porque solamente sus dos participantes generan estadísticas. La frecuencia y las versiones del resumen aumentan los puntos, no las combinaciones de tags. La estimación detallada corresponde al apartado de cardinalidad.

La muestra implementada en Neo4j contiene 96 partidos y, por lo tanto, 192 pares partido–equipo. Los 127 partidos de los Hitos 1 a 3 y de la Clase 9 pertenecen al escenario completo del Fixture; no se presentan como partidos ya cargados en el laboratorio.

La identidad de un punto combina tabla, tags y timestamp. Los reintentos del detalle deben reenviar exactamente los mismos valores. La carga debe detectar valores contradictorios para una identidad existente; no se resolverán suponiendo que la última escritura reemplaza siempre a la anterior. Una observación tardía nueva conserva su tiempo original.

## 5. Relación con los patrones de acceso

| Patrón | Tabla utilizada | Dimensiones y tiempo | Operación e interpretación |
|---|---|---|---|
| PA1 - Registrar una observación | `estadisticas_equipo` | Partido, equipo y tiempo observado. | Escribir un punto con las tres medidas y precisión `ms`. |
| PA2 - Evolución reciente | `estadisticas_equipo` | Partido, equipo y últimos cinco minutos. | Recuperar puntos ordenados por `time`, con huecos y antigüedad del último dato visibles. |
| PA3 - Comparar equipos | `estadisticas_equipo` | Mismo partido y ventana para ambos equipos. | Promediar posesión, sumar pases y calcular la diferencia de tiros entre fronteras. Informar cobertura por equipo. |
| PA4 - Resumen por minuto | `estadisticas_equipo`; resultado conservable en `resumen_equipo_minuto`. | Partido, equipo y ventanas de un minuto. | Calcular promedio, suma y cantidad de muestras. Recalcular ventanas afectadas por puntos tardíos. |
| PA5 - Tiros de un período | `estadisticas_equipo` | Partido, equipo y muestras de inicio y fin. | Restar contador inicial al final. Sin ambas fronteras, o ante un reinicio o corrección, no informar un incremento exacto. |
| PA6 - Evolución histórica | `resumen_equipo_minuto` | Partido, equipo y límites del período resumido. | Recuperar la última versión de cada minuto, con cobertura. Si no existe una representación conservada, indicar ausencia. |

La suma de pases exige ventanas alineadas con los intervalos de captura. La diferencia de tiros recupera también la muestra del límite final, aunque la recuperación general de puntos excluya ese límite. El resumen histórico no permite reconstruir el detalle por segundo ni calcular tiros exactos de un período cuando sus fronteras ya no están disponibles.

## 6. Atributos excluidos de tags

| Atributo | Decisión | Motivo |
|---|---|---|
| Posesión, pases y tiros | Fields numéricos. | Son valores observados que cambian; se comparan y agregan. |
| Timestamp, inicio y fin de ventana | Columna temporal o fields del resumen. | Cambian con cada punto o período; como tags crearían nuevas combinaciones continuamente. |
| Identificador único por observación o versión | No se incorpora como tag. | No responde a los patrones y multiplicaría las series. |
| Nombre del equipo, texto libre y comentarios | No se incorporan. | No son filtros prioritarios de estas consultas; los perfiles permanecen en su módulo. |
| Usuario, jugador y fuente | No se incorporan en este alcance. | Los seis patrones consultan estadísticas del equipo. Se utiliza una fuente de referencia por partido; agregar fuentes exige revisar identidad, consultas y cardinalidad. |

## 7. Alcance técnico

El modelo corresponde a un laboratorio InfluxDB 3 Core de un único nodo, ejecutado mediante Docker Compose. Los datos originales y los resúmenes se conservan en bases separadas para aplicar distintos períodos de retención.

La generación, carga, consulta, agregación y validación se implementan mediante scripts en `scripts/`. Las políticas de conservación y la estimación detallada de cardinalidad se desarrollan en sus documentos correspondientes. Las evidencias registrarán comandos y resultados efectivamente ejecutados en el ambiente local.

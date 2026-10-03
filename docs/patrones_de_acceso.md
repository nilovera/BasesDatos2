# Patrones de acceso - Estadísticas temporales del Fixture 2030

## 1. Objetivo

El módulo InfluxDB del Fixture 2030 registrará estadísticas que cambian durante los partidos. Permitirá recuperar su evolución, comparar equipos y consultar agregados temporales e históricos.

## 2. Problema temporal

Durante un partido llegan observaciones frecuentes de posesión, pases y tiros de cada equipo. Las consultas deben acotar el partido, los equipos y el período que se quiere analizar. El diseño debe distinguir una muestra de posesión, los pases de un intervalo y un contador de tiros acumulados para aplicar una agregación correcta.

## 3. Patrones de acceso

### PA1 - Registrar una observación de un equipo

- **Pregunta prioritaria:** ¿cómo registrar las estadísticas de un equipo en el instante observado?
- **Quién genera:** fuente de estadísticas del partido, simulada por un generador en el laboratorio.
- **Entrada disponible:** identificadores de partido y equipo, instante de observación, posesión, pases del intervalo y tiros acumulados.
- **Rango temporal:** instante de observación; la escritura no recupera un histórico.
- **Dimensiones:** partido y equipo.
- **Medidas:** posesión porcentual, pases completados durante el intervalo de captura y tiros acumulados desde el inicio del partido.
- **Agregación:** ninguna; se registra el detalle de la observación.
- **Frecuencia de llegada esperada:** una observación por segundo y por equipo como referencia inicial.
- **Precisión temporal necesaria:** milisegundos, usando el tiempo de observación de la fuente.
- **Respuesta esperada:** confirmación de escritura o identificación de errores.
- **Ausencia, retraso o dato tardío:** no generar ceros para cubrir interrupciones. Los puntos tardíos conservan su instante original y se incorporan si el detalle todavía está dentro del período de conservación.

### PA2 - Recuperar la evolución reciente de un equipo

- **Pregunta prioritaria:** ¿cómo evolucionaron las estadísticas de un equipo en los últimos cinco minutos?
- **Quién consulta:** consumidor de estadísticas en vivo de la plataforma.
- **Entrada disponible:** identificadores de partido y equipo, inicio y fin del período.
- **Rango temporal:** últimos cinco minutos del partido.
- **Dimensiones:** partido y equipo.
- **Medidas:** posesión, pases del intervalo y tiros acumulados.
- **Agregación:** ninguna; se recuperan los puntos ordenados por tiempo.
- **Frecuencia de llegada esperada:** una observación por segundo y por equipo; consulta frecuente durante el partido.
- **Precisión temporal necesaria:** milisegundos, conservando el detalle original.
- **Respuesta esperada:** secuencia temporal de las tres medidas y el instante del último dato recibido.
- **Ausencia, retraso o dato tardío:** devolver un resultado vacío si no hay puntos e identificar huecos sin interpolarlos. Un retraso de la fuente deja visible la antigüedad del último dato. Los puntos tardíos pueden aparecer al repetir la consulta.

### PA3 - Comparar a los dos equipos de un partido

- **Pregunta prioritaria:** ¿qué diferencias presentan los dos equipos durante una misma ventana temporal?
- **Quién consulta:** consumidor de estadísticas en vivo de la plataforma.
- **Entrada disponible:** identificador del partido, identificadores de ambos equipos e inicio y fin del período.
- **Rango temporal:** ventana común de cinco minutos.
- **Dimensiones:** partido como filtro y equipo para separar los resultados.
- **Medidas:** posesión, pases del intervalo y tiros acumulados.
- **Agregación:** promedio de posesión, suma de pases de intervalos completos y diferencia de tiros acumulados entre los límites del período.
- **Frecuencia de llegada esperada:** una observación por segundo y por equipo; consulta frecuente durante el partido.
- **Precisión temporal necesaria:** milisegundos, con límites y granularidad iguales para ambos equipos.
- **Respuesta esperada:** un resultado por equipo con los agregados y la cobertura del período.
- **Ausencia, retraso o dato tardío:** identificar la comparación como incompleta si falta información de un equipo. Si la fuente se retrasa, informar el último instante observado. Recalcular la ventana cuando se incorporen puntos tardíos.

### PA4 - Obtener un resumen por minuto

- **Pregunta prioritaria:** ¿cuál fue la posesión promedio y cuántos pases completó cada equipo por minuto?
- **Quién consulta:** analista de estadísticas del Fixture.
- **Entrada disponible:** identificador del partido e inicio y fin del tramo solicitado.
- **Rango temporal:** tramo de un partido, agrupado en ventanas de un minuto.
- **Dimensiones:** partido y equipo.
- **Medidas:** posesión y pases del intervalo.
- **Agregación:** promedio de posesión, suma de pases y conteo de muestras para verificar cobertura.
- **Frecuencia de llegada esperada:** una observación por segundo y por equipo; consulta a demanda.
- **Precisión temporal necesaria:** milisegundos en el detalle y ventanas de un minuto en la respuesta.
- **Respuesta esperada:** una fila por equipo y minuto con los agregados y la cantidad de muestras utilizadas.
- **Ausencia, retraso o dato tardío:** distinguir minutos sin datos y resúmenes parciales de valores cero. El retraso de la fuente puede dejar incompleto el último minuto. Los puntos tardíos requieren recalcular la ventana afectada.

### PA5 - Calcular los tiros de un período

- **Pregunta prioritaria:** ¿cuántos tiros registró un equipo entre dos instantes?
- **Quién consulta:** analista de estadísticas del Fixture.
- **Entrada disponible:** identificadores de partido y equipo, inicio y fin del período.
- **Rango temporal:** período solicitado y observaciones de sus límites inicial y final.
- **Dimensiones:** partido y equipo.
- **Medida:** tiros acumulados desde el inicio del partido.
- **Agregación:** diferencia entre el contador final y el inicial; no sumar las lecturas acumuladas.
- **Frecuencia de llegada esperada:** una observación por segundo y por equipo; consulta a demanda.
- **Precisión temporal necesaria:** milisegundos, con límites alineados con la captura.
- **Respuesta esperada:** incremento de tiros del período cuando existen ambas muestras de frontera y el contador no presenta reinicios ni correcciones.
- **Ausencia, retraso o dato tardío:** si falta una frontera, no informar un incremento exacto. Un retraso puede dejar pendiente la frontera final. Revisar disminuciones del contador y recalcular si llegan datos tardíos que modifican los límites.

### PA6 - Consultar la evolución histórica de un partido

- **Pregunta prioritaria:** ¿cómo evolucionaron las estadísticas de los equipos en un partido finalizado?
- **Quién consulta:** analista de estadísticas del Fixture.
- **Entrada disponible:** identificador del partido, equipos e inicio y fin del período histórico.
- **Rango temporal:** período solicitado dentro del partido finalizado.
- **Dimensiones:** partido y equipo.
- **Medidas:** posesión y pases por período.
- **Agregación:** resúmenes por minuto con promedio de posesión, suma de pases y cobertura.
- **Frecuencia de llegada esperada:** una observación por segundo y por equipo mientras el partido está activo; consulta histórica ocasional.
- **Precisión temporal necesaria:** ventanas de un minuto con límites temporales explícitos.
- **Respuesta esperada:** evolución resumida por equipo, con la granularidad disponible según la conservación del dato.
- **Ausencia, retraso o dato tardío:** indicar ausencia si el período no tiene una representación conservada. Identificar resúmenes incompletos por retrasos de la fuente y actualizar los afectados por datos tardíos mientras el detalle siga disponible.

## 4. Criterios de interpretación

| Medida | Significado | Agregación correcta |
|---|---|---|
| Posesión porcentual | Muestra decimal entre 0 y 100. | Promedio de muestras equiespaciadas, indicando cobertura si hay huecos. |
| Pases del intervalo | Conteo entero no negativo de pases durante el intervalo de captura. | Suma de intervalos completos, sin superposición ni duplicación. |
| Tiros acumulados | Contador entero no negativo desde el inicio del partido. | Diferencia entre límites para un período; última lectura para el estado actual. |

Cada conteo de pases corresponde al intervalo que comienza en el instante registrado y dura un segundo en la captura de referencia. Las ventanas de recuperación incluyen el inicio y excluyen el fin: `[inicio, fin)`. Para calcular diferencias de contadores se recupera también la muestra del límite final. La suma de pases requiere límites alineados con los intervalos de captura. La ausencia de una observación no equivale a un valor cero.

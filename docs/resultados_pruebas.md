# Resultados de pruebas

## Ambiente

La prueba se ejecutó localmente con:

- Sistema operativo: Windows con WSL2 y Docker Desktop.
- Procesador: Intel Core 5 120U.
- Núcleos físicos: 10.
- Procesadores lógicos: 12.
- Memoria RAM: 13,7 GB.
- InfluxDB: 3 Core 3.12.0.
- Puerto local: 8181.
- Persistencia: `~/docker/data/influxdb`.

## Volumen generado

El generador creó estadísticas para un partido entre Argentina y México:

- Duración simulada: 90 minutos.
- Frecuencia: un punto cada 10 segundos por equipo.
- Equipos: 2.
- Puntos por equipo: 540.
- Total generado: 1.080 puntos.
- Precisión temporal: segundos.
- Series resultantes: 2 combinaciones de `partido_id` y `equipo_id`.

## Método de carga

Los datos se generaron en line protocol y se cargaron en cinco lotes:

| Lote | Puntos |
|---:|---:|
| 1 | 250 |
| 2 | 250 |
| 3 | 250 |
| 4 | 250 |
| 5 | 80 |
| Total | 1.080 |

La carga utilizó el CLI `influxdb3 write`, autenticación mediante variable de entorno y precisión explícita `s`.

## Resultado medido

- Puntos enviados: 1.080.
- Puntos verificados: 1.080.
- Lotes procesados: 5.
- Tamaño máximo de lote: 250.
- Tiempo total observado: 5.144 ms.
- Rendimiento aproximado de la ejecución completa: 210 puntos por segundo.

Este resultado corresponde únicamente al ambiente local descripto. No representa el rendimiento máximo de InfluxDB ni permite afirmar que se hayan cargado 10 millones de puntos.

## Consultas verificadas

Se ejecutaron correctamente:

1. Ventana temporal de un minuto para Argentina.
2. Filtro por `partido_id` y `equipo_id`.
3. Comparación entre Argentina y México.
4. Promedio de posesión.
5. Suma de pases por intervalo.
6. Máximo del contador acumulado de tiros.
7. Agregación en ventanas de 15 minutos.
8. Validación de cantidad y distribución de puntos.

Los resultados mostraron:

- 540 puntos para Argentina.
- 540 puntos para México.
- 1.080 puntos totales.
- Rango temporal desde `2030-06-13T20:00:00` hasta `2030-06-13T21:29:50`.
- 12 resúmenes históricos.

## Downsampling

Los 1.080 puntos originales se redujeron a 12 puntos históricos:

- Seis ventanas para Argentina.
- Seis ventanas para México.
- Granularidad de 15 minutos.
- Retención histórica de 365 días.

## Persistencia

Después de reiniciar el contenedor se verificó que permanecieran:

- 1.080 puntos detallados.
- 12 resúmenes históricos.

Esto confirma que el montaje persistente conserva el catálogo y los datos.

## Manejo de errores

Durante la prueba se detectó que el envío por entrada estándar desde PowerShell agregaba finales de línea CRLF incompatibles con el parser de line protocol. La carga se corrigió generando archivos UTF-8 sin BOM con saltos LF y montando la carpeta `datos` como solo lectura dentro del contenedor.

El script detiene la ejecución si un lote devuelve un código de error. En una estrategia de mayor volumen también se registrarían lotes fallidos y se aplicarían reintentos controlados.

## Proyección hacia 10M+ puntos

La prueba local no intenta simular 10 millones de puntos. Para alcanzar ese objetivo se propone:

- Generar datos por streaming para evitar mantener todo el volumen en memoria.
- Mantener timestamps ordenados por fuente.
- Utilizar lotes medidos y ajustar su tamaño progresivamente.
- Incorporar concurrencia controlada.
- Registrar errores y reintentar únicamente lotes fallidos.
- Validar cantidades por partido, equipo y rango temporal.
- Aplicar retención de 7 días al detalle.
- Mantener resúmenes de 15 minutos durante 365 días.
- Escalar horizontalmente o utilizar una edición distribuida cuando el volumen y la concurrencia superen la capacidad del nodo local.

## Evidencias

Las capturas se encuentran en `docs/evidencia` e incluyen ambiente, modelo, carga, consultas, agregación, retención, validación y persistencia.

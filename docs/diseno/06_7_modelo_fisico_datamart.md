# 6.7 Modelo físico del Data Mart

## Responsabilidad y grano

PostgreSQL funciona como destino analítico separado. No confirma partidos ni
eventos. Recibe datos de MongoDB y resúmenes InfluxDB mediante un refresh ETL
explícito, con frescura dependiente de la última ejecución.

| Estructura | Grano y propósito |
|---|---|
| dim_torneo, dim_equipo, dim_jugador, dim_partido | Contexto descriptivo y claves de negocio comunes |
| dim_fecha, dim_tipo_evento | Calendario y clasificación de hechos |
| fact_evento_partido | Una fila por evento efectivo extraído, con métricas de goles/asistencias |
| fact_estadistica_equipo_15m | Una fila por partido, equipo y ventana de 15 minutos |
| etl_ejecucion | Estado y conteos de una carga |

Separar hechos evita mezclar granularidades: sumar una estadística de ventana
como si fuera un evento duplicaría o distorsionaría resultados. Las claves
naturales y `ON CONFLICT` evitan duplicar filas al repetir una carga idéntica.

## ETL y correcciones

La extracción MongoDB resuelve los eventos efectivos según las correcciones
disponibles. El refresh actual realiza UPSERT de lo extraído, no una eliminación
general de hechos que dejaron de aparecer en un snapshot posterior. Por ello
la idempotencia de una carga idéntica no debe interpretarse como reconciliación
completa de todas las correcciones o eliminaciones históricas. Ese caso requiere
un mecanismo específico y una prueba posterior a una carga ya materializada.

Los resúmenes dependen de la ingesta y agregación InfluxDB. El simulador actual
no genera por sí solo todas las estadísticas de equipo de 15 minutos. Un
refresh exitoso no demuestra la existencia de datos que no fueron ingresados.

## Conexiones y rendimiento

Se utiliza PostgreSQL persistente y un pool de conexiones Psycopg. La primera
comparación sin pool mostró p95 Data Mart de 28,853 ms frente a 21,554 ms de la
consulta operacional. La segunda, con pool, registró 23,143 ms frente a 46,363 ms.
Ambas usaron 100 consultas por alternativa y un partido, con resultados
equivalentes y cero errores. También hay mediciones de los dos endpoints bajo
carga mixta.

Estos resultados acreditan las ejecuciones concretas. Las variaciones entre
ejecuciones no aíslan causalmente el efecto del pool y el volumen es pequeño.
No se declara una ventaja universal ni una mejora a escala representativa.

## Operación y validación

La instancia de un nodo conserva volumen y credencial por archivo, con salud,
contadores de ETL/consulta y falla controlada registrada. No participa en la
transacción oficial. Su caída degrada analítica y no cambia el marcador.

Detalle de mediciones: [rendimiento Data Mart](../rendimiento/hito_12_datamart.md).
Evidencias: [estado de validación](../estado_validacion.md).

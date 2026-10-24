# Evidencia del Hito 12

Todo lo que hay en esta carpeta fue **generado por los scripts** al ejecutar las pruebas en la notebook del equipo el 24/10/2026. No hay valores escritos a mano.

| Archivo / carpeta | Qué contiene | Script que lo genera |
|---|---|---|
| `resultados_linea_base.md` / `.json` | Resumen de todas las corridas de línea base (y la v1 descartada): condiciones, global, por fase, por operación, recursos, integridad | `resumir_evidencia.py` |
| `resultados_optimizados.md` / `.json` | Igual para las corridas optimizadas | `resumir_evidencia.py` |
| `tablas_o_graficos.md` | Índice con los 5 gráficos, la tabla del diagnóstico de IRIS y la del Data Mart | `resumir_evidencia.py` |
| `preparacion_datos.json` | Claves por tipo, datos sintéticos creados y verificación de determinismo | `preparar_datos.py` |
| `humo_20261024-193640/` | Prueba de humo (20 s, 2 VUs) | `ejecutar_carga.py` + `validar_integridad.py` |
| `v1_linea_base_generador_1proceso_20261024-194009/` | Primer intento de línea base: el generador de 1 proceso era el cuello de botella (no se usa para comparar) | idem |
| `linea_base_20261024-195501/` | Línea base 1, commit `657a285` | `ejecutar_linea_base.ps1` |
| `optimizada_20261024-200735/` | Optimizada 1, commit `542a1d8`, `IRIS_POOL_SIZE=5` (incluye congelamiento de ~4 s) | `ejecutar_prueba_optimizada.ps1` |
| `linea_base_20261024-201624/` | Línea base 2 (repetición), commit `542a1d8`, `IRIS_POOL_SIZE=0` | `ejecutar_linea_base.ps1` |
| `optimizada_20261024-202348/` | Optimizada 2 (repetición) | `ejecutar_prueba_optimizada.ps1` |
| `diagnostico_iris.json` | Conexión nueva vs. reutilizada directo contra IRIS y límite de 8 conexiones | `diagnostico_iris.py` |
| `comparacion/` | `comparacion.md`, `comparacion.json` y 5 gráficos PNG (antes/después y repeticiones) | `comparar_resultados.py` |
| `data_mart_construccion.json` | Conteos fuente vs. destino, validaciones y observaciones de calidad del lote | `construir_data_mart.py` |
| `data_mart_comparacion.json` | Fuentes operacionales vs. Data Mart: tiempos, llamadas y respuesta | `consultar_data_mart.py` |
| `capturas_redactadas/` | Capturas de la consola de cada ejecución (sin credenciales) | — |

Contenido de cada carpeta de corrida:

| Archivo | Contenido |
|---|---|
| `metadatos.json` | Fecha, commit y rama, si había cambios sin commitear, versiones de paquetes, hardware, contenedores e imágenes, `/health/ready` previo, configuración completa de la prueba, resumen del catálogo |
| `resumen.json` | Métricas globales, por fase, por operación y por operación en el sostenimiento; recursos por fase |
| `solicitudes.csv.gz` | Una fila por solicitud: `request_id`, tiempo, fase, VUs, proceso, operación, clave, código HTTP, latencia, tiempo en la API, error, integridad |
| `recursos.csv` | Muestra cada 2 s: CPU/RAM del sistema, de la API y del generador, retraso del event loop, CPU y memoria de cada contenedor |
| `serie_tiempo.csv` | Ventanas de 5 s: req/s, errores, P50, P95, P95 dentro de la API, P95 de IRIS |
| `integridad.json` | Los 8 controles de `validar_integridad.py` |

Capturas:

| Captura | Muestra |
|---|---|
| `01_prueba_de_humo.png` | Humo + validación |
| `02_linea_base_v1_generador_1proceso.png` | Línea base con generador saturado |
| `03_linea_base_v2_y_diagnostico_iris.png` | Línea base 1 válida + diagnóstico de IRIS |
| `04_diagnostico_iris_limite_licencias.png` | Primer diagnóstico: "Unable to allocate a license" al abrir 20 conexiones |
| `05_optimizada_1_y_comparacion.png` | Optimizada 1 + comparación automática |
| `06_linea_base_2_repeticion.png` | Repetición de la línea base |
| `07_optimizada_2_repeticion.png` | Repetición de la optimizada + comparación |
| `08_data_mart.png` | Construcción del Data Mart y comparación con las fuentes |

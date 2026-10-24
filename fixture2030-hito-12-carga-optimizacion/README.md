# Hito 12 — Pruebas de carga y optimización del Fixture 2030

Ingeniería de Datos II · Grupo 10 · Rama `Carga` (sale de `Conectividad`)

Prueba de carga **reproducible** sobre la API integrada del Fixture 2030 (Hitos 10 y 11). Incluye la línea base, el cuello de botella detectado, una optimización justificada, la repetición en las mismas condiciones, la validación de integridad, un prototipo de Data Mart medido contra las fuentes operacionales y la comparación con una estructura relacional.

## Resultado en una tabla

Escenario "pico alrededor de un partido": 6 operaciones de lectura sobre las 6 bases, de 5 a 80 usuarios virtuales, 5 min 30 s. Dos corridas de cada versión, mismo escenario, datos, semilla y hardware.

| Métrica (medida) | Línea base (sin pool) | Optimizada (pool IRIS = 5) | Variación |
|---|---:|---:|---:|
| Tiempo de IRIS dentro de la API, P50 (sostenimiento) | 33,9 / 34,1 ms | **5,3 / 5,4 ms** | **−84 %** |
| Latencia del endpoint IRIS vista por el cliente, P95 (sostenimiento) | 89,1 / 90,7 ms | 58,7 / 63,4 ms | −30 a −34 % |
| CPU del contenedor IRIS (sostenimiento) | 56,8 / 58,0 % | **2,5 / 1,9 %** | −96 % |
| CPU del proceso de la API (sostenimiento) | 85,3 / 86,1 % | 69,4 / 70,1 % | −19 % |
| Latencia P95 global (todas las operaciones) | 135,4 / 135,2 ms | 119,9 / 124,4 ms | −8 a −11 % |
| Throughput en el pico de 80 VUs | 333,9 / 334,1 req/s | 306,9* / 364,0 req/s | +9 % (corrida 2) |
| Solicitudes con error | 0 / 0 | 0 / 0 | — |
| Controles de integridad aprobados | 8/8 · 8/8 | 8/8 · 8/8 | — |

\* La corrida optimizada 1 tuvo un congelamiento de ~4 s de la API (también observado en una corrida sin pool). Ver [`docs/integridad_y_limitaciones.md`](docs/integridad_y_limitaciones.md).

**Decisión del equipo:** se adopta el pool de conexiones de IRIS con tamaño 5 (`IRIS_POOL_SIZE=5`). Costo principal: IRIS Community acepta **8 conexiones simultáneas en total** (medido), así que el pool queda acotado y, si se usaran varias instancias de la API, habría que repartir ese cupo. Detalle en [`docs/hipotesis_y_optimizacion.md`](docs/hipotesis_y_optimizacion.md).

**Data Mart (prototipo medido):** responder "¿en qué ventanas de 10 minutos se concentran los comentarios y qué eventos ocurrieron?" para los 96 partidos tarda **8,7 s y 1.536 llamadas HTTP** desde las fuentes operacionales, contra **0,57 ms y 2 consultas SQL** desde la proyección analítica, con **la misma respuesta** en ambos caminos.

## Estructura

```text
fixture2030-hito-12-carga-optimizacion/
├── README.md                                 este archivo
├── compose-o-instrucciones-del-entorno.md    servicios, versiones, hardware y cómo levantarlos
├── requirements.txt                          psutil y matplotlib (se agregan al .venv de la API)
├── config/
│   ├── configuracion-ejemplo.json            escenario, mezcla, fases, semilla (versionado, sin secretos)
│   └── .gitignore                            excluye config/configuracion.json local
├── scripts/
│   ├── comun.py                              utilidades: rutas, huellas, metadatos del entorno
│   ├── preparar_datos.py                     datos sintéticos + catálogo de claves con huellas
│   ├── ejecutar_carga.py                     generador de carga y medición (4 procesos)
│   ├── ejecutar_linea_base.ps1               reinicia la API sin pool, carga y valida
│   ├── ejecutar_prueba_optimizada.ps1        reinicia la API con pool, carga, valida y compara
│   ├── validar_integridad.py                 8 controles de integridad por corrida
│   ├── diagnostico_iris.py                   prueba de la hipótesis directo contra IRIS
│   ├── comparar_resultados.py                tablas y gráficos antes/después + repeticiones
│   ├── resumir_evidencia.py                  resultados_linea_base / resultados_optimizados / tablas_o_graficos
│   ├── construir_data_mart.py                ETL del prototipo de Data Mart (SQLite)
│   ├── consultar_data_mart.py                fuentes operacionales vs. Data Mart (medido)
│   └── limpiar_datos_de_prueba.py            borra solo los datos sintéticos H12
├── docs/
│   ├── flujo_y_escenario_de_carga.md
│   ├── linea_base.md
│   ├── hipotesis_y_optimizacion.md
│   ├── integracion_data_mart.md
│   ├── comparacion_relacional.md
│   ├── integridad_y_limitaciones.md
│   └── evidencia/
│       ├── resultados_linea_base.md / .json  resumen de las corridas de línea base
│       ├── resultados_optimizados.md / .json resumen de las corridas optimizadas
│       ├── tablas_o_graficos.md              índice de tablas y gráficos
│       ├── comparacion/                      comparacion.md + 5 gráficos PNG
│       ├── capturas_redactadas/              capturas de consola sin secretos
│       └── <etiqueta>_<fecha-hora>/          datos crudos de cada corrida
└── datos-o-generadores/
    ├── README.md
    └── catalogo_claves.json                  claves usadas por la carga y huella de cada respuesta
```

Cambios en la API (fuera de esta carpeta, commit `542a1d8`): `app/adapters/iris.py` (pool), `app/config/settings.py` (`iris_pool_size`, por defecto 0) y `.env.example` (`IRIS_POOL_SIZE`).

## Requisitos

- Windows 10/11 con PowerShell 5.1+, Docker Desktop y los 6 contenedores del Fixture levantados con sus datos (ver [`compose-o-instrucciones-del-entorno.md`](compose-o-instrucciones-del-entorno.md)).
- La API de la rama en `.\` con su `.venv` y su `.env` completo (no se versiona).
- Cerrar aplicaciones pesadas durante las corridas: la prueba usa hasta 4 núcleos para el generador y 1 para la API.

## Orden de ejecución

Todos los comandos se corren **desde la carpeta raíz de la API** (`C:\...\api`).

```powershell
# 0. Una sola vez: dependencias del hito en el .venv de la API
.\.venv\Scripts\python.exe -m pip install -r .\fixture2030-hito-12-carga-optimizacion\requirements.txt

# 1. Levantar la API
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\reiniciar_api.ps1

# 2. Preparar datos sintéticos y catálogo (idempotente, ~1 min)
.\.venv\Scripts\python.exe .\fixture2030-hito-12-carga-optimizacion\scripts\preparar_datos.py

# 3. Prueba de humo (20 s, 2 VUs) -> verifica que todo el circuito funcione
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-12-carga-optimizacion\scripts\ejecutar_linea_base.ps1 -Escenario humo

# 4. Línea base completa (IRIS_POOL_SIZE=0, ~6,5 min)
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-12-carga-optimizacion\scripts\ejecutar_linea_base.ps1

# 5. Diagnóstico de la hipótesis directo contra IRIS (~1 min)
.\.venv\Scripts\python.exe .\fixture2030-hito-12-carga-optimizacion\scripts\diagnostico_iris.py

# 6. Prueba optimizada (IRIS_POOL_SIZE=5) + validación + comparación (~7 min)
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-12-carga-optimizacion\scripts\ejecutar_prueba_optimizada.ps1

# 7. (Recomendado) repetir 4 y 6 para medir la variación entre corridas
#    y regenerar los resúmenes de evidencia
.\.venv\Scripts\python.exe .\fixture2030-hito-12-carga-optimizacion\scripts\resumir_evidencia.py

# 8. Data Mart: construir la proyección y compararla con las fuentes operacionales
.\.venv\Scripts\python.exe .\fixture2030-hito-12-carga-optimizacion\scripts\construir_data_mart.py
.\.venv\Scripts\python.exe .\fixture2030-hito-12-carga-optimizacion\scripts\consultar_data_mart.py
```

Cada corrida deja una carpeta `docs/evidencia/<etiqueta>_<fecha-hora>/` con `metadatos.json` (commit, versiones, hardware, contenedores, configuración), `resumen.json`, `solicitudes.csv.gz` (una fila por solicitud), `recursos.csv`, `serie_tiempo.csv` e `integridad.json`. La comparación queda en `docs/evidencia/comparacion/`.

## Limpieza segura

La prueba es solo de lectura: no modifica datos de otros hitos. Los datos sintéticos (sesiones `SES-H12-*` en Redis, partidos `PAR-H12*` en IRIS y 28.800 comentarios marcados "sintético H12" en Cassandra) se pueden borrar sin tocar nada más:

```powershell
.\.venv\Scripts\python.exe .\fixture2030-hito-12-carga-optimizacion\scripts\limpiar_datos_de_prueba.py --confirmar
```

No borra la evidencia ni el catálogo. Para volver a probar, repetir desde el paso 2. Las sesiones de Redis expiran solas a las 4 h (`ttl_sesiones_s`); si expiran, basta con volver a correr `preparar_datos.py`.

## Seguridad

No se versionan `.env`, tokens, contraseñas ni `config/configuracion.json`. Los scripts leen las credenciales del `.env` de la API y la evidencia solo guarda parámetros no secretos (ver `metadatos.json → config_api`). El Data Mart SQLite se regenera con el script y está en `.gitignore`.

## Documentación

| Documento | Contenido |
|---|---|
| [`docs/flujo_y_escenario_de_carga.md`](docs/flujo_y_escenario_de_carga.md) | Flujo elegido, escenario, datos de prueba y método de medición |
| [`docs/linea_base.md`](docs/linea_base.md) | Línea base v1 (generador saturado) y v2, métricas, recursos, estabilidad |
| [`docs/hipotesis_y_optimizacion.md`](docs/hipotesis_y_optimizacion.md) | Cuello de botella, prueba de la hipótesis, cambio, repetición, comparación y trade-offs |
| [`docs/integracion_data_mart.md`](docs/integracion_data_mart.md) | Pregunta analítica, fuentes, grano, ETL, frescura, procedencia y medición |
| [`docs/comparacion_relacional.md`](docs/comparacion_relacional.md) | Alternativa relacional condicionada al flujo y al Data Mart |
| [`docs/integridad_y_limitaciones.md`](docs/integridad_y_limitaciones.md) | Validaciones, anomalías observadas, límites del laboratorio y próximos pasos |
| [`docs/evidencia/tablas_o_graficos.md`](docs/evidencia/tablas_o_graficos.md) | Índice de tablas y gráficos generados automáticamente |
| [`docs/evidencia/resultados_linea_base.md`](docs/evidencia/resultados_linea_base.md) · [`resultados_optimizados.md`](docs/evidencia/resultados_optimizados.md) | Resultados de cada corrida |

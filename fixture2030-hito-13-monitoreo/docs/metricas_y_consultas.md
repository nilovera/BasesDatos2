# Métricas y consultas PromQL (RF8, RF11, punto 5.2)

Todas las consultas de este documento se usan en el dashboard ([`grafana/dashboards/fixture2030.json`](../grafana/dashboards/fixture2030.json)), en las reglas ([`prometheus/reglas-o-alertas.yml`](../prometheus/reglas-o-alertas.yml)) o en la prueba controlada ([`scripts/ejecutar_prueba_controlada.py`](../scripts/ejecutar_prueba_controlada.py)). Los valores "medidos" salen de `evidencia/prueba_de_falla_redis_corte*/prometheus_series.json`: el script guarda allí el resultado de cada consulta, cada 5 s, durante la prueba.

## 1. Configuración de Prometheus (punto 5.2)

| Parámetro | Valor | Dónde | Por qué |
|---|---|---|---|
| Intervalo de scraping | **15 s** | `global.scrape_interval` | Igual al de la clase. Con una caída de 120 s se obtienen ~8 muestras; no agrega carga apreciable |
| Timeout de scraping | 10 s | `global.scrape_timeout` | Si una base está caída, el ping de la API puede tardar hasta ~6 s (timeout del driver + 1 s) |
| Evaluación de reglas | 15 s | `global.evaluation_interval` | Una alerta con `for: 1m` necesita 4 evaluaciones seguidas |
| Retención | **15 días** | `--storage.tsdb.retention.time=15d` en el compose | Cubre una semana de partidos y la defensa; en el laboratorio el volumen ocupa pocos MB |
| Etiquetas | `capa`, `componente`, `modelo`, `mecanismo` en cada target; `proyecto=fixture2030` global | `prometheus.yml` | Permiten agrupar por base o por capa sin depender del nombre del job |
| Recarga sin reiniciar | `--web.enable-lifecycle` | compose | `curl -X POST http://localhost:9090/-/reload` |

Los targets, sus endpoints y su relación con cada componente están en [`inventario_de_componentes.md`](inventario_de_componentes.md). Cómo validar que un target está UP o investigar uno DOWN: [README, sección 6](../README.md#6-validar-un-target-up-e-investigar-uno-down).

## 2. Métricas de aplicación (instrumentación propia de la API)

Se diferencian de las de infraestructura por el prefijo `fixture_` y por la etiqueta `capa="aplicacion"` del target (RF4).

| Métrica | Tipo | Etiquetas | Qué mide |
|---|---|---|---|
| `fixture_http_requests_total` | Counter | `metodo`, `ruta` (plantilla), `codigo`, `dependencia` | Solicitudes atendidas. `dependencia` = base que atiende la ruta (la misma que ya registraba el log del Hito 10) |
| `fixture_http_request_duration_seconds` | Histogram | `metodo`, `ruta`, `dependencia` | Tiempo dentro del proceso de la API (= encabezado `X-Process-Time-Ms`). Buckets de 5 ms a 10 s |
| `fixture_http_requests_in_progress` | Gauge | — | Solicitudes en curso al momento del scraping |
| `fixture_dependencia_up` | Gauge | `dependencia` | 1 si el ping del adaptador (Hito 11) funcionó. Se calcula con la caché de 15 s del Hito 11: el scraping no agrega carga a las bases |
| `fixture_dependencia_chequeo_segundos` | Gauge | `dependencia` | Duración de ese ping |
| `fixture_api_proceso_cpu_segundos_total` | Counter | — | Segundos de CPU del proceso uvicorn (psutil) |
| `fixture_api_proceso_memoria_bytes` | Gauge | — | Memoria residente del proceso |
| `fixture_corte_rapido_rechazos_total` / `_aperturas_total` / `_abierto` | Counter / Gauge | `dependencia` | Mejora transversal de este hito (ver [`decisiones_de_arquitectura.md`](decisiones_de_arquitectura.md#6-mejora-transversal-corte-rápido-por-base-rf12)) |
| `fixture_api_info` | Info | `version`, `iris_pool_size`, `corte_rapido_segundos` | Configuración con la que corre la API: queda registrada junto a cada medición (RNF2) |

**Decisión de cardinalidad:** la etiqueta `ruta` usa la **plantilla** (`/api/v1/partidos/{codigo}/eventos`) y no la URL real. Con 96 partidos, 64 equipos y 300 sesiones, usar la URL habría creado miles de series. Con la plantilla, la API expone **66 series** en total (medido en `metricas_disponibles.json`).

## 3. Consultas PromQL explicadas

### Q1 · Throughput por base (volumen)

```promql
sum by (dependencia) (rate(fixture_http_requests_total{ruta=~"/api/v1/.*"}[1m]))
```

- **Qué mide:** solicitudes de negocio por segundo, separadas por la base que las atiende. `rate` calcula el aumento por segundo del contador en la ventana; `sum by` junta métodos, rutas y códigos.
- **Unidad:** solicitudes/s. **Período:** ventana móvil de 1 min, evaluada cada 15 s.
- **Por qué `/api/v1/.*`:** excluye `/health/*` (lo usa el diagnóstico) y `/metrics` (no se cuenta), para medir solo el tráfico del Fixture.
- **Medido:** ~135 req/s totales con 20 usuarios (Cassandra ~37, InfluxDB ~24, Redis ~20, Neo4j ~18, MongoDB ~11, IRIS ~11; respeta la mezcla 30/20/15/15/10/10 del Hito 12). Con Redis caído y sin corte rápido el total bajó a **47 req/s**; con el corte v2 se mantuvo en **138 req/s**.

### Q2 · Latencia P95 global y por base

```promql
histogram_quantile(0.95, sum by (le) (rate(fixture_http_request_duration_seconds_bucket{ruta=~"/api/v1/.*"}[1m])))
histogram_quantile(0.95, sum by (le, dependencia) (rate(fixture_http_request_duration_seconds_bucket{ruta=~"/api/v1/.*"}[1m])))
```

- **Qué mide:** el tiempo por debajo del cual quedan el 95 % de las solicitudes, calculado a partir de los buckets del histograma.
- **Unidad:** segundos (Grafana los muestra en ms). **Período:** 1 min en el dashboard; **5 min** en la alerta (más estable).
- **Medido (dentro de la API):** P95 global ≈ 21 ms en condiciones normales; por base: MongoDB ~5 ms, IRIS ~7-8 ms, Neo4j ~7-9 ms, InfluxDB ~15-20 ms, Cassandra ~24 ms. **Con Redis caído y sin corte rápido el P95 global subió a ~2,0 s** y el de Redis a 2,4-2,8 s.
- **Precisión:** el valor sale de interpolar dentro de un bucket (5, 10, 25, 50 ms…). "4,9 ms" significa "casi todas por debajo de 5 ms", no un valor exacto.
- **Diferencia con el lado cliente:** el generador midió un P95 de ~125-135 ms para las mismas solicitudes. La diferencia (~100 ms) es tiempo **fuera** del código de la API: cola del servidor uvicorn (un solo proceso), red local y el propio generador en la misma notebook. Es la misma diferencia que se vio en el Hito 12 entre el tiempo del cliente y `X-Process-Time-Ms`. Por eso el P95 de las otras bases "subió" de 40 a 127-136 ms entre la prueba 1 y las otras: en la prueba 1 la API recibía 3 veces menos tráfico.

### Q3 · Proporción de errores 5xx (errores)

```promql
sum(rate(fixture_http_requests_total{ruta=~"/api/v1/.*", codigo=~"5.."}[2m]))
/
sum(rate(fixture_http_requests_total{ruta=~"/api/v1/.*"}[2m]))
```

- **Qué mide:** fracción de solicitudes de negocio que terminaron con un error del lado servidor (503 = base no disponible, 504 = timeout, 500 = error inesperado). Los 404 (clave inexistente) y 422 (parámetro inválido) **no** cuentan como falla.
- **Unidad:** proporción 0-1 (Grafana: %). **Período:** ventana de 2 min (también es la regla de registro `fixture:proporcion_errores_5xx:2m`).
- **Medido:** 0 % en todas las fases normales; **12,9 %** al dispararse la alerta durante la caída de Redis (captura `06_prometheus_alerta_errores_5xx.png`). Del lado cliente, 15,2 %: coincide con el 15 % de la mezcla que corresponde a sesiones.

### Q4 · Disponibilidad de cada base en dos capas

```promql
max by (dependencia) (fixture_dependencia_up)                  # la API puede usar la base
max by (componente) (probe_success{job="sonda-tcp"})            # el puerto acepta conexiones
```

- **Qué mide:** 1 = disponible, 0 = no. Comparar ambas separa una caída del motor (las dos en 0) de un problema de credenciales, base de datos o namespace (puerto en 1, API en 0), como el que clasifica `/health/dependencias` del Hito 11.
- **Unidad:** booleano. **Período:** valor instantáneo, resolución de 15 s (más 15 s de caché en la API).
- **Medido:** al detener Redis, Prometheus registró el puerto cerrado entre **4 y 15 s** después del `docker stop`, y la API lo vio caído entre **14 y 30 s** después. Al reiniciarlo, ambos volvieron a 1 en 15-30 s. En el incidente real de IRIS (ver limitaciones) el puerto estaba abierto pero la API lo veía caído: justamente el caso que distingue esta comparación.

### Q5 · CPU del proceso de la API (saturación)

```promql
rate(fixture_api_proceso_cpu_segundos_total[1m]) * 100
```

- **Qué mide:** porcentaje de **un** núcleo usado por el proceso de la API.
- **Unidad:** % de un núcleo. **Período:** 1 min.
- **Medido:** ~29 % con 135 req/s. Sirve para responder "¿dónde está el cuello de botella?": en el Hito 12, con ~330 req/s, la API llegó a 70-86 %. Con un solo proceso uvicorn, el límite está en la API antes que en las bases.

### Q6 · Uso de licencias de IRIS y memoria de Redis (capacidad)

```promql
max(iris_license_percent_used)
sum(redis_memory_used_bytes) / sum(redis_memory_max_bytes > 0)
```

- **Unidad:** % y proporción. **Período:** valor instantáneo.
- **Medido:** IRIS 13 % de licencias con el pool de 5 de la API; Redis 0,65 % de sus 256 MB (captura `10_grafana_comparacion_bases.png`).

## 4. Reglas de registro

Para que el dashboard y las alertas midan lo mismo, Prometheus precalcula ([`reglas-o-alertas.yml`](../prometheus/reglas-o-alertas.yml)):

| Regla | Expresión (resumen) | Uso |
|---|---|---|
| `fixture:solicitudes:rate1m` | Q1 | Condición de tráfico mínimo de las alertas |
| `fixture:errores_5xx:rate1m` | errores por base, 1 min | Análisis |
| `fixture:latencia_p95_segundos:5m` | Q2 por base, 5 min | Análisis |
| `fixture:latencia_p95_global_segundos:5m` | Q2 global, 5 min | Alerta `FixtureLatenciaP95Alta` |
| `fixture:proporcion_errores_5xx:2m` | Q3 | Alerta `FixtureErrores5xxAltos` |

## 5. Relación con los objetivos del TPO (RF11)

| Objetivo del TPO | Métrica que lo evidencia | Resultado observado |
|---|---|---|
| **Concurrencia** | `fixture_http_requests_in_progress`, CPU del proceso (Q5) | 20 usuarios virtuales → ~19 solicitudes en curso y ~29 % de un núcleo. La concurrencia la limita la API (un proceso), no las bases |
| **Throughput** | Q1 | ~135 req/s estables; sin corte rápido, la caída de **una** base bajó el total un 65 % |
| **Latencia** | Q2 | P95 interno ~21 ms; ningún motor supera 25 ms de P95. El dominante es Cassandra (lectura de una partición de 25 comentarios) |
| **Disponibilidad** | Q4 + alertas | Caída de Redis detectada en 4-30 s; las otras 5 bases respondieron **0 errores** en las 3 pruebas |
| **Distribución** | `dependencia` en todas las métricas de aplicación | La carga se reparte como se diseñó (30/20/15/15/10/10); se puede ver el peso de cada base en el total |
| **Recuperación** | Q4 + `api_ve_recuperada` | La API volvió a usar Redis 6-14 s después del `docker start`; las alertas de disponibilidad se resolvieron solas 15-30 s después y la de errores cuando su ventana de 2 min dejó de incluir la falla; datos idénticos antes y después (huellas) |

# Inventario de componentes monitoreados (punto 5.1)

Relevado el 30/10/2026 en la notebook del grupo (Windows + Docker Desktop con WSL2), commit `27b8139` y siguientes de la rama `monitoreo`. Fuente de cada fila: [`prometheus.yml`](../prometheus.yml), [`evidencia/prometheus_targets.md`](../evidencia/prometheus_targets.md) y [`evidencia/resultados_sin_secretos/metricas_disponibles.json`](../evidencia/resultados_sin_secretos/metricas_disponibles.json) (lista completa de métricas que entrega cada job).

Regla aplicada: **una base se declara monitoreada solo si hay una métrica que Prometheus efectivamente recolectó**. Por eso se distingue en cada fila qué se mide directamente, qué llega por un exporter y qué no se observa.

## 1. Tres capas de observación

Cada base se observa desde hasta tres lugares distintos. Así se puede responder *dónde* está una falla (ver [`decisiones_de_arquitectura.md`](decisiones_de_arquitectura.md#5-cómo-se-distingue-si-el-problema-está-en-la-api-o-en-la-base)):

| Capa | Pregunta que responde | Métrica | Mecanismo |
|---|---|---|---|
| **Red** | ¿El puerto publicado de la base acepta conexiones? | `probe_success{job="sonda-tcp"}` | blackbox exporter (`tcp_connect`) |
| **Aplicación** | ¿La API puede *usar* la base (conectar + autenticar + operación mínima)? ¿Cuánto tardan y cuántas fallan las rutas que la usan? | `fixture_dependencia_up`, `fixture_http_requests_total`, `fixture_http_request_duration_seconds` | endpoint propio `/metrics` de la API |
| **Motor** | ¿Qué está haciendo la base por dentro (operaciones, conexiones, memoria, licencias)? | `mongodb_*`, `redis_*`, `iris_*`, `http_requests_total`/`influxdb_iox_*` | exporter o métricas nativas |

## 2. Inventario

| Componente | Modelo de datos | Función en el Fixture | Puerto / endpoint | Mecanismo de monitoreo (job) | Métricas seleccionadas | Riesgo que se intenta observar | Limitaciones del monitoreo |
|---|---|---|---|---|---|---|---|
| **API integrada** (FastAPI, Hitos 10-12) | Integración (sin datos propios) | Punto único de acceso a las 6 bases | `127.0.0.1:8000/metrics` (Prometheus la lee por `host.docker.internal:8000`) | **Endpoint propio** (`fixture-api`), instrumentado en este hito; **sonda HTTP** a `/health/live` (`sonda-http`) | `fixture_http_requests_total{metodo,ruta,codigo,dependencia}`, `fixture_http_request_duration_seconds` (histograma), `fixture_http_requests_in_progress`, `fixture_dependencia_up`, `fixture_dependencia_chequeo_segundos`, `fixture_api_proceso_cpu_segundos_total`, `fixture_api_proceso_memoria_bytes`, `fixture_corte_rapido_*`, `fixture_api_info` | API caída; latencia alta; errores 5xx; saturación de CPU (en el Hito 12 la API fue el primer cuello de botella) | Un único proceso: no hay métricas por instancia. El histograma mide el tiempo **dentro** del proceso (no incluye red ni cola del sistema operativo). CPU y memoria se leen con psutil porque el colector estándar solo funciona en Linux |
| **MongoDB 7** (Hito 4) | Documental | Equipos y jugadores | `27017` | **Exporter** de Percona (`mongodb`, `mongodb-exporter:9216`) + sonda TCP + rutas de la API | `mongodb_up`, `mongodb_op_counters_total{type}`, `mongodb_connections{state}`, `mongodb_ss_*` (2.496 métricas disponibles) | Base caída, saturación de conexiones, cambio en el patrón de operaciones | `--collect-all` trae miles de series: en producción se filtrarían colectores. Una sola instancia: no hay métricas de réplica |
| **Neo4j** (Hito 5) | Grafo | Partidos, sedes, equipos y eventos (recorridos) | `7687` (Bolt) | **Sonda TCP** (`sonda-tcp`) + **ping de la API** (`fixture_dependencia_up{dependencia="Neo4j"}`) + latencia/errores de `/partidos/{codigo}/eventos` | `probe_success`, `fixture_dependencia_up`, P95 y 5xx de la ruta | Base caída o lenta para recorridos | **Sin métricas internas:** el endpoint Prometheus de Neo4j es una función de la edición Enterprise; el laboratorio usa Community. Se observa solo "desde afuera" (red + API) |
| **Cassandra** (Hito 6) | Columnar distribuido (wide-column) | Comentarios por partido y ventana de 10 min | `9042` (CQL) | **Sonda TCP** + **ping de la API** + latencia/errores de `/partidos/{codigo}/comentarios` | `probe_success`, `fixture_dependencia_up`, P95 y 5xx de la ruta | Base caída; aumento de latencia de lectura por partición caliente | **Sin métricas internas:** requiere agregar un agente JMX a la JVM de Cassandra (propuesta, no implementada). No se observan compactaciones, tombstones ni latencia por tabla |
| **Redis** (Hito 7) | Clave-valor con TTL | Sesiones de usuario | `6379` | **Exporter** `redis_exporter` (`redis`) + sonda TCP + rutas de la API | `redis_up`, `redis_memory_used_bytes`, `redis_memory_max_bytes`, `redis_connected_clients`, `redis_commands_processed_total` | Caída (se probó en la prueba controlada); memoria cerca de `maxmemory` con `noeviction` → rechazo de escrituras | No se instrumentó la tasa de expiración por TTL en un panel (la métrica existe: `redis_expired_keys_total`) |
| **InfluxDB 3 Core** (Hito 8) | Series temporales | Estadísticas de partido (10 s) y resúmenes de 15 min | `8181/metrics` | **Métricas nativas** (`influxdb`, con token de solo lectura en `.secretos/`) + sonda TCP + ruta `/estadisticas` | `http_requests_total`, `influxdb_iox_query_log_end2end_duration_seconds` (histograma), `influxdb3_parquet_cache_*` | Caída; consultas lentas; crecimiento del caché | Se usa el token de administrador generado en el laboratorio (no se creó uno exclusivo para monitoreo). No se versiona |
| **InterSystems IRIS** (Hito 9) | Objetos persistentes (multimodelo) | Detalle del partido (Partido, Árbitro, Eventos) | `1972` (Superserver, API) · `52773/api/monitor/metrics` | **Métricas nativas** (`iris`, usuario `_SYSTEM` con password en `.secretos/`) + sonda TCP + ruta `/detalle` | `iris_license_percent_used`, `iris_license_consumed`, `iris_glo_ref_per_sec`, `iris_process_count`, `iris_cpu_usage` | **Agotamiento de licencias** (Community admite 8 conexiones, medido en el Hito 12); caída del motor | El scraping usa el usuario de sistema del laboratorio; en producción se crearía un usuario con rol solo de monitoreo |
| **Host Docker** | — | Máquina donde corren los contenedores | `node-exporter:9100` | **Exporter** (`node-exporter`) | `node_cpu_seconds_total`, `node_memory_MemAvailable_bytes` | Saturación de CPU/memoria de la máquina | En Windows con Docker Desktop mide la **VM Linux de WSL2**, no Windows ni el proceso de la API |
| **Contenedores** (opcional) | — | CPU/memoria por contenedor | `cadvisor:8080` | **Exporter** cAdvisor, perfil `contenedores` | `container_cpu_usage_seconds_total` | Comparar consumo por base durante la carga | **No validado** en esta notebook (no se levantó el perfil). El panel queda vacío y el job aparece DOWN en `verificar_targets`: es esperado |
| **Prometheus** | — | Recolector y evaluador de alertas | `9090` | Endpoint propio (`prometheus`) | `up`, `scrape_duration_seconds` | Que el propio monitoreo deje de funcionar | No hay Alertmanager: las alertas se ven en `/alerts` y en Grafana, no se notifican |
| **Grafana** | — | Visualización | `3000` | — (consume Prometheus) | — | — | No se monitorea a sí mismo |

## 3. Qué se mide, qué llega por exporter y qué se infiere (RNF3)

| Tipo | Ejemplos | Comentario |
|---|---|---|
| **Medido directamente** por código del grupo | todas las `fixture_*` | Instrumentación de la API ([`app/middleware/metrics.py`](../../app/middleware/metrics.py), [`app/routes/metrics.py`](../../app/routes/metrics.py)). Lo que ve el usuario del Fixture |
| **Obtenido mediante exporter** | `mongodb_*`, `redis_*`, `node_*`, `probe_*` | Un proceso traductor consulta al motor y publica en formato Prometheus |
| **Nativo del producto** | `iris_*`, `http_requests_total` e `influxdb_iox_*` de InfluxDB | El motor ya expone `/metrics`; solo se configuró el acceso |
| **Inferido / propuesto** | causas de un aumento de latencia, capacidad para el tráfico real del Mundial, comportamiento con réplicas | No se mide: se razona a partir de lo medido y se marca como tal en [`limitaciones_y_evidencia.md`](limitaciones_y_evidencia.md) |

## 4. Relación entre cada job y el componente observado

| Job | Targets | Componente | Capa |
|---|---:|---|---|
| `prometheus` | 1 | Prometheus | monitoreo |
| `fixture-api` | 1 | API | aplicación |
| `mongodb` | 1 | MongoDB | infraestructura (motor) |
| `redis` | 1 | Redis | infraestructura (motor) |
| `iris` | 1 | InterSystems IRIS | infraestructura (motor) |
| `influxdb` | 1 | InfluxDB | infraestructura (motor) |
| `node-exporter` | 1 | Host Docker (VM de WSL2) | infraestructura |
| `cadvisor` | 1 | Contenedores (opcional) | infraestructura |
| `sonda-tcp` | 6 | Una por base (las 6) | red |
| `sonda-http` | 1 | API `/health/live` | red |

Cada target lleva las etiquetas `capa`, `componente`, `modelo` y `mecanismo`, así las consultas y los paneles pueden filtrar por cualquiera de ellas.

# Grafana · dashboard "Fixture 2030 · Monitoreo de la plataforma" (RF5, RF6, RF7, punto 5.3)

## Provisión (reproducible, sin pasos manuales)

| Archivo | Qué hace |
|---|---|
| `provisioning/datasources/prometheus.yml` | Crea el datasource **Prometheus Fixture 2030** (`uid: prometheus-fixture`, `http://prometheus:9090`, intervalo 15 s) |
| `provisioning/dashboards/dashboards.yml` | Carga todo JSON de `dashboards/` en la carpeta "Fixture 2030" |
| `dashboards/fixture2030.json` | El dashboard (32 paneles en 6 secciones). Se genera con `scripts/generar_dashboard.py`, así cada consulta queda versionada y revisable |

Grafana abre directamente en este dashboard. La lectura es **sin login** (rol Viewer anónimo) para la demo; para editar se entra con `admin` y la contraseña generada en `../.env`. Rango por defecto: últimos 30 min. Refresco: 10 s. La variable **"Base (rutas de la API)"** filtra las secciones 2 a 4 por una o varias bases.

Cada panel tiene título, unidad, leyenda y una descripción (ícono ⓘ) con la consulta, la ventana y cómo interpretarlo (RNF4).

## Qué muestra cada sección

| Sección | Paneles | Requisito 5.3 | Pregunta que responde |
|---|---|---|---|
| **1 · Estado de salud por base** | API (scraping); ¿la API puede usar cada base?; ¿el puerto de cada base acepta conexiones?; disponibilidad en el tiempo (API → base y targets); alertas activas | Vista de **disponibilidad**; panel de "estado de salud" por base | ¿Qué está caído y desde cuándo? ¿Es la base o la conexión? |
| **2 · Volumen y throughput** | Solicitudes/s por base (apiladas); throughput total; en curso; atendidas en el período | Vista de **volumen / throughput** | ¿Cuánto tráfico hay y cómo se reparte entre las bases? |
| **3 · Latencia** | P50/P95/P99 global con franja de umbral 250 ms; P95 por base; media por base; ping de la API a cada base | Vista de **latencia** + **umbral** | ¿Está lento? ¿Qué base lo explica? |
| **4 · Errores** | 5xx/s por base; respuestas por código; 503 inmediatos del corte rápido; % de 5xx (umbral 1 % / 5 %); 5xx en el período; circuito por base | Vista de **errores** + **umbral** | ¿Hay errores? ¿Se concentran en una base? |
| **5 · Comparación entre bases** | MongoDB ops/s; Redis comandos/s y clientes; IRIS globales/s y procesos; Redis memoria/maxmemory (umbral 85 %); IRIS licencias (umbral 75 %); conexiones por base; InfluxDB solicitudes y P95 de consultas; latencia de la sonda TCP; duración del scraping | **Comparación entre al menos dos componentes** | ¿Qué hace cada motor por dentro con la misma carga? |
| **6 · Saturación de recursos** | CPU del proceso de la API (umbral 80 %); CPU y memoria de la máquina Docker; CPU por contenedor (opcional) | Límites interpretados | ¿El cuello de botella está en la API o en las bases? |

Las **anotaciones naranjas** verticales las crea la prueba controlada (inicio, `docker stop`, `docker start`, fin): marcan en todos los paneles el momento exacto de la falla.

## Umbrales que se ven en el dashboard

| Panel | Verde | Amarillo | Rojo | Origen del umbral |
|---|---|---|---|---|
| Latencia P50/P95/P99 y P95 por base | < 250 ms | — | ≥ 250 ms | Alerta `FixtureLatenciaP95Alta` |
| % de 5xx | < 1 % | 1-5 % | ≥ 5 % | Alerta `FixtureErrores5xxAltos` |
| Redis memoria | < 70 % | 70-85 % | ≥ 85 % | Alerta `RedisMemoriaCercaDelLimite` |
| IRIS licencias | < 50 % | 50-75 % | ≥ 75 % | Alerta `IrisLicenciasCasiAgotadas` |
| CPU de la API | < 80 % | — | ≥ 80 % | Hito 12: 70-86 % en saturación |

La justificación de cada número está en [`../docs/alertas_y_umbral.md`](../docs/alertas_y_umbral.md).

## Cómo leerlo ante una señal desfavorable

1. **Sección 1:** si algo está en rojo, comparar las dos filas de cuadros. Si ambas dicen CAÍDA, la base está detenida. Si el puerto está OK pero la API dice CAÍDA, revisar `/health/dependencias`.
2. **Sección 3 "P95 por base":** ubicar qué motor sube.
3. **Sección 6 "CPU de la API":** si está cerca de 80 % y suben todas las bases a la vez, el límite es la API.
4. **Sección 4:** errores solo en una base → aislamiento funcionando; en todas → problema de la API.

## Capturas del dashboard operando

En [`../evidencia/dashboards/`](../evidencia/dashboards/): estado normal (01), Redis caído (02), errores y circuito abierto (03), alertas en Prometheus (04-06), recuperación (07), throughput (08), latencia con corte v1 (09), comparación entre bases (10), recursos (11), latencia y errores comparando corte v1 y v2 (12-13).

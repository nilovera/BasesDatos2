"""Genera grafana/dashboards/fixture2030.json (Hito 13). Uso: python scripts/generar_dashboard.py grafana/dashboards/fixture2030.json"""
import json
import sys

DS = {"type": "prometheus", "uid": "prometheus-fixture"}
NEG = 'ruta=~"/api/v1/.*", dependencia=~"$dependencia"'
paneles = []
pid = [0]
y = [0]


def nid():
    pid[0] += 1
    return pid[0]


def fila(titulo):
    paneles.append({"type": "row", "title": titulo, "id": nid(), "collapsed": False,
                    "gridPos": {"h": 1, "w": 24, "x": 0, "y": y[0]}, "panels": []})
    y[0] += 1


def t(expr, legend="", instant=False, ref="A", fmt=None):
    d = {"datasource": DS, "expr": expr, "legendFormat": legend, "refId": ref, "range": not instant,
         "instant": instant}
    if fmt:
        d["format"] = fmt
    return d


def umbrales(*pasos):
    base = [{"color": pasos[0], "value": None}]
    for i in range(1, len(pasos), 2):
        base.append({"color": pasos[i + 1], "value": pasos[i]})
    return {"mode": "absolute", "steps": base}


def panel(tipo, titulo, desc, targets, x, w, h, unidad=None, umb=None, extra=None, custom=None,
          opciones=None, mappings=None, overrides=None, minimo=None, maximo=None):
    p = {"type": tipo, "title": titulo, "description": desc, "id": nid(), "datasource": DS,
         "gridPos": {"h": h, "w": w, "x": x, "y": y[0]}, "targets": targets,
         "fieldConfig": {"defaults": {}, "overrides": overrides or []}, "options": opciones or {}}
    d = p["fieldConfig"]["defaults"]
    if unidad:
        d["unit"] = unidad
    if umb:
        d["thresholds"] = umb
    if mappings:
        d["mappings"] = mappings
    if custom:
        d["custom"] = custom
    if minimo is not None:
        d["min"] = minimo
    if maximo is not None:
        d["max"] = maximo
    if extra:
        p.update(extra)
    paneles.append(p)
    return p


UPDOWN = [{"type": "value", "options": {"0": {"text": "CAÍDA", "color": "red", "index": 0},
                                        "1": {"text": "OK", "color": "green", "index": 1}}}]
LEYENDA = {"displayMode": "table", "placement": "right", "calcs": ["lastNotNull", "max"], "showLegend": True}
LEYENDA_ABAJO = {"displayMode": "list", "placement": "bottom", "showLegend": True, "calcs": []}
TS_OPC = {"legend": LEYENDA, "tooltip": {"mode": "multi", "sort": "desc"}}
TS_OPC_B = {"legend": LEYENDA_ABAJO, "tooltip": {"mode": "multi", "sort": "desc"}}


def linea(fill=10, umbral_linea=False, stack=False):
    c = {"drawStyle": "line", "lineWidth": 2, "fillOpacity": fill, "showPoints": "never",
         "spanNulls": False, "axisSoftMin": 0}
    if umbral_linea:
        c["thresholdsStyle"] = {"mode": "line+area"}
    if stack:
        c["stacking"] = {"mode": "normal", "group": "A"}
    return c


# =========================================================== 1. disponibilidad
fila("1 · Estado de salud por base (disponibilidad)")
panel("stat", "API (scraping)", "up{job=\"fixture-api\"}: 1 si Prometheus pudo leer /metrics de la API en el último "
      "scraping (cada 15 s). Medido directamente.",
      [t('up{job="fixture-api"}', "API", instant=True)], 0, 3, 5, mappings=UPDOWN,
      umb=umbrales("red", 1, "green"),
      opciones={"colorMode": "background", "graphMode": "none", "textMode": "value_and_name",
                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
panel("stat", "¿La API puede usar cada base? (ping del adaptador)",
      "fixture_dependencia_up: 1 si el ping liviano del adaptador (Hito 11: conexión + autenticación + "
      "operación mínima) respondió. Lo calcula la API con caché de 15 s. Es la disponibilidad que importa para el "
      "Fixture: puerto abierto no alcanza si la autenticación falla.",
      [t('max by (dependencia) (fixture_dependencia_up)', "{{dependencia}}", instant=True)], 3, 11, 5,
      mappings=UPDOWN, umb=umbrales("red", 1, "green"),
      opciones={"colorMode": "background", "graphMode": "none", "textMode": "value_and_name",
                "orientation": "vertical", "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
panel("stat", "¿El puerto de cada base acepta conexiones? (sonda TCP)",
      "probe_success del blackbox exporter, módulo tcp_connect contra el puerto publicado de cada base. Mide la capa "
      "de red/infraestructura, sin autenticar. Única señal directa para Neo4j y Cassandra (sin exporter).",
      [t('max by (componente) (probe_success{job="sonda-tcp"})', "{{componente}}", instant=True)], 14, 10, 5,
      mappings=UPDOWN, umb=umbrales("red", 1, "green"),
      opciones={"colorMode": "background", "graphMode": "none", "textMode": "value_and_name",
                "orientation": "vertical", "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
y[0] += 5
panel("state-timeline", "Disponibilidad en el tiempo: API → base (ping del adaptador)",
      "Verde = la API pudo usar la base; rojo = no. Permite ver cuándo empezó y terminó una falla y "
      "cuánto tardó la recuperación (resolución: scraping de 15 s + caché de 15 s de la API).",
      [t('max by (dependencia) (fixture_dependencia_up)', "{{dependencia}}")], 0, 12, 7,
      mappings=UPDOWN, umb=umbrales("red", 1, "green"),
      opciones={"showValue": "never", "mergeValues": True, "rowHeight": 0.85, "legend": {"showLegend": False}},
      custom={"fillOpacity": 80, "lineWidth": 0})
panel("state-timeline", "Disponibilidad en el tiempo: targets de Prometheus",
      "up de cada job: 1 si Prometheus pudo leer sus métricas. Si un exporter está DOWN pero la sonda TCP de la base "
      "está OK, se perdió visibilidad, no la base. cadvisor (opcional) solo aparece si se levantó con el perfil 'contenedores'.",
      [t('max by (job) (up unless on(job) (up{job="cadvisor"} == 0))', "{{job}}")], 12, 12, 7,
      mappings=UPDOWN, umb=umbrales("red", 1, "green"),
      opciones={"showValue": "never", "mergeValues": True, "rowHeight": 0.85, "legend": {"showLegend": False}},
      custom={"fillOpacity": 80, "lineWidth": 0})
y[0] += 7
panel("table", "Alertas activas (reglas de Prometheus)",
      "ALERTS{alertstate=\"firing\"}: alertas definidas en prometheus/reglas-o-alertas.yml que están disparadas ahora. "
      "Vacío = sin alertas. El detalle (impacto y acción) está en http://localhost:9090/alerts.",
      [t('max by (alertname, severidad, atiende, dependencia, componente) (ALERTS{alertstate="firing"})', "",
         instant=True, fmt="table")], 0, 24, 5,
      extra={"transformations": [{"id": "organize", "options": {"excludeByName": {"Time": True, "Value": True}}}]},
      opciones={"showHeader": True, "footer": {"show": False}})
y[0] += 5

# =========================================================== 2. tráfico
fila("2 · Volumen y throughput de la API (capa de aplicación)")
panel("timeseries", "Solicitudes por segundo, por base",
      "sum by (dependencia) (rate(fixture_http_requests_total{ruta=~\"/api/v1/.*\"}[1m])). Solo rutas de negocio "
      "(/health y /metrics excluidas). Unidad: solicitudes/s, ventana de 1 min. Apilado = throughput total.",
      [t(f'sum by (dependencia) (rate(fixture_http_requests_total{{{NEG}}}[1m]))', "{{dependencia}}")],
      0, 16, 8, unidad="reqps", custom=linea(25, stack=True), opciones=TS_OPC)
panel("stat", "Throughput total",
      "Suma de solicitudes/s de negocio (ventana 1 min). Referencia Hito 12: ~330-360 req/s con 80 usuarios.",
      [t(f'sum(rate(fixture_http_requests_total{{{NEG}}}[1m]))', "req/s")], 16, 4, 4, unidad="reqps",
      opciones={"colorMode": "value", "graphMode": "area",
                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
panel("stat", "Solicitudes en curso",
      "fixture_http_requests_in_progress: solicitudes que la API está procesando en el instante del scraping.",
      [t('fixture_http_requests_in_progress', "en curso")], 20, 4, 4, unidad="short",
      opciones={"colorMode": "value", "graphMode": "area",
                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
panel("stat", "Solicitudes atendidas en el período",
      "increase() de solicitudes de negocio en el rango de tiempo elegido arriba a la derecha.",
      [t(f'sum(increase(fixture_http_requests_total{{{NEG}}}[$__range]))', "total", instant=True)], 16, 8, 4,
      unidad="short", opciones={"colorMode": "value", "graphMode": "none",
                                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
paneles[-1]["gridPos"]["y"] += 4
y[0] += 8

# =========================================================== 3. latencia
fila("3 · Latencia / tiempo de respuesta (umbral de alerta: P95 > 250 ms)")
panel("timeseries", "Latencia global de la API: P50 / P95 / P99",
      "histogram_quantile sobre fixture_http_request_duration_seconds (tiempo dentro del proceso de la API, el mismo "
      "de X-Process-Time-Ms). Ventana 1 min. La franja roja marca el umbral de 250 ms de la alerta FixtureLatenciaP95Alta "
      "(evaluada con ventana de 5 min).",
      [t(f'histogram_quantile(0.50, sum by (le) (rate(fixture_http_request_duration_seconds_bucket{{{NEG}}}[1m])))', "P50", ref="A"),
       t(f'histogram_quantile(0.95, sum by (le) (rate(fixture_http_request_duration_seconds_bucket{{{NEG}}}[1m])))', "P95", ref="B"),
       t(f'histogram_quantile(0.99, sum by (le) (rate(fixture_http_request_duration_seconds_bucket{{{NEG}}}[1m])))', "P99", ref="C")],
      0, 12, 8, unidad="s", umb=umbrales("green", 0.25, "red"), custom=linea(5, umbral_linea=True), opciones=TS_OPC_B)
panel("timeseries", "Latencia P95 por base",
      "P95 de cada ruta agrupado por la base que la atiende (etiqueta dependencia). Ventana 1 min. Permite ubicar qué "
      "motor explica una suba de la latencia global.",
      [t(f'histogram_quantile(0.95, sum by (le, dependencia) (rate(fixture_http_request_duration_seconds_bucket{{{NEG}}}[1m])))',
         "{{dependencia}}")],
      12, 12, 8, unidad="s", umb=umbrales("green", 0.25, "red"), custom=linea(0, umbral_linea=True), opciones=TS_OPC)
y[0] += 8
panel("timeseries", "Latencia media por base",
      "rate(sum) / rate(count) del histograma, por base. Ventana 1 min. Complementa al P95: la media se mueve con "
      "toda la población, el P95 con la cola lenta.",
      [t(f'sum by (dependencia) (rate(fixture_http_request_duration_seconds_sum{{{NEG}}}[1m])) / '
         f'sum by (dependencia) (rate(fixture_http_request_duration_seconds_count{{{NEG}}}[1m]))', "{{dependencia}}")],
      0, 12, 7, unidad="s", custom=linea(0), opciones=TS_OPC)
panel("timeseries", "Tiempo del ping de la API a cada base",
      "fixture_dependencia_chequeo_segundos: duración del último ping del adaptador (sin carga de negocio). Compara "
      "las seis bases en igualdad de condiciones y separa 'la base está lenta' de 'la consulta es pesada'.",
      [t('max by (dependencia) (fixture_dependencia_chequeo_segundos)', "{{dependencia}}")],
      12, 12, 7, unidad="s", custom=linea(0), opciones=TS_OPC)
y[0] += 7

# =========================================================== 4. errores
fila("4 · Errores y respuestas no exitosas (umbral de alerta: 5xx > 5 %)")
panel("timeseries", "Errores 5xx por segundo, por base",
      "rate de respuestas 5xx de rutas de negocio (ventana 1 min). 503 = la base de esa ruta no está disponible "
      "(la API aísla el error por adaptador y sigue atendiendo las demás).",
      [t(f'sum by (dependencia) (rate(fixture_http_requests_total{{{NEG}, codigo=~"5.."}}[1m]))', "{{dependencia}}")],
      0, 10, 8, unidad="reqps", custom=linea(30, stack=True), opciones=TS_OPC_B,
      overrides=[])
panel("timeseries", "Respuestas por código HTTP",
      "Todas las respuestas de negocio por código (ventana 1 min). 2xx = OK; 404 = clave inexistente (no es falla); "
      "422 = parámetro inválido; 5xx = falla del lado servidor.",
      [t(f'sum by (codigo) (rate(fixture_http_requests_total{{{NEG}}}[1m]))', "{{codigo}}")],
      10, 8, 8, unidad="reqps", custom=linea(10), opciones=TS_OPC_B)
panel("timeseries", "Corte rápido: 503 inmediatos por base",
      "rate(fixture_corte_rapido_rechazos_total[1m]): solicitudes que la API rechazó al instante porque el circuito de "
      "esa base estaba abierto (CORTE_RAPIDO_SEGUNDOS > 0). Mejora transversal del Hito 13: evita que una base caída "
      "ocupe hilos de la API ~2 s por solicitud.",
      [t('sum by (dependencia) (rate(fixture_corte_rapido_rechazos_total[1m]))', "{{dependencia}}")],
      18, 6, 8, unidad="reqps", custom=linea(20), opciones=TS_OPC_B)
y[0] += 8
panel("stat", "% de solicitudes con 5xx (2 min)",
      "Proporción de respuestas 5xx sobre el total en los últimos 2 min (misma ventana que la alerta). Amarillo desde 1 %, rojo desde 5 % "
      "(umbral de la alerta FixtureErrores5xxAltos). Hito 12: 0 %.",
      [t(f'(sum(rate(fixture_http_requests_total{{{NEG}, codigo=~"5.."}}[2m])) or vector(0)) / '
         f'sum(rate(fixture_http_requests_total{{{NEG}}}[2m]))', "5xx")],
      0, 6, 6, unidad="percentunit", umb=umbrales("green", 0.01, "yellow", 0.05, "red"),
      opciones={"colorMode": "background", "graphMode": "area",
                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
STAT = {"colorMode": "value", "graphMode": "none", "textMode": "value_and_name",
        "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}}
panel("stat", "Respuestas 5xx en el período, por base",
      "increase() de respuestas 5xx de negocio en el rango elegido, por base que atiende la ruta.",
      [t(f'sum by (dependencia) (increase(fixture_http_requests_total{{{NEG}, codigo=~"5.."}}[$__range]))', "{{dependencia}}",
         instant=True)], 6, 9, 6, unidad="short", umb=umbrales("green", 1, "red"), opciones=STAT)
panel("stat", "Circuito de corte rápido por base",
      "fixture_corte_rapido_abierto: ABIERTO = la API responde 503 al instante sin intentar conectarse a esa base. "
      "Vacío si CORTE_RAPIDO_SEGUNDOS = 0.",
      [t('max by (dependencia) (fixture_corte_rapido_abierto)', "{{dependencia}}", instant=True)], 15, 9, 6,
      mappings=[{"type": "value", "options": {"0": {"text": "cerrado", "color": "green", "index": 0},
                                              "1": {"text": "ABIERTO", "color": "orange", "index": 1}}}],
      umb=umbrales("green", 1, "orange"), opciones={**STAT, "colorMode": "background"})
y[0] += 6

# =========================================================== 5. comparación de bases
fila("5 · Comparación entre bases (métricas internas de cada motor)")
panel("timeseries", "MongoDB: operaciones por segundo",
      "mongodb_op_counters_total (exporter de Percona, modo compatible), rate 1 min por tipo de operación. "
      "Equipos y jugadores (Hito 4): se espera mayoría de 'query'.",
      [t('sum by (type) (rate(mongodb_op_counters_total[1m]))', "{{type}}")], 0, 8, 7, unidad="ops",
      custom=linea(10), opciones=TS_OPC_B)
panel("timeseries", "Redis: comandos por segundo y clientes",
      "rate(redis_commands_processed_total[1m]) (eje izq.) y redis_connected_clients (eje der.). Sesiones (Hito 7).",
      [t('sum(rate(redis_commands_processed_total[1m]))', "comandos/s", ref="A"),
       t('sum(redis_connected_clients)', "clientes conectados", ref="B")], 8, 8, 7, unidad="ops",
      custom=linea(10), opciones=TS_OPC_B,
      overrides=[{"matcher": {"id": "byName", "options": "clientes conectados"},
                  "properties": [{"id": "unit", "value": "short"}, {"id": "custom.axisPlacement", "value": "right"}]}])
panel("timeseries", "IRIS: referencias a globales/s y procesos",
      "iris_glo_ref_per_sec (accesos a globales, el almacenamiento de los objetos del Hito 9) y iris_process_count. "
      "Métricas nativas de /api/monitor/metrics.",
      [t('sum(iris_glo_ref_per_sec)', "globales/s", ref="A"),
       t('sum(iris_process_count)', "procesos", ref="B")], 16, 8, 7, unidad="short",
      custom=linea(10), opciones=TS_OPC_B,
      overrides=[{"matcher": {"id": "byName", "options": "procesos"},
                  "properties": [{"id": "custom.axisPlacement", "value": "right"}]}])
y[0] += 7
panel("gauge", "Redis: memoria usada / maxmemory",
      "redis_memory_used_bytes / redis_memory_max_bytes. Con noeviction (Hito 7) al 100 % se rechazan escrituras "
      "de sesiones. Amarillo 70 %, rojo 85 % (umbral de RedisMemoriaCercaDelLimite).",
      [t('sum(redis_memory_used_bytes) / sum(redis_memory_max_bytes > 0)', "Redis", instant=True)], 0, 6, 7,
      unidad="percentunit", umb=umbrales("green", 0.7, "yellow", 0.85, "red"), minimo=0, maximo=1,
      opciones={"showThresholdMarkers": True, "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
panel("gauge", "IRIS: % de licencias en uso",
      "iris_license_percent_used. IRIS Community admite 8 conexiones simultáneas (medido en el Hito 12): por eso el "
      "pool de la API quedó en 5. Rojo desde 75 % (umbral de IrisLicenciasCasiAgotadas).",
      [t('max(iris_license_percent_used)', "IRIS", instant=True)], 6, 6, 7,
      unidad="percent", umb=umbrales("green", 50, "yellow", 75, "red"), minimo=0, maximo=100,
      opciones={"showThresholdMarkers": True, "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}})
panel("timeseries", "Conexiones abiertas por base (según cada motor)",
      "MongoDB: mongodb_connections{state=\"current\"}; Redis: redis_connected_clients; IRIS: iris_license_consumed "
      "(licencias consumidas). Cada motor cuenta distinto: comparar tendencias, no valores absolutos.",
      [t('sum(mongodb_connections{state="current"})', "MongoDB", ref="A"),
       t('sum(redis_connected_clients)', "Redis", ref="B"),
       t('sum(iris_license_consumed)', "IRIS (licencias)", ref="C")], 12, 12, 7, unidad="short",
      custom=linea(0), opciones=TS_OPC_B)
y[0] += 7
panel("timeseries", "InfluxDB 3: solicitudes HTTP/s y P95 de consultas",
      "Métricas nativas de /metrics de InfluxDB 3 Core: rate(http_requests_total[1m]) (eje izq.) y P95 de "
      "influxdb_iox_query_log_end2end_duration_seconds (eje der.), tiempo de punta a punta de cada consulta SQL. "
      "Estadísticas temporales (Hito 8).",
      [t('sum(rate(http_requests_total{job="influxdb"}[1m]))', "solicitudes HTTP/s", ref="A"),
       t('histogram_quantile(0.95, sum by (le) (rate(influxdb_iox_query_log_end2end_duration_seconds_bucket{job="influxdb"}[1m])))',
         "P95 consulta", ref="B")], 0, 8, 7, unidad="reqps", custom=linea(10), opciones=TS_OPC_B,
      overrides=[{"matcher": {"id": "byName", "options": "P95 consulta"},
                  "properties": [{"id": "unit", "value": "s"}, {"id": "custom.axisPlacement", "value": "right"}]}])
panel("timeseries", "Latencia de la sonda TCP por base",
      "probe_duration_seconds del blackbox exporter: tiempo en abrir la conexión TCP al puerto de cada base "
      "(incluye el reenvío de puertos de Docker Desktop).",
      [t('max by (componente) (probe_duration_seconds{job="sonda-tcp"})', "{{componente}}")], 8, 8, 7,
      unidad="s", custom=linea(0), opciones=TS_OPC)
panel("timeseries", "Duración del scraping por target",
      "scrape_duration_seconds: cuánto tarda Prometheus en leer cada target. Un aumento brusco en 'fixture-api' "
      "suele indicar una base lenta en el diagnóstico de dependencias.",
      [t('max by (job) (scrape_duration_seconds)', "{{job}}")], 16, 8, 7, unidad="s",
      custom=linea(0), opciones=TS_OPC)
y[0] += 7

# =========================================================== 6. recursos
fila("6 · Saturación de recursos (¿el límite está en la API o en la base?)")
panel("timeseries", "CPU del proceso de la API",
      "rate(fixture_api_proceso_cpu_segundos_total[1m]) × 100 = % de UN núcleo (psutil). Hito 12: 70-86 % en "
      "sostenimiento con 40 usuarios: la API (un solo proceso uvicorn) es el primer cuello de botella.",
      [t('rate(fixture_api_proceso_cpu_segundos_total[1m]) * 100', "API (% de 1 núcleo)")], 0, 8, 7,
      unidad="percent", umb=umbrales("green", 80, "red"), custom=linea(15, umbral_linea=True), opciones=TS_OPC_B,
      minimo=0)
panel("timeseries", "CPU y memoria de la máquina Docker",
      "node-exporter: CPU usada (100 − idle) y memoria usada. En Windows con Docker Desktop corresponde a la VM "
      "Linux donde corren las seis bases, no a Windows.",
      [t('100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[1m])))', "CPU %", ref="A"),
       t('100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)', "Memoria %", ref="B")],
      8, 8, 7, unidad="percent", custom=linea(10), opciones=TS_OPC_B, minimo=0, maximo=100)
panel("timeseries", "CPU por contenedor (cAdvisor, opcional)",
      "sum by (name) (rate(container_cpu_usage_seconds_total[1m])) × 100. Solo con el perfil 'contenedores'; si "
      "está vacío, cAdvisor no está levantado (ver README).",
      [t('sum by (name) (rate(container_cpu_usage_seconds_total{name=~"fixture2030-.*"}[1m])) * 100', "{{name}}")],
      16, 8, 7, unidad="percent", custom=linea(0), opciones=TS_OPC_B, minimo=0)
y[0] += 7

dashboard = {
    "uid": "fixture2030-monitoreo",
    "title": "Fixture 2030 · Monitoreo de la plataforma",
    "description": "Hito 13 - Ingeniería de Datos II - Grupo 10. Disponibilidad, latencia, throughput, errores y "
                   "comparación de las seis bases NoSQL del Fixture 2030.",
    "tags": ["fixture2030", "hito13"],
    "timezone": "browser",
    "editable": True,
    "graphTooltip": 1,
    "refresh": "10s",
    "time": {"from": "now-30m", "to": "now"},
    "timepicker": {"refresh_intervals": ["5s", "10s", "30s", "1m", "5m"]},
    "schemaVersion": 39,
    "version": 1,
    "annotations": {"list": [
        {"builtIn": 1, "datasource": {"type": "grafana", "uid": "-- Grafana --"}, "enable": True, "hide": True,
         "iconColor": "rgba(0, 211, 255, 1)", "name": "Annotations & Alerts", "type": "dashboard"},
        {"datasource": {"type": "grafana", "uid": "-- Grafana --"}, "enable": True, "iconColor": "orange",
         "name": "Prueba controlada", "target": {"type": "tags", "tags": ["prueba-controlada"], "limit": 100,
                                                 "matchAny": True}},
    ]},
    "templating": {"list": [{
        "name": "dependencia", "label": "Base (rutas de la API)", "type": "query", "datasource": DS,
        "query": {"query": "label_values(fixture_http_requests_total, dependencia)", "refId": "dep"},
        "definition": "label_values(fixture_http_requests_total, dependencia)",
        "refresh": 2, "multi": True, "includeAll": True, "allValue": ".*",
        "current": {"selected": True, "text": ["All"], "value": ["$__all"]}, "sort": 1}]},
    "panels": paneles,
}
json.dump(dashboard, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(len(paneles), "paneles")

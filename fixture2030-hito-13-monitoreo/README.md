# Hito 13 — Monitoreo con Prometheus y Grafana, análisis transversal y defensa final del Fixture 2030

Ingeniería de Datos II · Grupo 10 · Rama `monitoreo` (sale de `carga-optimizacion`, Hito 12)

Capa de observabilidad sobre la plataforma construida en los hitos 4 a 12. Incluye:

- la API instrumentada con `/metrics`;
- Prometheus recolectando **14 targets** (9 jobs, más cAdvisor opcional): la API, 4 motores con exporter o métricas nativas, el host Docker y sondas de red a las 6 bases;
- un dashboard de Grafana provisionado (32 paneles en 6 secciones) y 8 alertas con impacto y acción;
- tres pruebas controladas de falla con carga, una mejora transversal medida (corte rápido) y el material de la defensa ante la FIFA.

## Resultado en una tabla

Prueba controlada: tráfico constante de 20 usuarios con la mezcla del Hito 12 (6 bases), **Redis detenido 120 s** con `docker stop` y vuelto a iniciar. Mismas condiciones en las tres corridas.

| Medido durante la falla de Redis | Sin corte rápido | Corte rápido v1 | **Corte rápido v2 (adoptado)** |
|---|---:|---:|---:|
| Throughput total de la API | 47 req/s (−65 %) | 115 req/s | **138 req/s** (igual que sin falla) |
| P95 máximo de las rutas de Redis | 2.812 ms | 1.592 ms | **4,9 ms** |
| Errores 5xx en las **otras 5 bases** | 0 | 0 | 0 |
| Datos de las 6 bases idénticos antes y después (15 claves c/u) | sí | sí | sí |
| Detección: puerto cerrado / API sin la base | 14 s / 29 s | 4 s / 14 s | 15 s / 30 s |
| Alertas disparadas y resueltas solas | 3 | 3 | 3 |

**Hallazgo y decisión.** El monitoreo mostró que, aunque la caída de una base no producía errores en las demás, sí las **frenaba**. En Windows, cada intento de conexión a Redis caído tardaba ~2,4 s en fallar y ocupaba la API durante ese tiempo. Se agregó un **corte rápido por base** ([`app/services/corte_rapido.py`](../app/services/corte_rapido.py), `CORTE_RAPIDO_SEGUNDOS=10`) y se volvió a medir. Detalle en [`docs/decisiones_de_arquitectura.md` §6](docs/decisiones_de_arquitectura.md#6-mejora-transversal-corte-rápido-por-base-rf12) y [`evidencia/comparacion_corte_rapido.md`](evidencia/comparacion_corte_rapido.md).

**Incidente real detectado.** Al iniciar el hito, IRIS arrancó sin su carpeta de datos (la distro WSL que la aloja estaba apagada). El monitoreo lo mostró como "puerto abierto pero la API no puede usarlo". Ver [`docs/limitaciones_y_evidencia.md` §4](docs/limitaciones_y_evidencia.md#4-anomalías-e-incidentes-observados).

## 1. Estructura

```text
fixture2030-hito-13-monitoreo/
├── README.md                          este archivo
├── docker-compose.yml                 Prometheus, Grafana, node-exporter, blackbox, exporters de MongoDB y Redis, cAdvisor (opcional)
├── prometheus.yml                     scraping cada 15 s, 9 jobs, etiquetas capa/componente/modelo/mecanismo
├── .env.example                       variables del stack (el .env real se genera y no se versiona)
├── .gitignore                         .env, .secretos/
├── requirements.txt                   prometheus_client, psutil, matplotlib (en el .venv de la API)
├── prometheus/
│   ├── reglas-o-alertas.yml           5 reglas de registro + 8 alertas
│   └── pruebas-reglas.yml             pruebas unitarias de las alertas (promtool)
├── blackbox/blackbox.yml              módulos tcp_connect y http_2xx
├── grafana/
│   ├── provisioning/                  datasource y proveedor de dashboards
│   ├── dashboards/fixture2030.json    dashboard "Fixture 2030 · Monitoreo de la plataforma"
│   └── README.md                      qué muestra cada sección y cómo leerla
├── scripts/
│   ├── iniciar_monitoreo.ps1          despierta WSL, inicia bases, secretos, API con /metrics, stack
│   ├── verificar_targets.ps1/.py      estado de cada target + disponibilidad en 3 capas -> evidencia
│   ├── ejecutar_prueba_controlada.ps1/.py  integridad + carga + falla + recuperación -> evidencia
│   ├── verificar_datos.py             huellas de las respuestas vs. catálogo del Hito 12
│   ├── comparar_pruebas.py            tabla y gráfico antes/después del corte rápido
│   ├── limpiar_entorno.ps1            baja el stack sin tocar las bases
│   ├── preparar_secretos.py           genera .env y .secretos/ desde el .env de la API
│   ├── generar_dashboard.py           genera el JSON del dashboard
│   └── comun_monitoreo.py             utilidades
├── docs/
│   ├── inventario_de_componentes.md   componente, modelo, función, puerto, mecanismo, métricas, riesgo, límites
│   ├── metricas_y_consultas.md        métricas de aplicación e infraestructura, 6 consultas PromQL explicadas
│   ├── alertas_y_umbral.md            8 alertas: condición, duración, severidad, impacto, acción, justificación
│   ├── decisiones_de_arquitectura.md  por qué cada base, distribución, CAP, API vs. base, mejora transversal
│   ├── limitaciones_y_evidencia.md    medido / diseño / propuesta / no medido, incidentes, plan B
│   └── defensa_final.md               respuesta a la pregunta central y a las preguntas de la FIFA
├── evidencia/                         ver evidencia/README.md
└── defensa/
    ├── presentacion.html              8 diapositivas, autocontenida (abre sin internet)
    ├── guion_de_20_minutos.md         tiempos, reparto y mensajes
    └── demo.md                        comandos de la demostración en vivo
```

Cambios en la API (fuera de esta carpeta): [`app/middleware/metrics.py`](../app/middleware/metrics.py), [`app/routes/metrics.py`](../app/routes/metrics.py), [`app/services/corte_rapido.py`](../app/services/corte_rapido.py), `app/main.py`, `app/config/settings.py` (`corte_rapido_segundos`, por defecto 0), `.env.example`, `requirements.txt` (`prometheus_client`, `psutil`) y `tests/unit/test_metrics_middleware.py`, `tests/unit/test_corte_rapido.py`.

## 2. Requisitos

- Windows 10/11 con PowerShell 5.1+ y Docker Desktop (WSL2).
- Las seis bases del Fixture creadas con sus datos: con sus compose de los hitos 4 a 9 o con [`../entorno-local/`](../entorno-local/README.md). Los nombres de contenedor deben ser `fixture2030-<base>`.
- La API de esta rama con su `.venv` y su `.env` completo (no se versiona).
- Puertos libres: 9090 (Prometheus), 3000 (Grafana), 9100, 9115, 9121 y 9216 (exporters).

## 3. Cómo iniciar el entorno

Desde la **carpeta raíz de la API**:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\iniciar_monitoreo.ps1
```

El script:

1. Verifica Docker.
2. Despierta la distro WSL donde están los datos de los hitos 6 a 9.
3. Inicia o reinicia las bases detenidas o `unhealthy` (no crea ni borra nada).
4. Instala `requirements.txt`.
5. Genera `.env` y `.secretos/` sin mostrar valores.
6. Reinicia la API con `IRIS_POOL_SIZE=5` y `CORTE_RAPIDO_SEGUNDOS=10`, y comprueba `/metrics`.
7. Levanta el stack (`docker compose up -d`) y espera a Prometheus y Grafana.

Opciones: `-Contenedores` (agrega cAdvisor), `-CorteRapido 0` (sin la mejora), `-PoolIris 0`, `-SinReiniciarApi`, `-DistroWsl ""`.

## 4. Cómo acceder

| Servicio | URL | Acceso |
|---|---|---|
| Grafana | http://localhost:3000 | Lectura sin login (abre en el dashboard del Fixture). Para editar: usuario `admin`, contraseña en `fixture2030-hito-13-monitoreo/.env` |
| Prometheus | http://localhost:9090 | `Status > Targets`, `Alerts`, `Graph` |
| Métricas de la API | http://127.0.0.1:8000/metrics | — |
| Swagger | http://127.0.0.1:8000/docs | — |

## 5. Datos de laboratorio

Se usan los datos de los hitos 4 a 9 y los datos sintéticos del Hito 12. Las sesiones `SES-H12-*` de Redis vencen a las 4 h: los scripts las recrean idénticas (misma semilla) antes de cada prueba. Para comprobar que los datos están intactos:

```powershell
.\.venv\Scripts\python.exe .\fixture2030-hito-13-monitoreo\scripts\verificar_datos.py --momento control
```

## 6. Validar un target UP e investigar uno DOWN

**Validar:**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\verificar_targets.ps1
```

Muestra, por target, job, componente, capa, mecanismo, estado y último error, más la disponibilidad de las bases en tres capas. Guarda `evidencia/prometheus_targets.md`. Código de salida 0 si los 9 jobs esperados están UP (cAdvisor es opcional). También se puede ver en `http://localhost:9090/targets` o con la consulta `up`.

**Investigar uno DOWN:**

| Paso | Qué mirar | Interpretación |
|---|---|---|
| 1 | Columna ERROR de `verificar_targets` o `/targets` | `connection refused` / `no such host`: el exporter no está corriendo → `docker compose ps` en esta carpeta. `EOF` / `context deadline exceeded`: el destino no responde a tiempo |
| 2 | Sonda TCP de esa base (`probe_success{componente="X"}`) | 0 → la base está caída o su puerto no está publicado: `docker ps -a --filter name=fixture2030`, `docker logs fixture2030-x` |
| 3 | `fixture_dependencia_up{dependencia="X"}` y `GET /health/dependencias?refrescar=true` | Puerto en 1 pero API en 0 → credenciales, namespace o motor que no terminó de arrancar (clasificación del Hito 11) |
| 4 | `fixture-api` DOWN | La API no corre o no expone `/metrics`: `scripts\reiniciar_api.ps1`; si persiste, que la API escuche en `0.0.0.0` |
| 5 | `iris` o `influxdb` DOWN con `401` | Contraseña o token desactualizados: volver a ejecutar `scripts/preparar_secretos.py` y `docker compose restart prometheus` |
| 6 | Caso real | IRIS `unhealthy` con `/durable/mgr: No such file or directory` → encender la distro (`wsl -d Ubuntu`) y `docker restart fixture2030-iris` |

## 7. Repetir la demostración

```powershell
# Prueba completa (≈ 7 min): integridad antes -> 60 s normal -> Redis detenido 120 s -> 90 s recuperación -> integridad después
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\ejecutar_prueba_controlada.ps1

# Otra base, o solo carga sin falla
... -Producto mongodb
... -Producto ninguno -Usuarios 40 -Normal 180

# Comparar las corridas guardadas
.\.venv\Scripts\python.exe .\fixture2030-hito-13-monitoreo\scripts\comparar_pruebas.py
```

Cada corrida deja `evidencia/prueba_de_falla_<base>_corte<N>_<fecha>/` con línea de tiempo, resumen, series de Prometheus, estado de salud y un gráfico. Para verla en vivo, abrir Grafana con el rango *Last 15 minutes*. La versión corta para la defensa está en [`defensa/demo.md`](defensa/demo.md).

**Probar las alertas sin levantar nada** (pruebas unitarias de promtool):

```powershell
docker run --rm -v "${PWD}\fixture2030-hito-13-monitoreo\prometheus:/r" --entrypoint promtool prom/prometheus:v3.5.0 test rules /r/pruebas-reglas.yml
```

## 8. Limpieza

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\limpiar_entorno.ps1
```

Vuelve a iniciar cualquier base que haya quedado detenida y baja el stack de monitoreo. **Nunca** borra volúmenes de las bases. `-BorrarHistorial` borra solo los volúmenes de Prometheus y Grafana de este proyecto; `-DetenerApi` detiene también la API.

## 9. Diferencias con el compose de la clase

| Aspecto | Clase 14 | Hito 13 | Motivo |
|---|---|---|---|
| Persistencia | `${HOME}/docker/data/...` | volúmenes con nombre | En PowerShell `HOME` no siempre es una variable de entorno |
| Versiones | `latest` | fijas (Prometheus 3.5.0, Grafana 11.6.0, …) | Reproducibilidad |
| Contraseña de Grafana | en el compose | `.env` generado al azar + lectura anónima | RNF6 |
| Targets | prometheus, node-exporter | + API, MongoDB, Redis, IRIS, InfluxDB, sondas | RF2, RF3, RF4 |
| Reglas | — | 5 de registro + 8 alertas | RF9 |

## 10. Seguridad

No se versionan `.env`, `.secretos/`, tokens ni contraseñas. Las capturas muestran Grafana en modo lectura. Detalle en [`docs/limitaciones_y_evidencia.md` §5](docs/limitaciones_y_evidencia.md#5-seguridad-de-la-evidencia-rnf6).

## 11. Mapa de requisitos

| Requisito | Dónde se cumple |
|---|---|
| RF1 Prometheus reproducible | `docker-compose.yml`, `prometheus.yml`, `scripts/iniciar_monitoreo.ps1` |
| RF2 Targets y componente de cada uno | `prometheus.yml`, `docs/inventario_de_componentes.md` §4 |
| RF3 Disponibilidad de ≥3 componentes | 6 bases × 2 capas + API (`evidencia/prometheus_targets.md`) |
| RF4 Métricas de API separadas de infraestructura | `/metrics` (`fixture_*`, `capa="aplicacion"`), `docs/metricas_y_consultas.md` §2 |
| RF5-RF7 Grafana y dashboard con comparación entre bases | `grafana/`, `grafana/README.md`, `evidencia/dashboards/` |
| RF8 Consultas PromQL explicadas | `docs/metricas_y_consultas.md` §3 (6 consultas) |
| RF9 Alertas | `prometheus/reglas-o-alertas.yml`, `docs/alertas_y_umbral.md` |
| RF10 Prueba de falla controlada | `evidencia/prueba_de_falla_redis_*`, `evidencia/prueba_de_falla.md` |
| RF11 Métricas vs. objetivos del TPO | `docs/metricas_y_consultas.md` §5 |
| RF12 Mejora transversal | `docs/decisiones_de_arquitectura.md` §6-7, `evidencia/comparacion_corte_rapido.md` |
| RF13-RF16 Defensa | `defensa/`, `docs/defensa_final.md`, `docs/decisiones_de_arquitectura.md` |
| RNF1-RNF12 | Este README (reproducibilidad), `docs/limitaciones_y_evidencia.md` (honestidad, seguridad, plan B), `defensa/guion_de_20_minutos.md` |

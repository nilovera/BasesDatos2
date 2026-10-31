# Limitaciones, evidencia y honestidad experimental (RNF8, punto 7)

## 1. Qué es medido, qué es diseño, qué es estimación y qué no se pudo obtener

| Categoría | Contenido | Dónde está |
|---|---|---|
| **Medido en este hito** | Targets UP/DOWN y métricas disponibles; throughput, latencia (P50/P95/P99), errores y disponibilidad durante 3 pruebas controladas; tiempos de detección y recuperación; disparo y resolución de alertas; CPU del proceso de la API; licencias de IRIS y memoria de Redis; integridad de datos antes y después | `evidencia/` |
| **Medido en hitos anteriores y reutilizado** | 8 conexiones de IRIS Community, efecto del pool (−84 %), P95 con 80 usuarios (Hito 12); aislamiento con MongoDB caído (Hito 11) | Ramas `Conectividad` y `carga-optimizacion` |
| **Objetivos de diseño** | Umbrales de alerta (250 ms, 5 %, 85 %, 75 %); ventana del corte rápido (10 s) | `docs/alertas_y_umbral.md` |
| **Propuestas no implementadas** | Réplicas, sharding y distribución por región para 2030; exporter JMX de Cassandra; varios procesos de la API; Alertmanager | `docs/decisiones_de_arquitectura.md` (marcadas como "propuesta") |
| **No se pudo obtener en el laboratorio** | Métricas internas de Neo4j (Enterprise) y de Cassandra (requiere agente JMX); CPU por contenedor (cAdvisor no validado); comportamiento con varios nodos; tráfico de un Mundial real | Esta sección |

## 2. Limitaciones del monitoreo

1. **Neo4j y Cassandra sin métricas internas.** Se observan solo por la sonda TCP, el ping de la API y la latencia/errores de sus rutas. No se puede ver, por ejemplo, una compactación de Cassandra; solo su efecto en la latencia.
2. **node-exporter mide la VM de WSL2, no Windows.** La API corre en Windows: su CPU se mide aparte, con psutil.
3. **cAdvisor no se validó** en esta notebook (perfil opcional). El panel "CPU por contenedor" queda vacío.
4. **Resolución temporal:** el scraping es cada 15 s y el diagnóstico de la API tiene una caché de 15 s. Una caída de menos de ~15 s puede no verse en `fixture_dependencia_up` (sí se vería en los errores 5xx).
5. **Precisión de los percentiles:** salen de buckets del histograma (5, 10, 25, 50 ms…). "4,9 ms" quiere decir "por debajo de 5 ms".
6. **Latencia interna vs. del cliente:** el histograma mide dentro de la API (~21 ms de P95). El generador, en la misma notebook, midió ~125-135 ms. La diferencia es cola de uvicorn, red local y el propio generador. Para el usuario final importa la segunda; para ubicar el motor, la primera.
7. **Sin Alertmanager:** las alertas se ven en Prometheus y Grafana, pero no se notifican.
8. **Un solo proceso de la API:** las métricas no distinguen instancias.

## 3. Limitaciones de las pruebas

1. **Una corrida por versión** del corte rápido. La diferencia es grande (47 → 115 → 138 req/s) y el throughput antes y después de la falla se repitió dentro de ±2 % en las tres. Aun así, no hay repeticiones para estimar la variación, como sí hubo en el Hito 12.
2. **Una sola notebook:** el generador de carga, la API, las seis bases y el monitoreo compiten por la misma CPU y memoria (memoria de la VM de Docker ~85 %, captura 11).
3. **Falla de un solo tipo:** contenedor detenido (`docker stop`). No se probaron una base lenta, una partición de red ni un disco lleno.
4. **El comportamiento de 2 s al conectarse a un puerto cerrado** es propio de Windows. En Linux el rechazo es inmediato: allí el corte rápido aportaría menos frente a un contenedor detenido, pero sigue siendo útil ante timeouts. Es una explicación consistente con lo medido (P95 de Redis 2,4-2,8 s), no una medición aislada de la pila TCP.
5. **Datos sintéticos** del Hito 12 (sesiones `SES-H12-*`, partidos `PAR-H12*`, comentarios marcados) más los datos de laboratorio de los hitos 4 a 9. No hay datos reales ni personales.
6. **Commits marcados "con cambios sin commitear"** en la evidencia: durante las corridas, la carpeta `evidencia/` todavía no estaba versionada. El código de la API y de los scripts sí estaba commiteado en el hash indicado (corte v1 en `2303e8c`, corte v2 en `c2363f2`).

## 4. Anomalías e incidentes observados

### Incidente real: IRIS arrancó sin su carpeta de datos (30/10, 23:12)

- **Qué vio el monitoreo:** sonda TCP de IRIS en OK, pero `fixture_dependencia_up{dependencia="InterSystems IRIS"} = 0` y el target `iris` DOWN con error `EOF` (captura `00a_incidente_iris_caida_verificacion.png`). Ese patrón dice "el puerto escucha pero el motor no se puede usar".
- **Causa (logs, captura `00b`):** `/durable/mgr: No such file or directory`. El compose del Hito 9 monta los datos desde `~/docker/data/iris` del Ubuntu de WSL. Esa distro estaba apagada cuando el contenedor arrancó, y Docker montó una carpeta vacía.
- **Recuperación:** se encendió la distro (`wsl -d Ubuntu`) y se reinició el contenedor. Los datos estaban intactos: 15/15 huellas idénticas al catálogo del Hito 12.
- **Mejora derivada:** `iniciar_monitoreo.ps1` ahora despierta la distro antes de tocar las bases y reinicia las que están `unhealthy`.
- **Lección para la defensa:** es exactamente el caso que la doble capa (sonda + API) permite diagnosticar en segundos.

### Congelamiento breve durante `docker start`

En las corridas con corte rápido, el generador registró ~5-8 s con muy pocas respuestas **de todas las bases** justo mientras `docker start` tardaba 5-9 s (en la corrida sin corte, el start tardó 0,6 s y no hubo congelamiento). **Hipótesis no verificada:** Docker Desktop reconfigura el reenvío de puertos de Windows al publicar los puertos del contenedor, y las conexiones locales a las otras bases (que usan el mismo mecanismo) se demoran. Puede estar relacionado con los congelamientos de ~4 s que reportó el Hito 12. Se ve en el gráfico de comparación como una baja de throughput posterior al `start`.

## 5. Seguridad de la evidencia (RNF6)

- No se versionan `.env` (API y monitoreo) ni `.secretos/` (token de InfluxDB, password de IRIS): están en `.gitignore` y se generan con `scripts/preparar_secretos.py`.
- `.env.example` del monitoreo solo tiene marcadores.
- Las capturas muestran Grafana en modo lectura (sin login) y Prometheus: ninguna muestra credenciales, URI con usuario ni tokens.
- Los JSON de evidencia guardan solo parámetros no secretos (`fixture_api_info`: versión, pool, ventana del corte).
- Las credenciales de MongoDB y Neo4j que aparecen en los compose de los hitos 4 y 5 son de laboratorio y ya estaban versionadas en esos hitos. No se reutilizan en ningún archivo nuevo del Hito 13.

## 6. Plan B para la defensa (RNF7)

| Si falla… | Alternativa preparada |
|---|---|
| Docker o alguna base el día de la defensa | Capturas en `evidencia/dashboards/` (todo el ciclo normal → falla → recuperación) y gráficos PNG de cada prueba |
| Grafana | Prometheus directo (`/targets`, `/alerts`, `/graph`) o `verificar_targets.ps1` en consola |
| Prometheus / la red local | `evidencia/*/prometheus_series.json` y los `README.md` de cada prueba, con todos los números |
| La notebook | El repositorio en GitHub tiene la presentación HTML (abre sin internet) y toda la evidencia |
| Falta de tiempo | El guion marca qué partes se pueden saltear ([`../defensa/guion_de_20_minutos.md`](../defensa/guion_de_20_minutos.md)) |

## 7. Índice de evidencia

| Evidencia | Qué demuestra | Requisito |
|---|---|---|
| `evidencia/prometheus_targets.md` / `.json` | 9 jobs esperados UP; reglas cargadas; disponibilidad en tres capas | RF1, RF2, RF3 |
| `evidencia/resultados_sin_secretos/metricas_disponibles.json` | Métricas que entrega cada job (inventario real) | RF2, RNF3 |
| `evidencia/resultados_sin_secretos/integridad_datos_antes.json` / `_despues.json` | 6 bases × 15 claves con respuesta idéntica al catálogo del Hito 12 | RNF5, RNF11 |
| `evidencia/prueba_de_falla_redis_corte0_*/` | Falla controlada sin corte rápido (problema detectado) | RF10 |
| `evidencia/prueba_de_falla_redis_corte10v1_*/` | Corte rápido v1 | RF12 |
| `evidencia/prueba_de_falla_redis_corte10v2_*/` | Corte rápido v2 (adoptado) | RF10, RF12 |
| `evidencia/comparacion_corte_rapido.md` / `.png` | Antes/después de la mejora | RF12 |
| `evidencia/dashboards/00a-13` | Capturas de Grafana y Prometheus (normal, falla, alertas, recuperación, comparación) | RF5, RF6, RF7, RF10 |
| `prometheus/pruebas-reglas.yml` | Alertas verificadas con promtool | RF9 |
| `tests/unit/test_metrics_middleware.py`, `test_corte_rapido.py` | Instrumentación y corte rápido verificados | RF4, RF12 |

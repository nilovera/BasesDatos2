# Infraestructura y observabilidad

El Compose actual levanta MongoDB, Redis, Cassandra, InfluxDB, Neo4j, PostgreSQL Data Mart, sus componentes auxiliares, la API,
Prometheus y Grafana. Todos los puertos se publican solamente sobre `127.0.0.1`.

## Servicios actuales

| Servicio | Puerto local | Función |
|---|---:|---|
| API | 8000 | Contrato deportivo y `/metrics` |
| MongoDB | 27017 | Fuente oficial y Outbox |
| Redis | 6379 | Caché, sesiones y datos temporales |
| Redis Exporter | 9121 | Memoria, hits, misses, evictions y persistencia |
| Cassandra | 9042 | Comentarios y moderación por consulta |
| InfluxDB | 8181 | Series deportivas; API autenticada, sin UI web |
| Neo4j | 7474/7687 | Browser, relaciones y recorridos Bolt |
| PostgreSQL Data Mart | 5433 | Esquema estrella y consultas analíticas |
| Prometheus | 9090 | Recolección de métricas técnicas |
| Grafana | 3000 | Dashboard `Fixture2030 — plataforma operacional y Data Mart` |

Grafana se aprovisiona automáticamente con Prometheus como fuente. Usuario
local: `admin`. La contraseña de laboratorio por defecto es `fixture2030` y
puede cambiarse definiendo `GRAFANA_ADMIN_PASSWORD` antes del primer arranque.
No es una configuración productiva.

Prometheus carga las reglas versionadas de `infra/prometheus/rules/`. Incluyen
indisponibilidad de la API, cinco motores y Data Mart, tasa de HTTP 5xx,
presión Redis y acumulación de Outbox. Los umbrales y responsables están documentados en
`docs/monitoreo/alertas_y_umbrales.md`.

## Ejecución

```powershell
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_flujo_mongodb.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_patrones_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_comentarios_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_telemetria_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_grafo_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_datamart.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_datamart.ps1
powershell -ExecutionPolicy Bypass -File scripts\comparar_rendimiento_datamart.ps1 -Iteraciones 100
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_datamart.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_datamart.ps1
powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia.ps1 -Scenario verificacion-integrada
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_api.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_mongodb.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
```

Para detener sin borrar datos:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\detener_plataforma.ps1
```

No usar `docker compose down -v` salvo que se decida explícitamente eliminar
todos los volúmenes del laboratorio.

## Límites

MongoDB, Redis, Cassandra, InfluxDB, Neo4j y PostgreSQL tienen un único miembro: permiten demostrar los
patrones, pero no alta disponibilidad. Redis Exporter aporta un tercer target
directo a Prometheus; Cassandra se observa funcionalmente mediante la API y
requiere JMX para métricas internas en RF=3. El dashboard sigue siendo una
línea base y no evidencia aún un SLO alcanzado.

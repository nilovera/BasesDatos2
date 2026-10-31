# Targets de Prometheus - 2026-10-30T23:23:47-03:00

Generado por `scripts/verificar_targets.py` sobre el commit `27b8139 (con cambios sin commitear)`. Fuente: `GET /api/v1/targets` y `GET /api/v1/query` de Prometheus.

| Job | Componente | Capa | Mecanismo | Estado | Duración scraping (s) | Error |
|---|---|---|---|---|---:|---|
| fixture-api | API | aplicacion | endpoint_propio | **UP** | 0.005 | — |
| cadvisor | Contenedores | infraestructura | exporter | **DOWN** | 3.296 | Get "http://cadvisor:8080/metrics": dial tcp: lookup cadvisor on 127.0.0.11:53: no such host |
| influxdb | InfluxDB | infraestructura | metricas_nativas | **UP** | 0.015 | — |
| iris | InterSystems IRIS | infraestructura | metricas_nativas | **UP** | 0.041 | — |
| mongodb | MongoDB | infraestructura | exporter | **UP** | 0.124 | — |
| node-exporter | Host Docker | infraestructura | exporter | **UP** | 0.016 | — |
| redis | Redis | infraestructura | exporter | **UP** | 0.016 | — |
| prometheus | Prometheus | monitoreo | endpoint_propio | **UP** | 0.004 | — |
| sonda-http | API | red | sonda_http | **UP** | 0.006 | — |
| sonda-tcp | Cassandra | red | sonda_tcp | **UP** | 0.002 | — |
| sonda-tcp | InfluxDB | red | sonda_tcp | **UP** | 0.003 | — |
| sonda-tcp | InterSystems IRIS | red | sonda_tcp | **UP** | 0.003 | — |
| sonda-tcp | MongoDB | red | sonda_tcp | **UP** | 0.011 | — |
| sonda-tcp | Neo4j | red | sonda_tcp | **UP** | 0.004 | — |
| sonda-tcp | Redis | red | sonda_tcp | **UP** | 0.003 | — |

## Disponibilidad de las bases en tres capas

- **api_puede_usar_la_base (fixture_dependencia_up):** MongoDB = 1, Neo4j = 1, Cassandra = 1, Redis = 1, InfluxDB = 1, InterSystems IRIS = 1
- **puerto_acepta_conexiones (probe_success sonda-tcp):** InterSystems IRIS = 1, MongoDB = 1, Cassandra = 1, InfluxDB = 1, Neo4j = 1, Redis = 1
- **exporter_llega_al_motor:** MongoDB (mongodb_up) = 1, Redis (redis_up) = 1

Reglas cargadas: **13**. Alertas en este momento: ninguna.

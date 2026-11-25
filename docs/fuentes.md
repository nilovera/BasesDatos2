# Fuentes y procedencia

Fecha de revisión de referencia: 20 de noviembre de 2026.

| Componente | Repositorio / rama | Commit inspeccionado |
|---|---|---|
| Catálogo MongoDB | nilovera/BasesDatos2 — MongoDB | d629d49d020941c0faebbe7130bfeec510eb7d37 |
| Cassandra | nilovera/BasesDatos2 — Cassandra | 982d79c138a61d2e03bd196bf9b8a00649b7c501 |
| Redis | nilovera/BasesDatos2 — Redis | 53227100afe7687eea19c3b7c3d43f6817c60668 |
| InfluxDB vigente | nilovera/BasesDatos2 — InfluxDB | 1668d8382d4e57ff4c458798ffa384f7c923922f |
| Integración y mejoras H11–H13 | nilovera/BasesDatos2 — monitoreo | 35f43f891f4fc68b41e4c35bd02c727582bc4ab6 |
| API H10, antecedente | nilovera/BasesDatos2 — API | 91981c10a230812fb36cc3ee8b6b40179629016f |
| Rama Neo, contenido MongoDB antiguo | nilovera/BasesDatos2 — Neo | 6c574ad704c6f3185246d78ed9cb07dc8c4146d1 |

La rama `Neo` no contiene una implementación Neo4j reutilizable: conserva una
carga MongoDB antigua. Por eso el incremento final de Neo4j se construye como
proyección nueva a partir del catálogo común, sin importar datos ni credenciales
del contenedor histórico. `InlfuxDB` es una rama desactualizada y no se utiliza
como referencia.

`data/fuentes/catalogo_base.json` conserva selecciones, perfiles de nombres y posiciones del generador MongoDB del commit indicado. `scripts/catalogo.py` reproduce sus IDs, nombres, fechas y pertenencias. La demostración de partido y sus equivalencias se agregan como decisión explícita de la rama limpia `trabajo-final`.

Los siete Markdown de `docs/antecedentes` proceden de los documentos preparados en el proyecto. Conservan evidencia y resultados históricos; las decisiones vigentes de implementación están en `docs/diseno` y el README. Los antecedentes no representan por sí solos pruebas de la arquitectura final.

No se incorporan credenciales, archivos internos de bases ni CSV masivos. Los datos personales de jugadores son sintéticos.

## Referencias técnicas del incremento de InfluxDB

- InfluxDB 3 Core, instalación y versión fijada: https://docs.influxdata.com/influxdb3/core/install/
- Tokens administrativos preconfigurados: https://docs.influxdata.com/influxdb3/core/admin/tokens/admin/preconfigured/
- Bases y retención: https://docs.influxdata.com/influxdb3/core/admin/databases/create/
- Escrituras v3 y lotes completos: https://docs.influxdata.com/influxdb3/core/write-data/http-api/v3-write-lp/
- Consultas SQL HTTP: https://docs.influxdata.com/influxdb3/core/query-data/execute-queries/influxdb-v3-api/
- Autorización de scrapes Prometheus: https://prometheus.io/docs/prometheus/latest/configuration/configuration/

Se fija `influxdb:3.12.3-core`; `3-core` es un tag flotante y no se usa en la
plataforma final. Las bases nuevas usan guiones porque la API v3 documenta esa
restricción de nombres.

## Referencias técnicas del incremento de API

- FastAPI, contenedores: https://fastapi.tiangolo.com/deployment/docker/
- MongoDB PyMongo, transacciones: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/transactions/
- Prometheus Python Client, ASGI: https://prometheus.github.io/client_python/exporting/http/asgi/
- Grafana, provisioning: https://grafana.com/docs/grafana/latest/administration/provisioning/

Versiones directas fijadas para reproducibilidad: FastAPI 0.165.0, PyMongo
4.20.1, Prometheus Client 0.26.0 y Uvicorn 0.54.0. Las imágenes de laboratorio
son Prometheus 3.16.0 y Grafana 13.3.1.

## Referencias técnicas del incremento de Neo4j

- Neo4j Operations Manual, imágenes Docker: https://neo4j.com/docs/operations-manual/current/docker/introduction/
- Neo4j Operations Manual, secretos Docker y `NEO4J_AUTH_FILE`: https://neo4j.com/docs/operations-manual/current/docker/configuration/#docker-secrets
- Cypher Manual, restricciones: https://neo4j.com/docs/cypher-manual/current/constraints/
- Cypher Manual, `MERGE`: https://neo4j.com/docs/cypher-manual/current/clauses/merge/
- Cypher Manual, caminos más cortos: https://neo4j.com/docs/cypher-manual/current/patterns/shortest-paths/
- Neo4j Python Driver Manual: https://neo4j.com/docs/python-manual/current/

Se fija `neo4j:5.26.34-community-trixie` y el driver Python `6.4.1`. El grafo es
una proyección reconstruible de MongoDB y el catálogo común; no se reutilizan
los volúmenes del contenedor histórico.

## Referencias técnicas del Data Mart

- Imagen oficial PostgreSQL y secretos `_FILE`: https://hub.docker.com/_/postgres
- Psycopg 3, instalación binaria: https://www.psycopg.org/install/
- Psycopg 3, pool de conexiones: https://www.psycopg.org/psycopg3/docs/advanced/pool.html
- PostgreSQL, `INSERT ... ON CONFLICT`: https://www.postgresql.org/docs/current/sql-insert.html

Se fija `postgres:18.7-alpine3.24`, `psycopg[binary]==3.3.9` y
`psycopg-pool==3.3.3`. PostgreSQL es una
proyección analítica reconstruible y no participa de la transacción oficial.


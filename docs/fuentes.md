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

Los scripts reales de Neo4j están en entorno-local/datos/neo4j dentro de monitoreo. InlfuxDB es una rama desactualizada y no se utiliza como referencia.

`data/fuentes/catalogo_base.json` conserva selecciones, perfiles de nombres y posiciones del generador MongoDB del commit indicado. `scripts/catalogo.py` reproduce sus IDs, nombres, fechas y pertenencias. La demostración de partido y sus equivalencias se agregan como decisión explícita de la rama limpia `trabajo-final`.

Los siete Markdown de `docs/antecedentes` proceden de los documentos preparados en el proyecto. Conservan evidencia y resultados históricos; las decisiones vigentes de implementación están en `docs/diseno` y el README. Los antecedentes no representan por sí solos pruebas de la arquitectura final.

No se incorporan credenciales, archivos internos de bases ni CSV masivos. Los datos personales de jugadores son sintéticos.

## Referencias técnicas del incremento de API

- FastAPI, contenedores: https://fastapi.tiangolo.com/deployment/docker/
- MongoDB PyMongo, transacciones: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/transactions/
- Prometheus Python Client, ASGI: https://prometheus.github.io/client_python/exporting/http/asgi/
- Grafana, provisioning: https://grafana.com/docs/grafana/latest/administration/provisioning/

Versiones directas fijadas para reproducibilidad: FastAPI 0.165.0, PyMongo
4.20.1, Prometheus Client 0.26.0 y Uvicorn 0.54.0. Las imágenes de laboratorio
son Prometheus 3.16.0 y Grafana 13.3.1.


# Resultados de pruebas

## Entorno

- Fecha: 10 de octubre de 2026.
- Python: 3.10.11.
- API: FastAPI con Uvicorn.
- Pruebas: Pytest y Postman/Newman.
- Dependencias: seis motores reales ejecutados localmente.

## Resumen

| Validación | Resultado | Evidencia |
|---|---|---|
| Conectividad | 6 de 6 motores disponibles | `scripts/probar_conexiones.py` |
| Integración | 21 de 21 pruebas aprobadas | `docs/evidencia/09_pruebas_integracion.txt` |
| Dependencia caída | Redis 503, MongoDB 200 y Redis recuperado 200 | `docs/evidencia/10_dependencia_redis_caida.txt` |
| OpenAPI | 8 rutas y 9 operaciones | `docs/evidencia/11_openapi_exportado.txt` |
| Postman | 9 solicitudes para los 6 motores | `docs/evidencia/12_postman_coleccion.txt` |
| Newman | 35 aserciones y 0 fallos | `docs/evidencia/13_postman_newman.txt` |
| Rendimiento | 60 de 60 solicitudes exitosas | `docs/evidencia/14_rendimiento_api.txt` |

## Cobertura por motor

- MongoDB: equipos, jugadores, paginación, recurso inexistente y datos inválidos.
- Neo4j: partidos, equipos, sedes, eventos y recurso inexistente.
- Cassandra: comentarios, page state, partición vacía y bucket inválido.
- Redis: consulta, cierre, expiración, caída y recuperación de sesiones.
- InfluxDB: detalle cada 10 segundos, resúmenes cada 15 minutos y ventanas temporales.
- InterSystems IRIS: partido, árbitro, eventos y recurso inexistente.

## Pruebas de integración

La suite `tests/integration/test_api_live.py` ejecutó 21 pruebas contra los motores reales.

- Aprobadas: 21.
- Fallidas: 0.
- Informe JUnit: `docs/evidencia/09_pruebas_integracion.xml`.
- Captura: `docs/evidencia/09_pruebas_integracion.png`.

## Aislamiento de fallos

Al detener Redis, su endpoint respondió HTTP 503 mientras MongoDB continuó respondiendo HTTP 200. Después de reiniciar Redis, el endpoint volvió a responder HTTP 200.

La falla fue detectada en aproximadamente 2,4 segundos.

Evidencias:

- `docs/evidencia/10_dependencia_redis_caida.txt`
- `docs/evidencia/10_dependencia_redis_caida.png`

## Postman y OpenAPI

El contrato OpenAPI 3.1.0 fue exportado en JSON y YAML. La colección de Postman fue ejecutada con Newman dentro de Docker.

Resultado Newman:

- Solicitudes: 9.
- Aserciones: 35.
- Fallos: 0.
- Duración: 1581 ms.
- Promedio: 149 ms.

## Rendimiento

Se midieron diez solicitudes por motor, con una solicitud previa de calentamiento y concurrencia igual a uno.

- Total: 60 solicitudes.
- Exitosas: 60.
- Promedio general: 23,57 ms.
- Resultado: aprobado.

Los detalles, el hardware y la relación con las evidencias están documentados en `docs/rendimiento.md`.

## Conclusión

La API integra correctamente los seis motores, valida entradas, pagina resultados, controla errores y mantiene disponibilidad parcial ante la caída de una dependencia.

Cada resultado está relacionado explícitamente con su archivo de evidencia.

# Arquitectura integrada de Fixture 2030

## Objetivo

Fixture 2030 API integra seis motores especializados mediante una API REST desarrollada con Python 3.10 y FastAPI.

Cada caso de uso consulta al motor responsable del dato. La API coordina el acceso, pero no funciona como una nueva fuente de verdad.

## Arquitectura por capas

La aplicación utiliza cuatro niveles principales:

1. **Rutas:** reciben solicitudes HTTP y validan parámetros.
2. **Servicios:** coordinan cada caso de uso.
3. **Adaptadores:** encapsulan drivers, conexiones y consultas.
4. **Motores:** almacenan y procesan los datos especializados.

El flujo general es:

`Cliente → Ruta FastAPI → Servicio → Adaptador → Base de datos`

## Distribución políglota

| Motor | Responsabilidad | Endpoint |
|---|---|---|
| MongoDB | Equipos y jugadores | `GET /api/v1/equipos/{codigo}` y `GET /api/v1/jugadores` |
| Neo4j | Relaciones entre partidos, equipos, sedes y eventos | `GET /api/v1/partidos/{codigo}/eventos` |
| Cassandra | Comentarios por partido y bucket temporal | `GET /api/v1/partidos/{codigo}/comentarios` |
| Redis | Sesiones temporales con TTL | `GET` y `DELETE /api/v1/sesiones/{sesion_id}` |
| InfluxDB | Estadísticas detalladas y resúmenes de 15 minutos | `GET /api/v1/partidos/{codigo}/estadisticas` |
| InterSystems IRIS | Objetos persistentes de partido, árbitro y eventos | `GET /api/v1/partidos/{codigo}/detalle` |

## Flujo de una solicitud

1. El cliente invoca un endpoint.
2. FastAPI valida rutas y parámetros.
3. El middleware genera un `X-Request-ID`.
4. La ruta selecciona el servicio.
5. El servicio utiliza el adaptador del motor.
6. El adaptador ejecuta la consulta.
7. La respuesta se transforma al esquema público.
8. Se devuelve `X-Request-ID` y `X-Process-Time-Ms`.
9. El resultado queda registrado en los logs.

## Contrato de errores

| Código | Significado |
|---|---|
| `200` | Operación correcta |
| `404` | Recurso inexistente o sesión expirada |
| `422` | Entrada o parámetro inválido |
| `503` | Dependencia no disponible |
| `500` | Error interno inesperado |

## Aislamiento de fallos

La prueba realizada el 10 de octubre de 2026 demostró que la caída de Redis afecta solamente sus endpoints:

- Redis devolvió `503`.
- MongoDB continuó respondiendo `200`.
- Redis volvió a responder `200` después de recuperarse.

Evidencias:

- `docs/evidencia/10_dependencia_redis_caida.txt`
- `docs/evidencia/10_dependencia_redis_caida.png`

## OpenAPI

El contrato exportado utiliza OpenAPI 3.1.0 y contiene 8 rutas con 9 operaciones.

Archivos:

- `openapi/fixture2030-openapi.json`
- `openapi/fixture2030-openapi.yaml`
- `docs/evidencia/11_openapi_exportado.txt`

## Decisiones técnicas

- Se utiliza un adaptador independiente por motor.
- Las credenciales se mantienen fuera del código.
- Cada respuesta informa su `fuente_datos`.
- Cassandra conserva la paginación mediante `page_state`.
- InfluxDB expone datos cada 10 segundos y resúmenes cada 15 minutos.
- Redis evita reintentos prolongados cuando no está disponible.
- IRIS abre y cierra una conexión por solicitud.

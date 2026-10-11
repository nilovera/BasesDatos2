# Fixture 2030 - API REST Integrada

Hito 10 de Ingeniería de Datos II.

API REST desarrollada con Python y FastAPI que integra seis tecnologías de persistencia utilizadas en los hitos anteriores del proyecto Fixture 2030.

## Tecnologías integradas

| Motor | Responsabilidad |
|---|---|
| MongoDB | Equipos y jugadores |
| Neo4j | Relaciones entre partidos, equipos, sedes y eventos |
| Cassandra | Comentarios por partido y ventana temporal |
| Redis | Sesiones con expiración |
| InfluxDB | Estadísticas temporales y resúmenes |
| InterSystems IRIS | Persistencia orientada a objetos |

## Arquitectura

La aplicación se divide en:

1. Routes: contrato HTTP y validación de parámetros.
2. Services: reglas de aplicación.
3. Adapters: acceso específico a cada motor.

Cada dependencia tiene su propio adaptador. La caída de un motor no detiene los endpoints correspondientes a los demás.

## Endpoints

| Método | Ruta | Motor |
|---|---|---|
| GET | `/health` | API |
| GET | `/api/v1/equipos/{codigo}` | MongoDB |
| GET | `/api/v1/jugadores` | MongoDB |
| GET | `/api/v1/partidos/{codigo}/eventos` | Neo4j |
| GET | `/api/v1/partidos/{codigo}/comentarios` | Cassandra |
| GET | `/api/v1/sesiones/{sesion_id}` | Redis |
| DELETE | `/api/v1/sesiones/{sesion_id}` | Redis |
| GET | `/api/v1/partidos/{codigo}/estadisticas` | InfluxDB |
| GET | `/api/v1/partidos/{codigo}/detalle` | InterSystems IRIS |

## Funcionalidades

- Validación con Pydantic.
- Paginación por cursor en MongoDB.
- Paginación mediante page state en Cassandra.
- Ventanas temporales en InfluxDB.
- Expiración y cierre de sesiones en Redis.
- Navegación de relaciones en Neo4j.
- Lectura de objetos persistentes en IRIS.
- Errores HTTP uniformes.
- Identificador y duración por solicitud.
- OpenAPI, Swagger y colección Postman.
- Pruebas automatizadas contra motores reales.

## Estructura principal

- `app`: código de la API.
- `docs`: documentación y evidencias.
- `openapi`: contrato exportado en JSON y YAML.
- `postman`: colección y entorno de Postman.
- `scripts`: automatizaciones de ejecución y validación.
- `tests`: pruebas automatizadas.

## Requisitos previos

- Windows PowerShell.
- Python 3.10.
- Docker Desktop.
- Los seis contenedores de bases de datos iniciados.
- Datos correspondientes a los hitos anteriores cargados.

La API consume los motores existentes; este repositorio no vuelve a crear sus modelos ni sus datos.

## Configuración inicial

Crear el entorno virtual:

    py -3.10 -m venv .venv

Activarlo:

    .\.venv\Scripts\Activate.ps1

Instalar dependencias:

    python -m pip install -r requirements.txt

Crear la configuración local:

    Copy-Item .env.example .env

Completar `.env` con las credenciales locales de cada motor. El archivo `.env` no debe publicarse ni agregarse a Git.

## Ejecutar la API

Desde la raíz del proyecto:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\reiniciar_api.ps1"

Direcciones disponibles:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Pruebas automatizadas

Ejecutar las 21 pruebas de integración:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\ejecutar_pruebas.ps1"

La suite utiliza las seis dependencias reales y genera evidencia en `docs/evidencia`.

## Postman y Newman

Regenerar la colección:

    .\.venv\Scripts\python.exe -m scripts.generar_postman

Ejecutar la colección dentro de Docker:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\ejecutar_postman.ps1"

Resultado final registrado:

- 9 solicitudes.
- 35 aserciones.
- 0 fallos.

## OpenAPI

Exportar el contrato:

    .\.venv\Scripts\python.exe -m scripts.exportar_openapi

Archivos generados:

- `openapi/fixture2030-openapi.json`
- `openapi/fixture2030-openapi.yaml`

## Rendimiento

Ejecutar la medición:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\medir_rendimiento.ps1"

Resultado final:

- 60 de 60 solicitudes exitosas.
- Promedio general de 23,57 ms.
- Fecha de medición: 10 de octubre de 2026.

## Documentación

- `docs/arquitectura_integrada.md`
- `docs/resultados_pruebas.md`
- `docs/rendimiento.md`
- `docs/seguridad_y_limitaciones.md`

## Evidencias

Las transcripciones, reportes, resultados estructurados y capturas se encuentran en `docs/evidencia`.

Cada resultado se encuentra vinculado con su evidencia correspondiente dentro de `docs/resultados_pruebas.md`.

## Seguridad

- Las credenciales se almacenan solamente en `.env`.
- `.env.example` no contiene secretos.
- Los archivos sensibles están excluidos mediante `.gitignore`.
- La API no expone trazas internas ni cadenas de conexión.
- Cada solicitud incluye `X-Request-ID` y `X-Process-Time-Ms`.

## Resultado del hito

La solución demuestra persistencia políglota mediante una única API REST, con acceso real a MongoDB, Neo4j, Cassandra, Redis, InfluxDB e InterSystems IRIS.

Las pruebas automatizadas, la colección Postman, el contrato OpenAPI, la prueba de dependencia caída y la medición de rendimiento finalizaron correctamente.

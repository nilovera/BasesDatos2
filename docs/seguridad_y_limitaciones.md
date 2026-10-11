# Seguridad y limitaciones

## Medidas de seguridad implementadas

### Gestión de credenciales

Las credenciales y tokens se almacenan exclusivamente en el archivo local `.env`.

El repositorio incluye `.env.example` con los nombres de las variables necesarias, pero sin valores sensibles. Los siguientes elementos se encuentran excluidos mediante `.gitignore`:

- `.env`
- entornos virtuales
- archivos PID
- registros locales
- cachés de Python
- tokens y secretos locales

Ninguna respuesta de la API expone contraseñas, tokens ni cadenas de conexión.

### Validación de entradas

FastAPI y Pydantic validan los datos antes de acceder a los motores:

- Formato de identificadores de equipos, partidos y sesiones.
- Límites máximos para la paginación.
- Formato del bucket temporal de Cassandra.
- Granularidad permitida para InfluxDB.
- Orden correcto de las fechas `desde` y `hasta`.
- Parámetros obligatorios y tipos de datos.

Las solicitudes inválidas reciben HTTP 422 con un cuerpo de error uniforme.

### Consultas seguras

Los adaptadores utilizan parámetros separados de las consultas siempre que el controlador del motor lo permite.

Esto reduce el riesgo de inyección en:

- MongoDB.
- Neo4j.
- Cassandra.
- InfluxDB.
- InterSystems IRIS.

La API no permite recibir directamente consultas MongoDB, Cypher, CQL, SQL ni comandos Redis desde el cliente.

### Manejo de errores

Los errores internos se registran en el servidor, pero no se devuelven trazas al cliente.

El contrato de error contiene:

- Código controlado.
- Mensaje comprensible.
- Identificador de la solicitud.
- Detalles de validación cuando corresponde.

Los fallos de dependencias se traducen a HTTP 503 y los tiempos de espera a HTTP 504.

### Trazabilidad

Cada solicitud incorpora:

- `X-Request-ID`.
- `X-Process-Time-Ms`.
- Método HTTP.
- Ruta solicitada.
- Dependencia utilizada.
- Código de respuesta.
- Duración de la operación.

Esto permite relacionar una respuesta con los registros de ejecución y con las evidencias del hito.

### Aislamiento de dependencias

Cada motor posee su propio adaptador. La caída de una dependencia no impide utilizar los endpoints asociados a otros motores.

La prueba documentada detuvo Redis y verificó:

- Endpoint de Redis: HTTP 503.
- Endpoint de MongoDB: HTTP 200.
- Recuperación posterior de Redis: HTTP 200.

El cliente Redis fue configurado sin reintentos prolongados para evitar que una falla bloquee innecesariamente la solicitud.

### Exposición de red

En la ejecución normal, Uvicorn escucha únicamente en `127.0.0.1`.

La dirección `0.0.0.0` se utiliza temporalmente durante la ejecución automatizada de Newman en Docker, permitiendo que el contenedor acceda a la API mediante `host.docker.internal`.

Finalizada la prueba, el script restaura la ejecución local.

## Limitaciones conocidas

El proyecto es una implementación académica local. No incluye todavía:

- Autenticación de clientes de la API.
- Autorización basada en roles.
- HTTPS y certificados TLS.
- Rate limiting.
- Balanceo de carga.
- Alta disponibilidad de la API.
- Rotación automática de secretos.
- Métricas centralizadas y alertas.
- Pruebas de carga concurrente intensiva.
- Sincronización automática entre todos los motores.
- Despliegue productivo mediante orquestadores.

Las mediciones de rendimiento se realizaron con concurrencia igual a uno. Por lo tanto, describen el comportamiento local de las consultas, pero no representan una prueba de capacidad máxima.

## Recomendaciones para producción

Para una evolución productiva se recomienda:

1. Incorporar OAuth2 o JWT.
2. Aplicar autorización por roles y permisos.
3. Utilizar HTTPS.
4. Gestionar secretos mediante un servicio especializado.
5. Agregar límites de frecuencia por cliente.
6. Implementar circuit breakers por dependencia.
7. Centralizar logs, métricas y trazas.
8. Ejecutar pruebas de carga concurrente.
9. Incorporar contenedores y health checks para la API.
10. Definir estrategias de consistencia y sincronización entre motores.

## Evidencias relacionadas

- `docs/evidencia/09_pruebas_integracion.txt`
- `docs/evidencia/10_dependencia_redis_caida.txt`
- `docs/evidencia/13_postman_newman.txt`
- `docs/evidencia/14_rendimiento_api.txt`

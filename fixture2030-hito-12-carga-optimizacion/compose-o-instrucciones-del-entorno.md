# Entorno de ejecución del Hito 12

El hito **no agrega servicios nuevos**: usa los mismos seis contenedores de los Hitos 4 a 9 y la API de los Hitos 10–11. No hace falta Prometheus ni Grafana (corresponden a la Clase 14); las métricas se toman con el propio generador, los encabezados de la API, `psutil` y `docker stats`.

## 1. Hardware y sistema donde se midió

| Elemento | Valor (de `metadatos.json` de cada corrida) |
|---|---|
| Sistema operativo | Windows 10 (10.0.19045) |
| Procesador | AMD64 Family 25 Model 33 (AMD Ryzen serie 5000), 6 núcleos físicos / 12 lógicos |
| RAM | 15,9 GB (uso del sistema durante las pruebas: 68–77 %) |
| Docker | Docker Desktop 29.7.2 con WSL 2, Docker Compose v5.4.0 |
| Python | 3.11.9 (`.venv` de la API) |

Toda la prueba corre en **una sola notebook**: generador, API y bases comparten CPU, memoria y disco. Por eso se registran los recursos de cada parte (ver [`docs/integridad_y_limitaciones.md`](docs/integridad_y_limitaciones.md)).

## 2. Servicios y versiones observadas

| Contenedor | Imagen | Puerto | Rol en la prueba |
|---|---|---|---|
| `fixture2030-mongodb` | `mongo:7.0` | 27017 | Equipos (`GET /equipos/{codigo}`) |
| `fixture2030-neo4j` | `neo4j:latest` | 7687 | Partidos y eventos (`GET /partidos/{codigo}/eventos`) |
| `fixture2030-cassandra` | `cassandra:latest` | 9042 | Comentarios por bucket (`GET /partidos/{codigo}/comentarios`) |
| `fixture2030-redis` | `redis:latest` | 6379 | Sesiones (`GET /sesiones/{id}`) |
| `fixture2030-influxdb` | `influxdb:3-core` | 8181 | Estadísticas cada 10 s (`GET /partidos/{codigo}/estadisticas`) |
| `fixture2030-iris` | `intersystems/iris-community:latest-cd` | 1972 | Detalle de partido (`GET /partidos/{codigo}/detalle`) |
| `fixture2030-mongo-express` | `mongo-express:1.0.0` | 8081 | No participa (consumo < 0,2 % CPU) |

Las imágenes `latest` pueden cambiar con el tiempo; la versión exacta usada queda en `metadatos.json → contenedores` de cada corrida. Para reproducir con la misma imagen conviene fijar la etiqueta en el compose.

Paquetes de la API registrados: FastAPI 0.143.0, Uvicorn 0.54.0 (1 proceso, sin `--workers`), httpx 0.28.1, pymongo 4.18.3, neo4j 6.4.0, cassandra-driver 3.30.1, redis 8.1.0, intersystems_irispython 5.4.1. Del hito: psutil 7.0.0 y matplotlib 3.10.3.

## 3. Cómo levantar los servicios

Opción A — con los `docker-compose.yml` de cada módulo (como en los hitos anteriores), siguiendo el README de cada uno para cargar los datos.

Opción B — con el entorno unificado de la rama `Conectividad`:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\entorno-local\preparar_entorno.ps1     # motores, datos, .venv y .env
```

Verificación antes de probar:

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\reiniciar_api.ps1
Invoke-RestMethod http://127.0.0.1:8000/health/ready     # las 6 dependencias deben figurar "up"
```

`ejecutar_carga.py` llama a `/health/ready` antes de cada corrida y guarda la respuesta en `metadatos.json → health_ready_previo`.

## 4. Configuración que cambia entre línea base y optimizada

| Parámetro | Línea base | Optimizada | Dónde se define |
|---|---|---|---|
| `IRIS_POOL_SIZE` | `0` (una conexión por solicitud, comportamiento original) | `5` | Variable de entorno que fijan `ejecutar_linea_base.ps1` / `ejecutar_prueba_optimizada.ps1` antes de reiniciar la API |
| Todo lo demás | igual | igual | `config/configuracion-ejemplo.json`, `.env` de la API |

`DEPENDENCY_TIMEOUT_SECONDS` = 5 en ambas. La API se reinicia antes de cada corrida (logs nuevos y mismo punto de partida).

## 5. Control de recursos (RNF9)

- La carga está acotada a 80 usuarios virtuales con 50–150 ms de pausa entre solicitudes.
- **Corte seguro:** si en una ventana de 20 s falla más del 50 % de las solicitudes, el generador se detiene solo (probado contra un servidor caído).
- Timeout por solicitud: 10 s.
- El generador usa 4 procesos (máximo medido: 3,9 núcleos de 12) y la API 1 núcleo.
- Antes de cada corrida se recomienda cerrar navegador y otras aplicaciones: con ~94 % de RAM ocupada al comienzo, el sistema operativo podía perturbar las mediciones.

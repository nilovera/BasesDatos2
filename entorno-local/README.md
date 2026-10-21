# Entorno local consolidado (hitos 4 a 9)

Permite levantar **en cualquier notebook** los seis motores del Fixture 2030 con sus datos, para ejecutar la API del Hito 10 y el diagnóstico del Hito 11 sin depender de la notebook donde se desarrollaron los hitos anteriores.

## Qué hace

`preparar_entorno.ps1` ejecuta, en orden:

1. Verifica Docker Desktop y Python ≥ 3.10.
2. Crea `.venv` en la raíz del repositorio e instala `requirements.txt`.
3. `docker compose up -d` con los seis servicios (la primera vez descarga unos 4 GB).
4. Espera a que cada motor responda con **su propio cliente** (`mongosh`, `cypher-shell`, `cqlsh`, `redis-cli`, `/health`, healthcheck de IRIS).
5. Carga los datos con los **scripts originales del grupo**:

| Motor | Origen | Scripts |
|---|---|---|
| MongoDB | Hito 4 (rama `main`) | `datos/mongodb/01_validaciones.js`, `02_carga_datos.js` → 64 equipos, 1.024 jugadores |
| Neo4j | Hito 5 (`fixture2030-neo4j`) | `datos/neo4j/estructura.cypher`, `carga.cypher`, `segundacarga.cypher` → 96 partidos, 192 eventos |
| Cassandra | Hito 6 (`fixture2030-cassandra`) | `datos/cassandra/esquema.cql`, `carga_muestra.cql` |
| Redis | Hito 10 | `scripts/preparar_sesiones_redis.ps1` |
| InfluxDB 3 | Hito 8 (rama `InfluxDB`) | bases y tablas de `creacion_modelo.ps1`; puntos de `generar_datos.ps1` y resumen de `agregacion.ps1`, reproducidos en `datos/influxdb/generar_influx.py` |
| IRIS | Hito 9 (rama `IRIS`) | clases `datos/iris/Fixture.*.cls` + `semilla_hito11.mac` (partido PAR-0001) |

6. Genera el `.env` de la API y `hito11-conectividad/config/conectividad.env` (ambos fuera de Git).
7. Muestra las cantidades cargadas.

Cada paso se puede repetir: las cargas usan `MERGE`, upsert o `IF NOT EXISTS`.

## Uso

Desde la raíz del repositorio, con Docker Desktop abierto:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\entorno-local\preparar_entorno.ps1
.\scripts\reiniciar_api.ps1
.\hito11-conectividad\scripts\evaluar_conectividad.ps1
```

Apagar sin perder datos:

```powershell
docker compose -f entorno-local\docker-compose.yml stop
```

Volver a encender:

```powershell
docker compose -f entorno-local\docker-compose.yml start
.\scripts\preparar_sesiones_redis.ps1   # la sesión de demo vence a los 30 minutos
```

**No usar `docker compose down -v`:** borra los volúmenes con los datos.

## Diferencias con los entornos originales

| Aspecto | Original | Entorno local | Motivo |
|---|---|---|---|
| Proyecto Compose | uno por hito | uno solo (`fixture2030`) | levantar todo con un comando |
| Persistencia | carpetas `~/docker/data/*` en WSL | volúmenes Docker con nombre | no depende de WSL ni de permisos de carpetas |
| Neo4j | plugins APOC y GDS | sin plugins | las cargas del Hito 5 no los usan y su descarga es pesada |
| Cassandra | heap por defecto | `MAX_HEAP_SIZE=1G` | consumo razonable en una notebook |
| Cassandra | carga de muestra + masiva (1.000.000 de filas) | solo carga de muestra | la masiva no es necesaria para la conectividad; por eso el Hito 11 usa la partición `PAR-0001 / 203006132000` |
| InfluxDB | generador en PowerShell | generador en Python con las mismas fórmulas | en Windows con configuración regional es-AR PowerShell escribe `50,23` y el line protocol lo rechaza |
| IRIS | directorio durable `/durable` | sin durable externo | evita permisos de carpeta; los datos se conservan con `docker stop`/`start` |
| IRIS | password definida a mano | password aleatoria en `.secretos/` | no se versionan credenciales |

Los nombres de contenedor y los puertos son los mismos que en los hitos originales, por lo que la API del Hito 10 y los scripts del Hito 11 funcionan sin cambios.

## Credenciales

- MongoDB (`admin` / `password123`) y Neo4j (`neo4j` / `fixture2030`): las mismas que el grupo documentó en los hitos 4 y 5, solo para el laboratorio local.
- InfluxDB (token de administrador) e IRIS (password de `_SYSTEM`): se generan en cada notebook y se guardan en `entorno-local/.secretos/`, que está en `.gitignore`.

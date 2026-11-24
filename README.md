# Fixture 2030 — trabajo final

Integración final del trabajo de Ingeniería de Datos II dentro del repositorio
`nilovera/BasesDatos2`, rama `trabajo-final`.

**Estado:** MongoDB autoritativo, API transaccional, Redis para datos calientes,
Cassandra para comentarios y observabilidad con Prometheus y Grafana. InfluxDB
y Neo4j siguen pendientes de integración en la rama final.

## Preparar la rama limpia

La rama `trabajo-final` debe comenzar sin heredar el contenido de `monitoreo` ni
de otra rama histórica. Las implementaciones anteriores se conservan como
antecedentes y se recuperan archivo por archivo después de su revisión.

Desde una copia limpia del repositorio:

```text
git clone https://github.com/nilovera/BasesDatos2.git
cd BasesDatos2
git switch --orphan trabajo-final
```

Copiar entonces el contenido de este paquete en la raíz del repositorio, revisar
`git status` y crear el primer commit. No realizar un merge completo de las ramas
anteriores.

## Verificar el commit inicial

Instalar Python 3.10 o superior. Desde CMD o PowerShell:

```text
python -m scripts.catalogo --check
python -m unittest discover -s tests -v
```

Si Windows utiliza el lanzador de Python, reemplazar `python` por `py`. Esta
primera entrega no requiere paquetes externos.

Para regenerar los JSON del catálogo:

```text
python -m scripts.catalogo
python -m scripts.catalogo --check
```

## Contenido y estado

| Carpeta | Contenido | Estado |
|---|---|---|
| `data/fuentes/` | Definición reproducible del dataset | Implementado |
| `data/catalogo/` | 64 equipos, 1.024 jugadores, equivalencias, partido de demostración y eventos iniciales vacíos | Generado y verificado |
| `scripts/` | Generación y comprobación de integridad | Implementado |
| `tests/` | Pruebas del catálogo, contratos, dominio, API e infraestructura | Ejecutadas estáticamente |
| `docs/antecedentes/` | Siete documentos de diseño previos | Conservados como antecedentes |
| `docs/diseno/` | Convenciones y decisiones de la rama final | Base inicial documentada |
| `backend/` | FastAPI, contrato OpenAPI, transacción e idempotencia | Implementado; ejecución integrada pendiente |
| `mongodb/` | Replica set, validadores, índices, carga y verificación | Implementado y validado en Docker |
| `redis/` | Cache-Aside, sesiones, TTL, LFU, RDB y AOF | Implementado; ejecución Docker pendiente |
| `cassandra/` | Esquema por consulta, buckets, shards e idempotencia | Implementado; ejecución Docker pendiente |
| `infra/` | Prometheus, reglas de alerta, Grafana y dashboard inicial | Implementado y ejecutado en Docker |
| `evidencia/` | Resultados trazables por commit y prueba de falla controlada | Estructura y captura automatizadas; ejecuciones pendientes de versionar |

## Arquitectura objetivo

La solución final utiliza cinco motores con responsabilidades diferentes:

| Motor | Responsabilidad principal |
|---|---|
| MongoDB | Fuente oficial de equipos, jugadores, partidos, alineaciones y eventos deportivos |
| Cassandra | Comentarios, moderación y vistas por partido/usuario con buckets y shards |
| Redis | Sesiones, caché, concurrencia y datos temporales |
| InfluxDB | Estadísticas, posiciones y series temporales |
| Neo4j | Relaciones y recorridos entre jugadores, equipos y partidos |

InterSystems IRIS fue evaluado y queda excluido de la arquitectura ejecutable.
La decisión, las alternativas consideradas, las responsabilidades reasignadas y
sus consecuencias están documentadas en
[`ADR-001`](docs/diseno/ADR-001-exclusion-iris.md).

## Decisiones iniciales

- La integración se construye en la rama limpia `trabajo-final`.
- Las ramas anteriores permanecen como evidencia; no se fusionan completas.
- Cada incorporación debe indicar origen, cambios, prueba y limitaciones.
- IDs internos: `EQ-01`, `JUG-0001`, `PAR-0001` y `EVE-000001`.
- `ARG -> EQ-01` y `MEX -> EQ-33` son las equivalencias explícitas de la demostración; las demás quedan pendientes de fuente validada.
- El partido Argentina-México del 13/06/2030 a las 20:00 UTC es un dato sintético de laboratorio.
- El partido comienza en `PROGRAMADO`, sin eventos oficiales.
- El catálogo de 96 partidos de la carga histórica de Neo4j es un antecedente, no el fixture final validado.
- `InfluxDB` es la rama de referencia; `InlfuxDB` está desactualizada y no se incorpora.

## Orden de trabajo

1. Validar la API, transacciones, idempotencia, Prometheus y Grafana en Docker.
2. Validar Cassandra y luego incorporar InfluxDB y Neo4j mediante adaptadores revisados.
3. Procesar la Outbox y construir las proyecciones idempotentes.
4. Completar usuarios, asistencias, telemetría y simulador sintético.
5. Agregar exporters, alertas y dashboards de los cinco motores.
6. Ejecutar humo, tráfico normal, estrés y recuperación.
7. Preparar la demostración y defensa final.

## Evidencia del incremento 03

Con la plataforma operativa, capturar el estado reproducible:

```text
powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia.ps1
```

Luego ejecutar la falla controlada de la API. El script detiene solamente ese
contenedor, espera que Prometheus registre `up=0` y la alerta pase a `firing`,
y siempre intenta recuperarlo en un bloque `finally`:

```text
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_api.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
```

Los resultados quedan bajo `evidencia/ejecuciones/`. Deben revisarse antes de
versionarlos y complementarse con capturas de Grafana de la misma ventana
temporal. Las consultas, umbrales, responsables y limitaciones están en
[`docs/monitoreo`](docs/monitoreo/).

## Incremento 04 Redis

Redis implementa Cache-Aside, invalidación después de una escritura oficial,
sesiones con renovación explícita, contadores atómicos, ranking, evicción LFU,
snapshots RDB y AOF. Para probarlo:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_patrones_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_redis.ps1
```

El modelo y sus trade-offs están en
[`06_3_modelo_fisico_redis.md`](docs/diseno/06_3_modelo_fisico_redis.md).

## Incremento 05 Cassandra

Cassandra conserva comentarios por partido y por usuario, aplica idempotencia,
moderación y paginación temporal, y se degrada sin bloquear el fixture:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_comentarios_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_cassandra.ps1
```

El modelo y la diferencia entre RF=1 local y RF=3 objetivo están en
[`06_4_modelo_fisico_cassandra.md`](docs/diseno/06_4_modelo_fisico_cassandra.md).

Ver el [plan de incorporación](docs/plan_incorporacion.md), el
[registro de los 17 puntos](docs/pendientes.md) y las
[fuentes inspeccionadas](docs/fuentes.md). Las tareas de usuarios, asistencias,
telemetría, simulación y carga están registradas en
[tareas posteriores a la integración](docs/tareas_integracion_final.md).

## Alcance de las verificaciones actuales

MongoDB fue ejecutado en el equipo del grupo con 64 equipos, 1.024 jugadores,
un partido, replica set PRIMARY e idempotencia de la carga. La API, Redis,
Prometheus y Grafana también fueron iniciados y verificados. Cassandra queda
como incremento implementado pendiente de ejecución en el equipo del grupo.
Todavía no se versionaron mediciones de capacidad, SLO ni convergencia completa.

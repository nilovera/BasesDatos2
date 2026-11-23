# Fixture 2030 — trabajo final

Integración final del trabajo de Ingeniería de Datos II dentro del repositorio
`nilovera/BasesDatos2`, rama `trabajo-final`.

**Estado:** base inicial, diseño físico de MongoDB, contrato HTTP y entorno
MongoDB reproducible en Docker. La ejecución en el equipo del grupo, la API, los
demás motores y el monitoreo deben completarse y validarse de manera integrada.

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
| `tests/` | Pruebas del catálogo, OpenAPI y esquema MongoDB | Ejecutadas |
| `docs/antecedentes/` | Siete documentos de diseño previos | Conservados como antecedentes |
| `docs/diseno/` | Convenciones y decisiones de la rama final | Base inicial documentada |
| `backend/` | Contrato OpenAPI del primer flujo vertical | Diseñado; servicio pendiente |
| `mongodb/` | Replica set de laboratorio, validadores, índices, carga y verificación | Implementado; ejecución en equipo pendiente |
| `infra/` | Docker y criterios de observabilidad | MongoDB incorporado; resto pendiente |

## Arquitectura objetivo

La solución final utiliza cinco motores con responsabilidades diferentes:

| Motor | Responsabilidad principal |
|---|---|
| MongoDB | Fuente oficial de equipos, jugadores, partidos, alineaciones y eventos deportivos |
| Cassandra | Comentarios, moderación y vistas de consulta por partido y por usuario |
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

1. Ejecutar y probar el esquema MongoDB en replica set local.
2. Implementar la API sobre el contrato sin dependencias de IRIS.
3. Incorporar Cassandra, Redis, InfluxDB y Neo4j mediante adaptadores revisados.
4. Integrar idempotencia, outbox, caché, comentarios, estadísticas y proyecciones.
5. Crear el entorno Docker reproducible.
6. Incorporar Prometheus, Grafana, alertas y evidencia de una falla controlada.
7. Ejecutar pruebas integradas, de carga y recuperación.
8. Preparar la demostración y defensa final.

Ver el [plan de incorporación](docs/plan_incorporacion.md), el
[registro de los 17 puntos](docs/pendientes.md) y las
[fuentes inspeccionadas](docs/fuentes.md). Las tareas de usuarios, asistencias,
telemetría, simulación y carga están registradas en
[tareas posteriores a la integración](docs/tareas_integracion_final.md).

## Alcance de las verificaciones actuales

Los controles de este commit se ejecutan sobre archivos y generación de datos.
No prueban todavía conexiones, persistencia, réplicas, capacidad, Docker,
observabilidad ni recuperación. Los resultados de hitos anteriores conservan su
fecha y entorno originales y no se presentan como evidencia de la integración
final.

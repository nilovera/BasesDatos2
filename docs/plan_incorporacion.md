# Plan de incorporación a `trabajo-final`

La rama final se crea limpia dentro de `nilovera/BasesDatos2`. No deriva de
`monitoreo` y no recibe merges completos de las ramas históricas. Cada pieza se
incorpora después de revisar identidad, configuración, dependencias y pruebas.

## Relación con el plan vigente

| Paso | Trabajo en `trabajo-final` | Estado inicial |
|---|---|---|
| 1-5 | Conservar alcance, patrones, comparación, arquitectura, diagramas y objetivos | Antecedentes incorporados |
| 6.1 | Identidad, tiempos, estados, autoridad del dato y catálogo común | Base inicial verificada |
| 6.2 | Diseño físico de MongoDB | Diseñado, ejecutado y verificado en replica set local de un miembro |
| 6.3-6.6 | Diseño físico de Redis, Cassandra, InfluxDB y Neo4j | Los cuatro diseños especializados están implementados; Neo4j pendiente de ejecución local |
| 7 | Escrituras, idempotencia, outbox, sincronización y fallos | Primer flujo transaccional implementado; consumidores pendientes |
| 8 | Revisión y recuperación selectiva de los hitos | Fuentes identificadas; incorporación pendiente |
| 9 | Implementación incremental y Docker integrado | Los cinco motores, API, Prometheus y Grafana están incorporados |
| 10 | Monitoreo, validación integrada, evidencia y defensa | API, cinco motores y Data Mart instrumentados; carga y defensa pendientes |

IRIS no recibe diseño físico ni contenedor. Su evaluación y exclusión se registran
en `docs/diseno/ADR-001-exclusion-iris.md`.

## Política para reutilizar código

Cada incorporación debe:

1. identificar la rama y el commit de origen;
2. recuperar solamente archivos necesarios;
3. eliminar credenciales y dependencias ajenas a la arquitectura final;
4. adaptar IDs, semillas, puertos y contratos comunes;
5. ejecutar pruebas específicas antes de confirmar el commit;
6. registrar limitaciones y evidencia obtenida.

La rama `monitoreo` es una fuente de diagnóstico, aislamiento de fallos y
métricas; no es la base de la rama final. La rama `InlfuxDB` no se utiliza.

## Incrementos previstos

1. **Base documental y catálogo:** contenido de este paquete.
2. **MongoDB reproducible:** equipos, jugadores, partidos, índices y replica set.
3. **API y observabilidad inicial:** eventos, transacción, outbox, Prometheus y Grafana.
4. **Redis:** sesiones, caché real, invalidación y control de concurrencia.
5. **Cassandra:** comentarios, moderación y paginación implementados; validar carga, shards y RF=3 fuera del laboratorio local.
6. **InfluxDB:** estadísticas, posiciones, cursores y mapas de calor implementados; ejecutar evidencia Docker.
7. **Neo4j:** carga idempotente, CRUD, recomendaciones y consultas multisalto implementadas; falta ejecución local.
8. **Data Mart:** estrella PostgreSQL, ETL idempotente y línea base del Hito 12.
9. **Integración:** consumidores Outbox y proyecciones idempotentes.
10. **Observabilidad y defensa:** carga, recuperación, evidencia, demo y guion de 20 minutos.

Después de integrar los cinco motores se ejecutarán las tareas T01-T06 de
`docs/tareas_integracion_final.md`: usuarios sintéticos, asistencias, telemetría,
simulador reproducible, escenarios de carga y SLI/SLO/SLA propuesto.

## Primer flujo de aceptación

El primer recorrido ejecutable será:

`proveedor simulado -> API -> MongoDB -> respuesta -> Outbox -> proyecciones`.

Debe permitir iniciar `PAR-0001`, registrar un gol, repetir el mismo request sin
duplicarlo, corregirlo, registrar una sustitución y consultar el resultado.

## Criterio de seguimiento

Cada punto de `docs/pendientes.md` debe terminar con una decisión, cambios
concretos y una prueba de aceptación. Diseñado, implementado, ejecutado y medido
son estados distintos. Las pruebas de catálogo de este commit no cierran la
validación del sistema distribuido.

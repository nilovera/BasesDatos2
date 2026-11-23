# Plan de incorporación a `trabajo-final`

La rama final se crea limpia dentro de `nilovera/BasesDatos2`. No deriva de
`monitoreo` y no recibe merges completos de las ramas históricas. Cada pieza se
incorpora después de revisar identidad, configuración, dependencias y pruebas.

## Relación con el plan vigente

| Paso | Trabajo en `trabajo-final` | Estado inicial |
|---|---|---|
| 1-5 | Conservar alcance, patrones, comparación, arquitectura, diagramas y objetivos | Antecedentes incorporados |
| 6.1 | Identidad, tiempos, estados, autoridad del dato y catálogo común | Base inicial verificada |
| 6.2-6.6 | Diseño físico de MongoDB, Cassandra, Redis, InfluxDB y Neo4j | Pendiente |
| 7 | Escrituras, idempotencia, outbox, sincronización y fallos | Pendiente |
| 8 | Revisión y recuperación selectiva de los hitos | Fuentes identificadas; incorporación pendiente |
| 9 | Implementación incremental y Docker integrado | Pendiente |
| 10 | Monitoreo, validación integrada, evidencia y defensa | Pendiente |

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
2. **MongoDB y API:** equipos, jugadores, partidos, alineaciones, eventos y outbox.
3. **Cassandra:** comentarios, moderación, paginación y convergencia de vistas.
4. **Redis:** sesiones, caché real, invalidación y control de concurrencia.
5. **InfluxDB:** estadísticas, posiciones, cursores y mapas de calor.
6. **Neo4j:** carga desde el catálogo y consultas multisalto justificadas.
7. **Docker integrado:** cinco motores, API, volúmenes, red, semillas y healthchecks.
8. **Observabilidad:** Prometheus, Grafana, exporters, alertas y prueba controlada.
9. **Validación y defensa:** carga, recuperación, evidencia, demo y guion de 20 minutos.

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

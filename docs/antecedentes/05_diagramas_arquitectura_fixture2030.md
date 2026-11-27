# Fixture 2030 — Diagramas de arquitectura

## Escritura oficial y entrega de proyecciones

```mermaid
flowchart TD
    API["API: comando deportivo"] --> TX["Transacción MongoDB"]
    TX --> D["Partido y evento"]
    TX --> O["Outbox deportiva"]
    TX --> A["Cola de auditoría"]
    O --> W["Worker Outbox"]
    W --> R["Redis"]
    R --> N["Neo4j"]
    A --> H["Relay de auditoría"]
    H --> C["Cassandra: historial"]
```

El recorrido Redis → Neo4j expresa el orden de llamadas del worker, no una
replicación entre esos motores. Ambos reciben información del mensaje Outbox.
El hecho deportivo es oficial desde la confirmación MongoDB; el estado
`PUBLICADO` se registra después de completar los dos destinos. El relay de
auditoría es independiente y pertenece al incremento 15.

## Datos sociales, telemetría y analítica

```mermaid
flowchart TD
    S["API y simulador"] --> C["Cassandra: comentarios y moderación"]
    S --> I["InfluxDB: posiciones y estadísticas"]
    C --> A["Auditoría de acciones sociales"]
    M["MongoDB: eventos efectivos"] --> E["Refresh ETL explícito"]
    I --> E
    E --> P["PostgreSQL: Data Mart"]
```

Los comentarios permanecen en Cassandra. La telemetría permanece en InfluxDB.
El Data Mart recibe hechos y resúmenes mediante refresh; no mueve las fuentes
ni convierte MongoDB en repositorio de todas las muestras. El simulador escribe
posiciones y pelota; las estadísticas de equipo y sus resúmenes tienen rutas
de ingesta/agregación propias.

## Observabilidad

```mermaid
flowchart TD
    P["Prometheus"] --> A["API y salud funcional"]
    P --> O["Métricas Outbox"]
    P --> R["Redis Exporter"]
    P --> I["InfluxDB: métricas directas"]
    P --> G["Grafana"]
    A --> M["Métricas nativas MongoDB mediante collector"]
```

Las flechas desde Prometheus representan recolección; Grafana consulta
Prometheus para visualizar las series. Prometheus también se recolecta a sí
mismo. Cassandra, Neo4j y Data Mart se observan funcionalmente desde la API;
no se afirma disponer de métricas internas completas de esos motores.

## Topología y fallas

Cada motor tiene una instancia local con persistencia por volumen. La parada
de un contenedor puede degradar su función mientras otra lectura continúa.
La recuperación observada consiste en reiniciar el componente y comprobar su
salud y la convergencia que corresponda.

Un despliegue redundante requeriría varias réplicas, dominios de falla
independientes, políticas de elección/failover y restauración probada. No se
dibuja esa topología como parte del entorno ejecutado. La configuración local
y los resultados registrados se detallan en
[arquitectura y consistencia](04_arquitectura_distribuida_cap_consistencia.md) y
[estado de validación](../estado_validacion.md).

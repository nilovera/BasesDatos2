# API y observabilidad de la integración

## Responsabilidad

FastAPI coordina contratos HTTP y servicios especializados. MongoDB confirma
el hecho deportivo; Cassandra conserva comentarios y auditoría; InfluxDB,
telemetría; Redis, temporales; Neo4j, recorridos; Data Mart, analítica batch.
El contrato de la API del incremento 15 tiene versión 0.10.0.

La escritura de eventos confirma agregado, hecho y Outbox en una transacción.
La entrega de auditoría oficial se agrega en esa misma transacción. Outbox
actualiza Redis y Neo4j de manera eventual. Los comentarios y la telemetría
no se presentan como copias oficiales del resultado deportivo.

## Salud y métricas

`/health` informa disponibilidad por dependencia y estado degradado cuando
corresponde. Una API viva puede no estar en condiciones de confirmar un evento.
Prometheus recolecta la API, el worker Outbox, Redis Exporter, InfluxDB y sus
propias métricas. MongoDB también aporta métricas nativas mediante un collector
de la API que consulta `serverStatus` y `dbStats`.

Grafana utiliza provisioning versionado. El panel vigente prioriza API y los
cinco motores operacionales; las métricas de Outbox y Data Mart continúan
disponibles aunque no todas tengan un panel visible. El dashboard usa
Prometheus; no se afirma que consulte directamente InfluxDB.

Los indicadores incluyen latencia, errores, volumen, operaciones de dominio,
disponibilidad y convergencia. La latencia de Prometheus es una estimación del
histograma en una ventana; los percentiles del generador de carga se calculan
sobre sus solicitudes. No son muestras intercambiables.

## Logs y auditoría

El incremento 15 añade logs HTTP estructurados y un historial de acciones
confirmadas por actor/recurso y día. Los rechazos quedan en los logs técnicos;
no se atribuye a la auditoría una cobertura universal de accesos o fallos.
Las sesiones siguen siendo de laboratorio, con consulta de historial limitada
a una sesión ADMIN de ese entorno.

## Evidencia y límites

La plataforma posee verificaciones Docker, fallas controladas y pruebas de
lectura. Humo y normal cumplieron sus SLO locales; estrés alcanzó 79,932 req/s.
La auditoría tiene pruebas unitarias y una ejecución HTTP real con resultado OK.
Los logs técnicos HTTP se observan en Docker; el historial de acciones se
consulta en Cassandra. Son registros con finalidades y almacenamiento diferentes.
Ver [estado de validación](../estado_validacion.md).

La API usa una instancia local. Los puertos se publican en loopback; no hay
autenticación MongoDB de producción ni TLS en esta configuración. La validación
manual de participación no reconstruye todos los intervalos históricos. Estos
límites no se confunden con ausencia de ejecución de la integración existente.

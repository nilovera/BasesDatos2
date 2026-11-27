# Fixture 2030 — Plan de integración y control

## Propósito

Fixture2030 integra modelos de persistencia especializados para administrar un
catálogo deportivo, registrar partidos, mostrar información en vivo y consultar
relaciones y resultados analíticos. La integración busca justificar cada motor
por su patrón de acceso y conservar una autoridad explícita para cada dato.

La rama `trabajo-final` constituye la implementación integrada. Las ramas de los
hitos son fuentes de procedencia, no componentes que deban fusionarse completos.
Esta decisión evita heredar catálogos incompatibles, credenciales y estados de
demostración que no pertenecen al escenario común.

## Decisiones consolidadas

| Decisión | Fundamento | Consecuencia |
|---|---|---|
| MongoDB confirma el hecho deportivo | Evento, versión del partido y entrega deben concordar | Transacción local y Outbox |
| Cassandra conserva comentarios y auditoría | Historial de escrituras y lecturas por claves conocidas | Vistas por consulta y particiones acotadas |
| Redis mantiene temporales | Caché, sesiones y marcador requieren acceso por clave | TTL, límite de memoria y recuperación desde la autoridad cuando corresponde |
| InfluxDB conserva telemetría | Las consultas recorren tiempo y ventanas | Series, retención y agregaciones |
| Neo4j resuelve recorridos | Rivalidades y recomendaciones dependen de vínculos | Catálogo y proyección de eventos identificables |
| Data Mart separa analítica | Las consultas agregadas tienen otro grano y ritmo de actualización | ETL explícito hacia PostgreSQL |
| IRIS queda excluido | Su responsabilidad se superponía con el núcleo documental | Menos autoridades y rutas de sincronización |

## Integración realizada

1. Catálogo común reproducible: 64 equipos y 1.024 jugadores, con IDs estables.
2. Diseño físico, validadores, índices y esquemas específicos por motor.
3. Contrato HTTP, transacción deportiva y reintentos idempotentes.
4. Proyección mediante Outbox hacia Redis y Neo4j.
5. Comentarios, telemetría, recorridos y ETL accesibles desde la API.
6. Observabilidad con Prometheus, Grafana, reglas y pruebas de falla controlada.
7. Perfiles de lectura, comparación del Data Mart y simulación reproducible.
8. Extensión de auditoría por actor/recurso y día, con validación unitaria y prueba HTTP integrada propia.

Los puntos anteriores no tienen el mismo nivel de evidencia. El núcleo integrado
posee ejecuciones Docker registradas; la auditoría también cuenta con resultado
HTTP integrado OK, además de sus pruebas unitarias. El
[registro de validación](../estado_validacion.md) establece esa diferencia.

## Criterios de control

- Cada dato tiene un propietario y las copias derivadas indican su fuente.
- Los IDs y contratos se comparten entre motores; no se mezclan alias sin equivalencia.
- Una respuesta de éxito requiere la confirmación del almacenamiento responsable.
- El replay no crea un segundo hecho ni vuelve a aplicar una moderación antigua.
- Las mediciones identifican commit, escenario, solicitudes, latencia y errores.
- Los contenedores de un solo nodo no se describen como un clúster de alta disponibilidad.
- Los perfiles de lectura no se utilizan para acreditar capacidad de escritura.

## Alcance de la continuidad del proyecto

La operación local, la evidencia integrada y el front ya forman parte del
proyecto. Las extensiones reales son autenticación y autorización de producción,
perfiles persistentes de usuarios, validación histórica completa de participación,
despliegue redundante, restauración de backups y pruebas de volumen representativo.
No constituyen pasos necesarios para reconocer las ejecuciones ya registradas.

Cada cambio posterior debe actualizar contrato, diseño y evidencia afectada.
La validación previa se conserva con su versión de origen, sin atribuirla a
código que todavía no fue ejecutado en ese mismo escenario.

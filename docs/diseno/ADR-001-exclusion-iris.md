# ADR-001 — Exclusión de InterSystems IRIS

- **Estado:** aceptada
- **Alcance:** arquitectura ejecutable de la rama `trabajo-final`
- **Decisión:** utilizar MongoDB, Cassandra, Redis, InfluxDB y Neo4j; no desplegar IRIS

## Contexto

Los hitos anteriores utilizaron IRIS para parte de partidos, eventos y árbitros,
mientras MongoDB y otros motores también almacenaban o proyectaban información
del núcleo deportivo. Al integrar los hitos aparecieron dos riesgos: más de una
fuente potencial para el mismo hecho y contratos incompatibles para IDs, estados,
fechas y partidos.

La arquitectura final necesita que cada motor responda a un patrón de acceso
diferente y que el equipo pueda desplegar, monitorear, explicar y recuperar el
sistema completo en un entorno de laboratorio.

## Alternativas consideradas

### A. Mantener IRIS como fuente de partidos y eventos

Se descartó porque competiría con MongoDB por la autoridad del núcleo deportivo.
Resolverlo exigiría coordinación adicional, reglas de precedencia y recuperación
de divergencias sin aportar una consulta exclusiva.

### B. Mantener IRIS como réplica o proyección

Se descartó porque agrega otro adaptador, sincronización, contenedor, monitoreo y
procedimiento de recuperación. Una réplica sin un patrón de acceso diferencial
duplica el costo operativo y la superficie de falla.

### C. Excluir IRIS y reasignar sus responsabilidades

Es la alternativa elegida. Reduce ambigüedad sobre la fuente oficial y permite
concentrar la evidencia en cinco modelos con responsabilidades no equivalentes.

## Decisión y reasignación

| Responsabilidad histórica o posible | Destino final | Motivo |
|---|---|---|
| Partidos, eventos, árbitros y estado oficial | MongoDB | Agregados documentales y escrituras transaccionales del núcleo deportivo |
| Resultado y estado de consulta frecuente | Redis | Copia temporal reconstruible; baja latencia |
| Comentarios, moderación y auditoría | Cassandra | Escrituras distribuidas y consultas definidas por partición |
| Estadísticas y posiciones por tiempo | InfluxDB | Series temporales, ventanas y agregaciones |
| Relaciones entre jugadores, equipos y partidos | Neo4j | Recorridos y consultas multisalto |

MongoDB es la única autoridad del hecho deportivo. Redis y Neo4j mantienen
vistas derivadas; InfluxDB conserva telemetría sintética ingresada por su
flujo propio, sin una copia exhaustiva en MongoDB. Cassandra es autoridad de
comentarios y del historial de auditoría. El Data Mart PostgreSQL es un destino
analítico separado, no otra autoridad deportiva.

## Fundamentos

La exclusión no implica que IRIS sea técnicamente incapaz. La decisión se basa en:

- superposición funcional con MongoDB para el agregado deportivo;
- ausencia de un patrón de acceso del Fixture que requiera IRIS de forma exclusiva;
- riesgo de dos fuentes de verdad para partidos y eventos;
- mayor cantidad de contratos, credenciales, fallas y sincronizaciones;
- costo adicional de despliegue, monitoreo y explicación en el laboratorio;
- posibilidad de cubrir los requisitos con cinco modelos ya diferenciados.

## Consecuencias positivas

- una única fuente oficial para eventos deportivos;
- menos rutas de sincronización y recuperación;
- entorno Docker y monitoreo más acotados;
- responsabilidades más claras para la defensa;
- eliminación de estados y datos contradictorios entre IRIS y MongoDB.

## Costos y riesgos aceptados

- se pierde la demostración específica del modelo de IRIS;
- la API histórica no puede reutilizarse sin remover su adaptador y configuración;
- datos históricos de IRIS requieren migración explícita si se desean conservar;
- la decisión debe defenderse como un trade-off, no como una superioridad absoluta.

## Controles de implementación

La exclusión se considera aplicada cuando:

1. Docker Compose no define servicios, volúmenes ni secretos de IRIS;
2. la API no importa ni inicializa adaptadores de IRIS;
3. healthchecks, métricas y documentación no declaran IRIS como componente activo;
4. partidos y eventos se recuperan desde MongoDB;
5. no quedan variables de entorno ni rutas ejecutables que apunten a IRIS;
6. las pruebas integradas funcionan con los cinco motores definidos;
7. la documentación explica beneficios, costos y responsabilidades reasignadas.

La implementación y las ejecuciones se relacionan en el
[estado de validación](../estado_validacion.md); este registro no acredita una
exposición oral ni una aprobación externa.

## Revisión futura

La decisión podría revisarse si aparece un requisito que IRIS resuelva de manera
claramente diferencial y medible. Cualquier reincorporación deberá definir
autoridad del dato, patrón de acceso, consistencia, recuperación, monitoreo y
evidencia comparativa antes de agregar el motor al entorno.

# Registro de trazabilidad de los 17 puntos de revisión

Actualización: 27 de noviembre de 2026. Se conserva la identificación H01–H17
para permitir el seguimiento de decisiones anteriores. La columna de límites
describe el alcance real; no reabre ejecuciones que ya poseen resultados.
Evidencia de referencia: [estado de validación](estado_validacion.md).

| ID | Tema | Resolución vigente | Límite o comprobación adicional |
|---|---|---|---|
| H01 | Identidad de equipos | IDs comunes en el catálogo y las integraciones; ARG/EQ-01 y MEX/EQ-33 explícitos | No extender equivalencias de alias sin una fuente validada |
| H02 | Jugadores | MongoDB y Neo4j verifican el catálogo de 1.024 jugadores; MongoDB registra cero huérfanos | Los conteos no sustituyen una comparación exhaustiva de todos los atributos proyectados |
| H03 | Partidos | PAR-0001 representa el escenario sintético común; nuevas simulaciones crean otros IDs | No importar la agenda histórica como fixture oficial |
| H04 | IRIS | Excluido de código ejecutable, Compose y monitoreo; controlado por pruebas | Cualquier reincorporación requiere una responsabilidad diferenciada |
| H05 | Base de integración | Diagnóstico, aislamiento y métricas incorporados selectivamente | Las ramas históricas conservan su propia procedencia |
| H06 | Neo4j | Módulo nuevo con restricciones, MERGE, consultas y ejecución Docker registrada | La idempotencia de carga no equivale a una prueba exhaustiva de reconciliación de cambios |
| H07 | Semillas MongoDB | Carga idempotente; el bootstrap no reinicia el partido operativo | Respaldar datos antes de una migración de esquema |
| H08 | Eventos oficiales | Una autoridad MongoDB; Outbox proyecta Redis y Neo4j; replay y convergencia registrados | No existe una barrera estricta de orden de todas las proyecciones por partido |
| H09 | Cassandra y distribución | Publicación, lecturas y moderación integradas; lectura mixta y falla registradas | No hay comparación representativa de escritura con 4, 8 y 16 shards ni RF=3 |
| H10 | Escrituras API | Inicio, goles, tarjetas, VAR, correcciones, sustituciones y comentarios implementados | Perfiles durables y autenticación de producción son extensiones |
| H11 | Moderación y auditoría | Visibilidad implementada; incremento 15 conserva historial por actor/recurso | Auditoría con prueba HTTP integrada OK; control ADMIN basado en sesiones de laboratorio, sin autenticación productiva |
| H12 | Vistas de comentarios | Batch logged acotado e idempotencia; prueba unitaria de recuperación del nuevo historial | Sin worker general de reparación de todas las vistas ni aislamiento entre particiones |
| H13 | Caché real | Cache-Aside, persistencia, bypass y replay de proyección con evidencia Docker | Standalone; LFU puede expulsar temporales antes del TTL |
| H14 | Participación y mapas | Nuevas simulaciones generan alineaciones y sustituciones; front y mapas verificados | La entrada manual valida plantel/equipo, sin reconstrucción histórica completa por instante |
| H15 | Paginación temporal | Cursor compuesto implementado y validado unitariamente; telemetría integrada operativa | La muestra de una simulación no demuestra recorrido exhaustivo de todo cursor a gran volumen |
| H16 | Contratos y almacenamiento | Vocabulario compartido, validadores y pruebas de contratos | Toda ampliación debe actualizar OpenAPI, modelos y esquema afectado |
| H17 | Entorno distribuido | Motores y observabilidad ejecutados en una red Docker con volúmenes | RF=1 y nodos únicos; sin demostración de alta disponibilidad o failover regional |

La nueva auditoría mantiene su procedimiento de integración en
`scripts/probar_auditoria.ps1`. Las limitaciones de producción y de escala no se
confunden con ausencia de ejecución Docker de la plataforma existente.

# Integración final: resultados y extensiones

Revisión: 27 de noviembre de 2026. Los identificadores T01–T09 conservan la
trazabilidad del plan. Los resultados se enlazan en el
[estado de validación](estado_validacion.md).

| ID | Área | Resultado vigente | Extensión delimitada |
|---|---|---|---|
| T01 | Usuarios sintéticos | Sesiones Redis y autores sintéticos disponibles | Perfiles durables, credenciales verificadas y autorización de producción no implementados |
| T02 | Asistencias | Contrato opcional, validación básica y relación ASISTIO en Neo4j implementados | Validación histórica de participación en comandos manuales; no se afirma escritura automática de estadísticas InfluxDB por cada gol |
| T03 | Telemetría | Lotes, cursor compuesto, posiciones y mapas de calor implementados; muestras integradas verificadas | Control histórico de participación en cargas manuales y escala de ingesta |
| T04 | Simulador y front | Partido completo y respuestas del front verificados; 17 eventos y marcador final 1–2 en la ejecución registrada | Una instancia local; el control de ejecución no equivale a orquestación distribuida |
| T05 | Escenarios de carga | Humo, normal, estrés y recuperación ejecutados con semillas 2029, 2030 y 2031 según perfil | Escrituras masivas, 10M+ puntos y búsqueda del punto de saturación no acreditados |
| T06 | SLI, SLO y SLA | Latencia, errores y throughput medidos; humo y normal cumplen objetivos locales | Sin SLA contractual ni disponibilidad anual medida |
| T07 | Evidencia | Verificaciones Docker, fallas de los motores y Outbox, carga, simulación y front registradas | La captura HTTP del front no sustituye una validación visual de todas las pantallas |
| T08 | Data Mart | Comparaciones sin/con pool y consultas bajo carga mixta ejecutadas | Volumen representativo, comparación repetida controlada y reconciliación de cambios históricos |
| T09 | Outbox | Lease, reintentos, deduplicación Redis y proyección Neo4j; convergencia registrada | Sin garantía de orden causal estricto por partido para todas las proyecciones |

## Auditoría incorporada en el incremento 15

El historial de acciones se conserva en Cassandra. Las escrituras oficiales
agregan su entrega durable en la transacción MongoDB. Comentarios y moderación
incluyen el registro en un batch acotado. La validación local comprende 170
pruebas, incluidas 25 específicas de auditoría. La comprobación HTTP integrada
se ejecutó en Docker con resultado OK el 27 de noviembre de 2026. El
[resultado original](../evidencia/ejecuciones/auditoria-20261127T040527Z/resultado.json)
confirma historial, cero duplicados, acceso restringido y entrega de la creación
de una simulación a Cassandra. El procedimiento permanece disponible para
reproducir ese escenario.

## Criterios para nuevas mediciones

Las pruebas posteriores deben indicar commit, escenario, semilla, duración,
mezcla, datos iniciales, tasa lograda, errores y percentiles. La capacidad de
escritura debe medirse con confirmación durable, distribución sesgada y
reintentos. La capacidad analítica debe compararse con resultados equivalentes,
frescura explícita y suficiente volumen. La recuperación debe distinguir
reinicio con volumen conservado de restauración ante pérdida de almacenamiento.

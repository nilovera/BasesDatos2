# Revisión documental del incremento 15

Revisión: 27 de noviembre de 2026. Base inspeccionada:
`f4cb9be15f996d2710b41c36b18b09eed7e07da2`, rama `trabajo-final`.

## Alcance y fundamento

Se revisaron los Markdown del proyecto frente al código, esquemas, configuración
y registros de ejecución. Se actualizaron fundamentación, alcance, diseños,
seguimiento y monitoreo para distinguir implementación, ejecución, medición y
extensiones. Las instrucciones históricas de aplicación se conservan con su
propósito original. Los resultados de las ejecuciones existentes no se modifican.

## Correcciones principales

| Área | Corrección y justificación |
|---|---|
| Estados | Redis, Cassandra, Neo4j y Data Mart tienen registros Docker; se reemplazan los estados desactualizados por resultados trazables |
| Marco teórico | Selección por patrón de acceso, propiedad del dato, CAP, consistencia, particionado y replicación vinculados a la configuración real |
| Autoridades | Comentarios en Cassandra y telemetría en InfluxDB; sin traslado automático de ambos a MongoDB |
| Outbox | Se documentan Redis y Neo4j como destinos y la ausencia de barrera estricta de orden por partido |
| Contratos | Idempotencia diferenciada por operación; clave y respuesta deportivas dentro del evento, no en una colección inexistente |
| Monitoreo | Collector nativo MongoDB, targets reales y alcance funcional de cada indicador |
| Rendimiento | Se conserva humo diagnóstico desfavorable, tasa efectiva de 79,932 req/s y SLO distintos de humo y normal |
| Data Mart | Comparaciones sin/con pool y carga mixta ya ejecutadas; sin atribución causal absoluta ni ventaja general de escala |
| Simulación | Conteos nominales separados de muestras verificadas; estadísticas de equipo y resúmenes no automáticos |
| Auditoría | Historial Cassandra y entrega transitoria MongoDB; validación unitaria y resultado HTTP integrado del 27 de noviembre registrados |
| Redacción | Texto formal, sin referencias conversacionales a docentes ni instrucciones personales usadas como fundamento técnico |

La revisión también explicita una limitación del ETL: el UPSERT de snapshots
no elimina automáticamente hechos que dejaron de estar presentes después de
una corrección. Se documenta para no confundir idempotencia con reconciliación
completa; esta revisión no cambia ese comportamiento del código.

## Controles

Se comprueban enlaces relativos contra el contenido del repositorio base y los
archivos nuevos, nombres de tablas y colecciones contra sus esquemas, cifras
contra los resultados conservados, ausencia de estados obsoletos y consistencia
de los límites. La regresión ejecuta la suite de 170 pruebas; el reporte se
incluye bajo `evidencia/ejecuciones/auditoria-unitarias-*`.

Un control documental de la suite se actualiza para comprobar el vínculo al
estado de validación en lugar de exigir la conclusión desactualizada de cierre.
La revisión adicional no modifica los servicios de ejecución de la auditoría.

## Documentos actualizados

- `INSTRUCCIONES_AUDITORIA_15.md`
- `README.md`
- `backend/README.md`
- `cassandra/README.md`
- `datamart/README.md`
- `docs/antecedentes/00_plan_maestro_fixture2030.md`
- `docs/antecedentes/02_patrones_acceso_y_requisitos_fixture2030.md`
- `docs/antecedentes/03_comparacion_motores_y_estrategia_cap.md`
- `docs/antecedentes/04_arquitectura_distribuida_cap_consistencia.md`
- `docs/antecedentes/05B_objetivos_capacidad_slo_rpo_rto_y_pruebas.md`
- `docs/antecedentes/05_diagramas_arquitectura_fixture2030.md`
- `docs/antecedentes/README.md`
- `docs/antecedentes/alcance_funcional_fixture2030.md`
- `docs/diseno/06_1_convenciones_comunes.md`
- `docs/diseno/06_2_modelo_fisico_mongodb.md`
- `docs/diseno/06_3_modelo_fisico_redis.md`
- `docs/diseno/06_4_modelo_fisico_cassandra.md`
- `docs/diseno/06_5_modelo_fisico_influxdb.md`
- `docs/diseno/06_6_modelo_fisico_neo4j.md`
- `docs/diseno/06_7_modelo_fisico_datamart.md`
- `docs/diseno/07_contratos_eventos_idempotencia_outbox.md`
- `docs/diseno/08_api_y_observabilidad_inicial.md`
- `docs/diseno/09_simulador_partido_reproducible.md`
- `docs/diseno/10_auditoria_actividad.md`
- `docs/diseno/ADR-001-exclusion-iris.md`
- `docs/estado_validacion.md`
- `docs/fuentes.md`
- `docs/monitoreo/alertas_y_umbrales.md`
- `docs/monitoreo/evidencia_y_limitaciones.md`
- `docs/monitoreo/inventario_componentes.md`
- `docs/monitoreo/matriz_cumplimiento_hito_13.md`
- `docs/monitoreo/metricas_y_consultas.md`
- `docs/pendientes.md`
- `docs/plan_incorporacion.md`
- `docs/rendimiento/hito_12_datamart.md`
- `docs/rendimiento/pruebas_carga_sla_slo.md`
- `docs/revision_documental_15.md`
- `docs/tareas_integracion_final.md`
- `evidencia/README.md`
- `influxdb/README.md`
- `infra/README.md`
- `mongodb/README.md`
- `neo4j/README.md`
- `redis/README.md`

El [cierre documental de auditoría](cierre_auditoria_16.md) incorpora la
ejecución HTTP real posterior a la revisión inicial y su procedencia.
La guía de consultas de demostración se revisó y conserva su procedimiento.
El [estado de validación](estado_validacion.md) reúne la trazabilidad de las
mediciones y las limitaciones que siguen aplicando.

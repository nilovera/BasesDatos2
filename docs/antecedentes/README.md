# Fundamentación y arquitectura de referencia

Esta carpeta conserva las rutas de los documentos de análisis del proyecto.
La revisión del 27 de noviembre de 2026 actualiza su contenido para presentar
una fundamentación coherente con la rama final y separar el laboratorio
implementado de las alternativas de distribución para producción.

| Documento | Propósito |
|---|---|
| [Plan maestro](00_plan_maestro_fixture2030.md) | Decisiones, integración y criterios de control |
| [Alcance funcional](alcance_funcional_fixture2030.md) | Funciones implementadas y extensiones delimitadas |
| [Patrones de acceso](02_patrones_acceso_y_requisitos_fixture2030.md) | Relación entre consultas, datos y requisitos |
| [Comparación de motores](03_comparacion_motores_y_estrategia_cap.md) | Justificación de la persistencia políglota |
| [Arquitectura distribuida](04_arquitectura_distribuida_cap_consistencia.md) | Consistencia, particionado, replicación y recuperación |
| [Diagramas](05_diagramas_arquitectura_fixture2030.md) | Flujos y fronteras de responsabilidad |
| [Capacidad y validación](05B_objetivos_capacidad_slo_rpo_rto_y_pruebas.md) | SLI, SLO, carga y límites de recuperación |

Las definiciones físicas están en [diseño](../diseno/06_1_convenciones_comunes.md).
Los resultados comprobados se centralizan en el
[estado de validación](../estado_validacion.md). Un diseño de réplica o una meta
de disponibilidad no se presenta como una configuración ejecutada.

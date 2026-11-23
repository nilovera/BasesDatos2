# Paso 6.1 — Convenciones comunes

Fecha: 20 de noviembre de 2026. Estado: definición inicial implementada en el catálogo; pendiente de propagación a motores y API.

## Identidad

| Entidad | Formato interno | Ejemplo | Situación |
|---|---|---|---|
| Equipo | EQ- y dos dígitos | EQ-01 | Conservado del Hito 4 |
| Jugador | JUG- y cuatro dígitos | JUG-0001 | Conservado del Hito 4 |
| Partido | PAR- y cuatro dígitos | PAR-0001 | Conservado; semántica unificada en el catálogo nuevo |
| Usuario | USR- y cuatro dígitos | USR-0001 | Propuesto para semillas; perfiles pendientes |
| Evento oficial | EVE- y seis dígitos | EVE-000001 | Nuevo espacio de demostración; migración de EVE-0001 pendiente |
| Comentario | UUID | UUID del comentario | Conservado; no se confunde con evento deportivo |
| Sesión | Identificador opaco | Por definir en contrato de sesiones | Las sesiones SES-* históricas son de laboratorio |

Los límites de estos formatos pertenecen al laboratorio, no representan una garantía de escala productiva. Un ID no se reasigna a una entidad diferente ni depende del nombre visible. El generador actual conserva el orden del Hito 4; agregar equipos debe hacerse sin reordenar IDs existentes.

Los códigos ARG y MEX son aliases externos, no IDs de persistencia. El catálogo incorpora únicamente las dos equivalencias utilizadas en la demostración. No se infiere un ID a partir de un nombre ni se inventa el resto del mapeo.

## Autoridad del dato

MongoDB será la fuente oficial de equipos, jugadores y núcleo deportivo. Redis mantiene sesiones temporales y copias calientes. Cassandra conserva comentarios y la auditoría consultable diseñada. InfluxDB conserva las series temporales. Neo4j se incorpora como proyección si su uso y obligatoriedad se justifican.

El catálogo JSON es la fuente común de las semillas del laboratorio, no una segunda fuente de verdad productiva. Las proyecciones se reconstruirán desde la fuente y mecanismos de sincronización acordados.

## Partido de demostración y decisión de migración

PAR-0001 representa Argentina (EQ-01) contra México (EQ-33), con inicio programado 2030-06-13T20:00:00Z. Se elige esta pareja para conservar el caso temporal de InfluxDB y establecer una única referencia en la rama final. Los datos contradictorios de implementaciones históricas no se importan.

El antecedente Neo4j usa PAR-0001 para Argentina–Países Bajos (EQ-17). Ese significado histórico se conserva en el repo anterior y debe migrarse explícitamente antes de reutilizar sus eventos. No se copian goles de minuto 17 o 23 como si fueran un único registro oficial.

El partido comienza PROGRAMADO y sin eventos. El listado actual es una demostración, no un torneo completo ni el calendario real del Mundial.

## Fechas y estados

- Transporte JSON: ISO 8601 en UTC con Z.
- Persistencia: tipo temporal nativo de cada motor; conversión explícita en el adaptador.
- Fecha de nacimiento: el catálogo conserva medianoche UTC para reproducir MongoDB; la respuesta de la API podrá exponer una fecha civil.
- Estados comunes: PROGRAMADO, EN_CURSO, SUSPENDIDO, FINALIZADO, CANCELADO.
- Los estados de fuentes históricas se normalizan al vocabulario común; no se copian estados libres ni dependencias de IRIS.
- Tiempo deportivo (período/minuto/segundo), hora del proveedor y hora de recepción son conceptos diferentes. Su contrato queda en el paso 7.
- Buckets de comentarios: se calculan desde el timestamp UTC del comentario. La semilla histórica con datos comienza en 203006132000.

## Referencias e idempotencia

Cada jugador refiere a un equipo existente. Cada partido refiere a dos equipos distintos. Los eventos deben referir a un partido existente.

Identidad del evento, secuencia por recurso, versión y clave idempotente se completarán en el paso 7. El ID del evento y el request ID no son intercambiables. Tener datos generados de forma reproducible no demuestra idempotencia de escrituras de la API.

## Estado de cierre

Implementado y verificado: catálogo reproducible, correspondencias usadas, IDs, referencias, equipos distintos, fechas UTC y vocabulario de estados.

Pendiente: catálogo final de partidos, validación académica de volúmenes, contrato completo de eventos, perfiles/sesiones, migraciones y propagación de reglas a los cinco motores.


# Cierre documental de la validación de auditoría

La ejecución `auditoria-20261127T040527Z` terminó en OK el 27 de noviembre de
2026, a las 04:05:31 UTC (01:05:31 de Argentina), con HTTP y motores reales
del laboratorio Docker. Se incorpora su resultado a los estados del proyecto.

| Comprobación | Resultado |
|---|---|
| Historial del comentario | Tres acciones: publicación, ocultamiento y restauración |
| Idempotencia | Cero duplicados; replay de publicación y de moderación comprobados |
| Orden de moderaciones | El replay de un ocultamiento anterior no revierte la restauración |
| Consultas | Vistas por actor/recurso y paginación verificadas |
| Acceso | Sesión ADMIN de laboratorio y rechazo público HTTP 403 |
| Entrega oficial | Creación de simulación enviada de MongoDB a Cassandra |

El [resultado original](../evidencia/ejecuciones/auditoria-20261127T040527Z/resultado.json)
se conserva byte por byte. La
[procedencia complementaria](../evidencia/ejecuciones/auditoria-20261127T040527Z/procedencia.json)
registra su hash, la transcripción de referencia y la limitación del SHA no
capturado al ejecutar el script original. Los hashes posteriores no se presentan
como una captura de un commit limpio realizada durante la prueba.

Se actualizan README, diseño, alcance, seguimiento y monitoreo para retirar
el estado anterior de comprobación integrada sin ejecutar. Las 170 pruebas
unitarias y de regresión, incluidas 25 específicas de auditoría, mantienen su
evidencia separada. La validación funcional no mide capacidad, replicación,
RPO/RTO ni todas las acciones posibles del sistema.

Los logs técnicos HTTP se observan en Docker. Cassandra conserva el historial
de acciones confirmadas. La actualización documental no modifica servicios,
tablas, datos de negocio ni contenedores, y no requiere reconstruir la API.

El [estado de validación](estado_validacion.md) resume los resultados vigentes.

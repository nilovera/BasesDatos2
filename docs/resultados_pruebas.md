# Resultados de pruebas - Hito 9

| Prueba | Resultado observado | Estado |
|---|---|---|
| Ambiente IRIS Community | Contenedor iniciado en estado `healthy` | Correcto |
| Compilación | Cinco clases y sus tablas SQL compiladas sin errores | Correcto |
| Herencia | `Arbitro` heredó las propiedades persistentes de `Persona` | Correcto |
| Guardado padre-hijo | Un `%Save()` sobre `Partido` persistió un evento subordinado | Correcto |
| Proyección SQL | SQL recuperó `PAR-0001` y el evento del minuto 23 | Correcto |
| Navegación | `%OpenId()` y `GetAt(1)` permitieron navegar sin `JOIN` | Correcto |
| Transición ilegal | Un partido finalizado no volvió a `EnCurso` | Rechazada correctamente |
| Evento posterior | No se agregó un evento a un partido finalizado | Rechazado correctamente |
| Propiedad requerida | Un técnico sin `Nombre` no recibió ID | Rechazado correctamente |
| Equipos iguales | Un partido `ARG` contra `ARG` no recibió ID | Rechazado correctamente |
| Persistencia durable | `PAR-0001`, su evento y árbitro sobrevivieron al reinicio | Correcto |

Las pruebas utilizan un volumen reducido y validan comportamiento e integridad. No representan una medición de rendimiento productivo.

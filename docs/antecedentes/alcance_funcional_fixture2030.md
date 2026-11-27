# Fixture 2030 — Alcance funcional

## Propósito y datos

La plataforma permite consultar un catálogo de selecciones y jugadores,
reproducir partidos sintéticos y observar eventos, comentarios, posiciones,
relaciones y resultados analíticos. El catálogo contiene 64 equipos y 1.024
jugadores con identificadores internos comunes. La agenda y las muestras de
juego son datos de laboratorio; no constituyen un fixture oficial ni datos
capturados de un encuentro real.

## Funciones implementadas

| Función | Comportamiento | Almacenamiento responsable |
|---|---|---|
| Catálogo | Consultar equipos y planteles con referencias consistentes | MongoDB |
| Partidos y cruces | Consultar agenda sintética y preparar nuevos encuentros | MongoDB |
| Simulación | Crear, iniciar, pausar, reanudar y cambiar velocidad | MongoDB y worker de simulación |
| Eventos | Registrar inicio, goles, tarjetas, sustituciones, VAR, fin y correcciones | MongoDB |
| Marcador | Mostrar estado oficial y una vista caliente cuando está convergida | MongoDB y Redis |
| Comentarios | Publicar, listar por partido/usuario y moderar visibilidad | Cassandra |
| Sesiones | Crear, consultar y revocar sesiones con TTL | Redis |
| Telemetría | Ingresar y consultar posiciones, pelota, estadísticas y mapas de calor | InfluxDB |
| Relaciones | Consultar rivales, recomendaciones, caminos y relaciones deportivas | Neo4j |
| Analítica | Ejecutar refresh y consultar hechos agregados | Data Mart PostgreSQL |
| Observabilidad | Salud, métricas, paneles y alertas de dependencias | API, Prometheus y Grafana |
| Auditoría, incremento 15 | Consultar acciones confirmadas por actor o recurso y día | Cassandra; cola transitoria MongoDB para acciones oficiales |

La existencia de un endpoint no implica que tenga un control visible en el
front. La auditoría se consulta por Swagger o HTTP y no agrega una pantalla.
Las estadísticas y resúmenes tienen rutas de carga propias; la simulación
actual genera posiciones de jugadores y pelota, sin poblar automáticamente
todas las estadísticas de equipo o las ventanas de 15 minutos.

## Reglas del núcleo deportivo

Cada partido tiene identidad, estado, versión y secuencia de eventos. Un evento
debe respetar su contrato y el estado permitido. La transacción conserva el
hecho y las entregas necesarias. Un reintento con igual clave y contenido
devuelve el resultado original; reutilizar la clave con otro contenido genera
conflicto. Una corrección conserva el evento original y registra otro hecho.

El simulador mantiene su alineación, realiza sustituciones y genera posiciones
para los participantes correspondientes. La validación manual no reconstruye
toda la participación histórica por instante. La proyección del grafo tampoco
se considera una reconstrucción completa de todas las correcciones deportivas.

## Identidades y auditoría

Las sesiones son de laboratorio: el cliente puede elegir usuario y rol al
crearlas. No existe autenticación de producción ni un perfil durable de usuario
con credenciales verificadas. El historial distingue sesión de laboratorio,
autor declarado, solicitud anónima y servicio interno para evitar atribuciones
que la aplicación no puede demostrar.

La auditoría registra publicación/moderación de comentarios, registro/corrección
de eventos y controles de simulación. No registra retrospectivamente operaciones
anteriores ni cada lectura o muestra de telemetría. Los rechazos HTTP se
observan en logs técnicos; el historial de acciones confirmadas no sustituye
un registro de seguridad de todos los intentos.

## Flujos principales

Antes del encuentro se consulta el catálogo y se prepara el partido. Durante
la simulación, los eventos oficiales se confirman en MongoDB y Outbox actualiza
Redis y Neo4j. Los comentarios ingresan en Cassandra y las posiciones en
InfluxDB. El front consulta estas funciones mediante la API. Tras el partido,
los hechos permanecen consultables y el refresh del Data Mart actualiza sus
proyecciones analíticas.

Ante una dependencia caída se informa la función degradada. Una lectura oficial
puede continuar si MongoDB está operativo; no se promete que todo el simulador
avance durante una falla de sus escrituras remotas.

## Límites y extensiones

No se incluyen entrega multimedia, autenticación de producción, perfiles
persistentes de usuarios, proveedor deportivo real, fixture oficial completo,
alta disponibilidad multirregión ni restauración integral de backups probada.
Los mecanismos de contadores/ranking Redis no equivalen a un producto completo
de clasificación con todas las reglas de negocio de un torneo real.

Las funciones previas al incremento 15 tienen registros Docker, carga y
simulación. La auditoría tiene pruebas unitarias y una ejecución HTTP integrada
con resultado OK. La correspondencia exacta se encuentra en el
[estado de validación](../estado_validacion.md).

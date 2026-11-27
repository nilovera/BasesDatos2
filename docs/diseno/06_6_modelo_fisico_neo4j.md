# 6.6 Modelo físico de Neo4j

## Propósito y origen

Neo4j resuelve consultas basadas en recorridos: rivales de un equipo,
recomendaciones por posición y confederación, caminos entre equipos y relaciones
de eventos deportivos. Comparte IDs con MongoDB y no confirma el hecho deportivo.
El catálogo se carga desde las fuentes comunes; no se importan volúmenes ni
credenciales de las ramas históricas.

## Nodos y relaciones

El catálogo contiene `Equipo`, `Jugador`, `Partido`, `Confederacion` y `Torneo`.
Los vínculos incluyen `PERTENECE_A`, `MIEMBRO_DE`, `PARTICIPA_EN`, `LOCAL_EN` y
`VISITANTE_EN`. La captura base verificó 64 equipos, 1.024 jugadores, un partido,
seis confederaciones y 1.097 relaciones. Las simulaciones agregan hechos y
relaciones, por lo que ese total no es una constante del sistema operativo.

La proyección oficial incorpora `EventoOficial` y `OCURRIO_EN`, además de
`ANOTO`, `ASISTIO`, `RECIBIO_TARJETA`, `TUVO_GOL_ANULADO` y `ENTRO_POR` según el
tipo y los participantes del evento. Los `MERGE` se identifican por evento y
las restricciones del catálogo protegen sus IDs.

## Actualización y consultas

Outbox entrega el evento después de confirmar MongoDB. El worker procesa
Redis y Neo4j antes de marcar el mensaje publicado. Si se repite una entrega,
el uso de identidad estable evita crear otro hecho lógico. Una actualización
arbitraria de atributos MongoDB no modifica automáticamente el catálogo Neo4j;
requiere ejecutar el procedimiento de carga/proyección correspondiente.

Las recomendaciones actuales filtran misma posición y confederación y ordenan
por diferencia de ranking. No constituyen un modelo predictivo. Los caminos
usan vínculos acotados; no se utiliza Graph Data Science. El grafo no constituye
una reconstrucción completa de todas las correcciones ni garantiza orden
estricto de las proyecciones: el resultado oficial se obtiene de MongoDB.

## Despliegue y evidencia

Se utiliza `neo4j:5.26.34-community-trixie`, credencial por archivo y volúmenes
persistentes. La plataforma tiene ejecución Docker, consultas de salud, falla
controlada y verificación de relaciones deportivas en la simulación integrada.
El monitoreo registra salud Bolt y operaciones de API, sin exporter de todas
las métricas internas del proceso.

Community de un nodo no acredita alta disponibilidad ni failover. Los scripts
de carga idempotente y CRUD se mantienen como procedimientos reproducibles;
su disponibilidad no equivale a una prueba independiente de cada escenario
de reconciliación. Evidencia: [estado de validación](../estado_validacion.md).

// Equipos ordenados por ranking dentro de una confederacion.
MATCH (e:Equipo)-[:MIEMBRO_DE]->(c:Confederacion {id: 'CONMEBOL'})
RETURN e.id AS equipoId, e.nombre AS equipo, e.ranking AS ranking
ORDER BY ranking ASC;

// Rival de Argentina en los partidos oficiales cargados.
MATCH (equipo:Equipo {id: 'EQ-01'})-[:LOCAL_EN|VISITANTE_EN]->(p:Partido)
MATCH (rival:Equipo)-[:LOCAL_EN|VISITANTE_EN]->(p)
WHERE rival <> equipo
RETURN p.id AS partidoId, rival.id AS rivalId, rival.nombre AS rival,
       p.inicioProgramado AS inicioProgramado
ORDER BY inicioProgramado;

// Recomendaciones de jugadores mediante un recorrido de cuatro saltos.
MATCH (origen:Jugador {id: 'JUG-0001'})-[:PERTENECE_A]->(equipo:Equipo)
      -[:MIEMBRO_DE]->(conf:Confederacion)<-[:MIEMBRO_DE]-(otroEquipo:Equipo)
      <-[:PERTENECE_A]-(candidato:Jugador)
WHERE candidato.posicion = origen.posicion AND candidato <> origen
RETURN candidato.id AS jugadorId, candidato.nombre AS jugador,
       otroEquipo.id AS equipoId, otroEquipo.nombre AS equipo,
       abs(otroEquipo.ranking - equipo.ranking) AS diferenciaRanking
ORDER BY diferenciaRanking, jugadorId
LIMIT 10;

// Camino entre equipos de confederaciones distintas a traves del torneo.
MATCH (origen:Equipo {id: 'EQ-01'}), (destino:Equipo {id: 'EQ-33'})
MATCH camino = shortestPath(
  (origen)-[:MIEMBRO_DE|PARTICIPA_EN*..4]-(destino)
)
RETURN camino;

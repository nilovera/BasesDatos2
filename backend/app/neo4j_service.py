from neo4j.exceptions import Neo4jError, ServiceUnavailable, SessionExpired

from .errors import DomainError


GRAPH_ERRORS = (Neo4jError, ServiceUnavailable, SessionExpired, OSError)


class Neo4jGraphService:
    def __init__(self, client):
        self.client = client

    def health(self):
        return self.client.health()

    def _all(self, query, parameters=None):
        try:
            return self.client.query_all(query, parameters)
        except GRAPH_ERRORS as error:
            raise DomainError(503, "NEO4J_UNAVAILABLE", "Neo4j no está disponible") from error

    def _one(self, query, parameters=None):
        try:
            return self.client.query_one(query, parameters)
        except GRAPH_ERRORS as error:
            raise DomainError(503, "NEO4J_UNAVAILABLE", "Neo4j no está disponible") from error

    def summary(self):
        result = self._one(
            """
            MATCH (e:Equipo) WITH count(e) AS equipos
            MATCH (j:Jugador) WITH equipos, count(j) AS jugadores
            MATCH (p:Partido) WITH equipos, jugadores, count(p) AS partidos
            MATCH (c:Confederacion)
            WITH equipos, jugadores, partidos, count(c) AS confederaciones
            MATCH ()-[r]->()
            RETURN equipos, jugadores, partidos, confederaciones,
                   count(r) AS relaciones
            """
        )
        if result is None:
            raise DomainError(503, "NEO4J_EMPTY", "Neo4j no devolvió el resumen")
        return result

    def rivals(self, team_id):
        team = self._one(
            "MATCH (e:Equipo {id: $team_id}) RETURN e.id AS id, e.nombre AS nombre",
            {"team_id": team_id},
        )
        if team is None:
            raise DomainError(404, "TEAM_NOT_FOUND", "Equipo inexistente")
        rows = self._all(
            """
            MATCH (equipo:Equipo {id: $team_id})-[:LOCAL_EN|VISITANTE_EN]->(p:Partido)
            MATCH (rival:Equipo)-[:LOCAL_EN|VISITANTE_EN]->(p)
            WHERE rival <> equipo
            RETURN p.id AS partidoId, rival.id AS equipoId,
                   rival.nombre AS nombre, p.inicioProgramado AS inicioProgramado
            ORDER BY inicioProgramado, equipoId
            """,
            {"team_id": team_id},
        )
        return {"equipoId": team_id, "items": rows}

    def recommendations(self, player_id, limit):
        player = self._one(
            "MATCH (j:Jugador {id: $player_id}) RETURN j.id AS id, j.nombre AS nombre",
            {"player_id": player_id},
        )
        if player is None:
            raise DomainError(404, "PLAYER_NOT_FOUND", "Jugador inexistente")
        rows = self._all(
            """
            MATCH (origen:Jugador {id: $player_id})-[:PERTENECE_A]->(equipo:Equipo)
                  -[:MIEMBRO_DE]->(conf:Confederacion)<-[:MIEMBRO_DE]-(otroEquipo:Equipo)
                  <-[:PERTENECE_A]-(candidato:Jugador)
            WHERE candidato.posicion = origen.posicion AND candidato <> origen
            RETURN candidato.id AS jugadorId, candidato.nombre AS nombre,
                   candidato.posicion AS posicion, otroEquipo.id AS equipoId,
                   otroEquipo.nombre AS equipo,
                   abs(otroEquipo.ranking - equipo.ranking) AS diferenciaRanking,
                   conf.id AS criterio
            ORDER BY diferenciaRanking, jugadorId
            LIMIT $limit
            """,
            {"player_id": player_id, "limit": limit},
        )
        return {
            "jugadorId": player_id,
            "criterio": "MISMA_POSICION_Y_CONFEDERACION",
            "items": rows,
        }

    def team_path(self, origin_id, destination_id):
        endpoints = self._one(
            """
            OPTIONAL MATCH (origen:Equipo {id: $origin_id})
            OPTIONAL MATCH (destino:Equipo {id: $destination_id})
            RETURN origen IS NOT NULL AS origenExiste,
                   destino IS NOT NULL AS destinoExiste
            """,
            {"origin_id": origin_id, "destination_id": destination_id},
        )
        if not endpoints["origenExiste"] or not endpoints["destinoExiste"]:
            raise DomainError(404, "TEAM_NOT_FOUND", "Equipo de origen o destino inexistente")
        result = self._one(
            """
            MATCH (origen:Equipo {id: $origin_id}), (destino:Equipo {id: $destination_id})
            MATCH camino = shortestPath(
              (origen)-[:MIEMBRO_DE|PARTICIPA_EN*..4]-(destino)
            )
            RETURN [n IN nodes(camino) | {
                     tipo: labels(n)[0], id: n.id, nombre: coalesce(n.nombre, n.id)
                   }] AS nodos,
                   [r IN relationships(camino) | type(r)] AS relaciones,
                   length(camino) AS saltos
            """,
            {"origin_id": origin_id, "destination_id": destination_id},
        )
        if result is None:
            raise DomainError(404, "PATH_NOT_FOUND", "No existe un camino entre los equipos")
        return {
            "origenId": origin_id,
            "destinoId": destination_id,
            **result,
        }

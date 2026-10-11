from datetime import date

from app.adapters.neo4j import Neo4jAdapter
from app.exceptions import ResourceNotFoundError
from app.schemas.neo4j import (
    EquipoGrafoResponse,
    EventoGrafoResponse,
    PartidoEventosResponse,
    SedeGrafoResponse,
)


class Neo4jService:
    def __init__(self, adapter: Neo4jAdapter) -> None:
        self._adapter = adapter

    def get_partido_eventos(
        self,
        codigo: str,
    ) -> PartidoEventosResponse:
        result = self._adapter.get_partido_eventos(
            codigo
        )

        if result is None:
            raise ResourceNotFoundError(
                resource="el partido",
                identifier=codigo,
            )

        partido = result["partido"]
        sede = result["sede"]

        return PartidoEventosResponse(
            codigo=partido["codigo"],
            fecha=date.fromisoformat(
                str(partido["fecha"])
            ),
            fase=partido["fase"],
            equipos=[
                EquipoGrafoResponse(
                    codigo=equipo["codigo"],
                    nombre=equipo["nombre"],
                    confederacion=equipo[
                        "confederacion"
                    ],
                )
                for equipo in result["equipos"]
            ],
            sede=(
                SedeGrafoResponse(
                    codigo=sede["codigo"],
                    nombre=sede["nombre"],
                )
                if sede is not None
                else None
            ),
            eventos=[
                EventoGrafoResponse(
                    codigo=evento["codigo"],
                    tipo=evento["tipo"],
                    minuto=int(evento["minuto"]),
                )
                for evento in result["eventos"]
            ],
        )
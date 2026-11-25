from datetime import datetime, timezone
from uuid import uuid4

from psycopg import Error as PsycopgError
from psycopg_pool import PoolClosed, PoolTimeout, TooManyRequests

from .errors import DomainError


DATAMART_CONNECTION_ERRORS = (
    OSError,
    PsycopgError,
    PoolClosed,
    PoolTimeout,
    TooManyRequests,
)


def _utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class DataMartService:
    def __init__(self, connection_factory):
        self.connection_factory = connection_factory

    def health(self):
        try:
            with self.connection_factory() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 AS ok")
                    return "UP" if cursor.fetchone()["ok"] == 1 else "DOWN"
        except DATAMART_CONNECTION_ERRORS:
            return "DOWN"

    def refresh(self, snapshot, summaries):
        execution_id = uuid4()
        try:
            with self.connection_factory() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO analytics.etl_ejecucion "
                        "(ejecucion_id, iniciada_en, estado) VALUES (%s, now(), 'EN_CURSO')",
                        (execution_id,),
                    )
                    cursor.execute(
                        "INSERT INTO analytics.dim_torneo (torneo_id, nombre) VALUES (%s, %s) "
                        "ON CONFLICT (torneo_id) DO UPDATE SET nombre = EXCLUDED.nombre",
                        ("TOR-2030", "Fixture 2030"),
                    )
                    for team in snapshot["equipos"]:
                        cursor.execute(
                            "INSERT INTO analytics.dim_equipo "
                            "(equipo_id, nombre, confederacion) VALUES (%s, %s, %s) "
                            "ON CONFLICT (equipo_id) DO UPDATE SET nombre=EXCLUDED.nombre, "
                            "confederacion=EXCLUDED.confederacion",
                            (team["equipoId"], team["nombre"], team["confederacion"]),
                        )
                    for player in snapshot["jugadores"]:
                        cursor.execute(
                            "INSERT INTO analytics.dim_jugador "
                            "(jugador_id, nombre, posicion, equipo_id) VALUES (%s,%s,%s,%s) "
                            "ON CONFLICT (jugador_id) DO UPDATE SET nombre=EXCLUDED.nombre, "
                            "posicion=EXCLUDED.posicion, equipo_id=EXCLUDED.equipo_id",
                            (player["jugadorId"], player["nombre"], player["posicion"], player["equipoId"]),
                        )
                    for match in snapshot["partidos"]:
                        cursor.execute(
                            "INSERT INTO analytics.dim_partido "
                            "(partido_id, torneo_id, local_id, visitante_id, inicio_programado, estado) "
                            "VALUES (%s,'TOR-2030',%s,%s,%s,%s) ON CONFLICT (partido_id) DO UPDATE "
                            "SET local_id=EXCLUDED.local_id, visitante_id=EXCLUDED.visitante_id, "
                            "inicio_programado=EXCLUDED.inicio_programado, estado=EXCLUDED.estado",
                            (match["partidoId"], match["localId"], match["visitanteId"], match["inicioProgramado"], match["estado"]),
                        )
                    for event in snapshot["eventos"]:
                        occurred = _utc(event["ocurridoEn"])
                        date_key = int(occurred.strftime("%Y%m%d"))
                        cursor.execute(
                            "INSERT INTO analytics.dim_fecha (fecha_key,fecha,anio,mes,dia) "
                            "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (fecha_key) DO NOTHING",
                            (date_key, occurred.date(), occurred.year, occurred.month, occurred.day),
                        )
                        cursor.execute(
                            "INSERT INTO analytics.dim_tipo_evento (tipo) VALUES (%s) "
                            "ON CONFLICT (tipo) DO NOTHING", (event["tipo"],),
                        )
                        cursor.execute(
                            "INSERT INTO analytics.fact_evento_partido "
                            "(evento_id,partido_key,fecha_key,tipo_evento_key,equipo_key,jugador_key,"
                            "secuencia,ocurrido_en,goles,asistencias,evento_origen_id,cargado_en) "
                            "SELECT %s,p.partido_key,%s,t.tipo_evento_key,e.equipo_key,j.jugador_key,"
                            "%s,%s,%s,%s,%s,now() FROM analytics.dim_partido p "
                            "JOIN analytics.dim_tipo_evento t ON t.tipo=%s "
                            "LEFT JOIN analytics.dim_equipo e ON e.equipo_id=%s "
                            "LEFT JOIN analytics.dim_jugador j ON j.jugador_id=%s "
                            "WHERE p.partido_id=%s ON CONFLICT (evento_id) DO UPDATE SET "
                            "tipo_evento_key=EXCLUDED.tipo_evento_key,equipo_key=EXCLUDED.equipo_key,"
                            "jugador_key=EXCLUDED.jugador_key,goles=EXCLUDED.goles,"
                            "asistencias=EXCLUDED.asistencias,evento_origen_id=EXCLUDED.evento_origen_id,"
                            "cargado_en=now()",
                            (event["eventoId"], date_key, event["secuencia"], occurred,
                             event["goles"], event["asistencias"], event.get("eventoOrigenId"),
                             event["tipo"], event.get("equipoId"), event.get("jugadorId"), event["partidoId"]),
                        )
                    for item in summaries:
                        window = _utc(item["ventanaInicio"])
                        date_key = int(window.strftime("%Y%m%d"))
                        cursor.execute(
                            "INSERT INTO analytics.dim_fecha (fecha_key,fecha,anio,mes,dia) "
                            "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (fecha_key) DO NOTHING",
                            (date_key, window.date(), window.year, window.month, window.day),
                        )
                        cursor.execute(
                            "INSERT INTO analytics.fact_estadistica_equipo_15m "
                            "(partido_key,equipo_key,fecha_key,ventana_inicio,posesion_promedio,"
                            "pases_total,tiros_finales,goles_finales,muestras,cargado_en) "
                            "SELECT p.partido_key,e.equipo_key,%s,%s,%s,%s,%s,%s,%s,now() "
                            "FROM analytics.dim_partido p JOIN analytics.dim_equipo e ON e.equipo_id=%s "
                            "WHERE p.partido_id=%s ON CONFLICT (partido_key,equipo_key,ventana_inicio) "
                            "DO UPDATE SET posesion_promedio=EXCLUDED.posesion_promedio,"
                            "pases_total=EXCLUDED.pases_total,tiros_finales=EXCLUDED.tiros_finales,"
                            "goles_finales=EXCLUDED.goles_finales,muestras=EXCLUDED.muestras,cargado_en=now()",
                            (date_key, window, item["posesionPromedio"], item["pasesTotal"],
                             item["tirosFinales"], item["golesFinales"], item["muestras"],
                             item["equipoId"], item["partidoId"]),
                        )
                    cursor.execute(
                        "UPDATE analytics.etl_ejecucion SET finalizada_en=now(),estado='OK',"
                        "eventos_cargados=%s,resumenes_cargados=%s WHERE ejecucion_id=%s",
                        (len(snapshot["eventos"]), len(summaries), execution_id),
                    )
            return {"ejecucionId": str(execution_id), "estado": "OK", "eventosCargados": len(snapshot["eventos"]), "resumenesCargados": len(summaries)}
        except DATAMART_CONNECTION_ERRORS as error:
            try:
                with self.connection_factory() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO analytics.etl_ejecucion "
                            "(ejecucion_id,iniciada_en,finalizada_en,estado,error) "
                            "VALUES (%s,now(),now(),'ERROR',%s) "
                            "ON CONFLICT (ejecucion_id) DO UPDATE SET "
                            "finalizada_en=now(),estado='ERROR',error=EXCLUDED.error",
                            (execution_id, str(error)[:500]),
                        )
            except DATAMART_CONNECTION_ERRORS:
                pass
            raise DomainError(503, "DATAMART_UNAVAILABLE", "El Data Mart no pudo completar la carga") from error

    def goals_by_team(self):
        query = """
            SELECT e.equipo_id, e.nombre, count(*)::integer AS goles
            FROM analytics.fact_evento_partido f
            JOIN analytics.dim_equipo e ON e.equipo_key=f.equipo_key
            WHERE f.goles=1 GROUP BY e.equipo_id,e.nombre ORDER BY goles DESC,e.equipo_id
        """
        try:
            with self.connection_factory() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    return {"fuente": "DATAMART", "items": [
                        {"equipoId": row["equipo_id"], "nombre": row["nombre"], "goles": row["goles"]}
                        for row in cursor.fetchall()
                    ]}
        except DATAMART_CONNECTION_ERRORS as error:
            raise DomainError(503, "DATAMART_UNAVAILABLE", "El Data Mart no respondió") from error

    def summary(self):
        try:
            with self.connection_factory() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT (SELECT count(*) FROM analytics.dim_equipo) AS equipos,(SELECT count(*) FROM analytics.dim_jugador) AS jugadores,(SELECT count(*) FROM analytics.dim_partido) AS partidos,(SELECT count(*) FROM analytics.fact_evento_partido) AS eventos,(SELECT count(*) FROM analytics.fact_estadistica_equipo_15m) AS resumenes")
                    return dict(cursor.fetchone())
        except DATAMART_CONNECTION_ERRORS as error:
            raise DomainError(503, "DATAMART_UNAVAILABLE", "El Data Mart no respondió") from error

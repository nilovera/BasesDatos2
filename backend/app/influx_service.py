import base64
import binascii
import json
import math
from datetime import datetime, timezone

from .errors import DomainError


def _utc(value):
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainError(
            422, "INVALID_TELEMETRY_TIME", "El timestamp debe incluir zona horaria"
        )
    return value.astimezone(timezone.utc)


def _iso(value):
    return _utc(value).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_time(value):
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _timestamp_ns(value):
    value = _utc(value)
    seconds = int(value.timestamp())
    return seconds * 1_000_000_000 + value.microsecond * 1_000


def _tag(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(" ", "\\ ")
        .replace(",", "\\,")
        .replace("=", "\\=")
    )


def _number(value):
    number = float(value)
    if not math.isfinite(number):
        raise DomainError(422, "INVALID_TELEMETRY_VALUE", "El valor debe ser finito")
    return format(number, ".15g")


def encode_position_cursor(captured_at, player_id):
    payload = json.dumps(
        {"t": _iso(captured_at), "j": player_id},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def decode_position_cursor(cursor):
    try:
        padding = "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(cursor + padding))
        captured_at = _parse_time(payload["t"])
        player_id = payload["j"]
        if (
            not isinstance(player_id, str)
            or len(player_id) != 8
            or not player_id.startswith("JUG-")
            or not player_id[4:].isdigit()
        ):
            raise ValueError("jugador invalido")
        return captured_at, player_id
    except (
        ValueError,
        KeyError,
        TypeError,
        UnicodeDecodeError,
        binascii.Error,
        json.JSONDecodeError,
    ) as error:
        raise DomainError(
            400, "INVALID_TELEMETRY_CURSOR", "El cursor de telemetria no es valido"
        ) from error


class InfluxTelemetryService:
    def __init__(self, client, detail_database, historical_database):
        self.client = client
        self.detail_database = detail_database
        self.historical_database = historical_database

    def health(self):
        return self.client.health()

    def write_positions(self, match_id, samples):
        seen = set()
        lines = []
        for sample in samples:
            identity = (sample.jugador_id, _iso(sample.capturado_en))
            if identity in seen:
                raise DomainError(
                    422,
                    "DUPLICATE_TELEMETRY_SAMPLE",
                    "El lote contiene dos posiciones para el mismo jugador y timestamp",
                )
            seen.add(identity)
            lines.append(
                "posiciones_jugador,"
                f"partido_id={_tag(match_id)},equipo_id={_tag(sample.equipo_id)},"
                f"jugador_id={_tag(sample.jugador_id)} "
                f"x={_number(sample.x)},y={_number(sample.y)},"
                f"periodo={sample.periodo}i,segundo_partido={sample.segundo_partido}i "
                f"{_timestamp_ns(sample.capturado_en)}"
            )
        self.client.write_lines(self.detail_database, lines)
        return {
            "partidoId": match_id,
            "muestrasAceptadas": len(lines),
            "repetible": True,
            "base": self.detail_database,
        }

    def write_team_statistics(self, match_id, samples):
        seen = set()
        lines = []
        for sample in samples:
            identity = (sample.equipo_id, _iso(sample.capturado_en))
            if identity in seen:
                raise DomainError(
                    422,
                    "DUPLICATE_TELEMETRY_SAMPLE",
                    "El lote contiene dos estadisticas para el mismo equipo y timestamp",
                )
            seen.add(identity)
            lines.append(
                "estadisticas_equipo,"
                f"partido_id={_tag(match_id)},equipo_id={_tag(sample.equipo_id)} "
                f"posesion_pct={_number(sample.posesion_pct)},"
                f"pases_intervalo={sample.pases_intervalo}i,"
                f"tiros_acumulados={sample.tiros_acumulados}i,"
                f"goles_acumulados={sample.goles_acumulados}i,"
                f"periodo={sample.periodo}i,segundo_partido={sample.segundo_partido}i "
                f"{_timestamp_ns(sample.capturado_en)}"
            )
        self.client.write_lines(self.detail_database, lines)
        return {
            "partidoId": match_id,
            "muestrasAceptadas": len(lines),
            "repetible": True,
            "base": self.detail_database,
        }

    def list_positions(
        self,
        match_id,
        player_id=None,
        from_time=None,
        to_time=None,
        cursor=None,
        limit=100,
    ):
        if from_time and to_time and _utc(from_time) >= _utc(to_time):
            raise DomainError(
                400, "INVALID_TELEMETRY_WINDOW", "desde debe ser anterior a hasta"
            )
        filters = [f"partido_id = '{match_id}'"]
        if player_id:
            filters.append(f"jugador_id = '{player_id}'")
        if from_time:
            filters.append(f"time >= '{_iso(from_time)}'")
        if to_time:
            filters.append(f"time < '{_iso(to_time)}'")
        if cursor:
            cursor_time, cursor_player = decode_position_cursor(cursor)
            timestamp = _iso(cursor_time)
            filters.append(
                f"(time > '{timestamp}' OR (time = '{timestamp}' AND jugador_id > '{cursor_player}'))"
            )
        sql = (
            "SELECT time, equipo_id, jugador_id, x, y, periodo, segundo_partido "
            "FROM posiciones_jugador WHERE "
            + " AND ".join(filters)
            + f" ORDER BY time, jugador_id LIMIT {limit + 1}"
        )
        rows = self.client.query(self.detail_database, sql)
        has_more = len(rows) > limit
        page = rows[:limit]
        items = []
        for row in page:
            captured_at = _parse_time(row["time"])
            items.append(
                {
                    "partidoId": match_id,
                    "equipoId": row["equipo_id"],
                    "jugadorId": row["jugador_id"],
                    "x": float(row["x"]),
                    "y": float(row["y"]),
                    "periodo": int(row["periodo"]),
                    "segundoPartido": int(row["segundo_partido"]),
                    "capturadoEn": _iso(captured_at),
                }
            )
        next_cursor = None
        if has_more and page:
            last = page[-1]
            next_cursor = encode_position_cursor(
                _parse_time(last["time"]), last["jugador_id"]
            )
        return {"items": items, "siguienteCursor": next_cursor}

    def heatmap(self, match_id, player_id, resolution, from_time=None, to_time=None):
        if from_time and to_time and _utc(from_time) >= _utc(to_time):
            raise DomainError(
                400, "INVALID_TELEMETRY_WINDOW", "desde debe ser anterior a hasta"
            )
        filters = [
            f"partido_id = '{match_id}'",
            f"jugador_id = '{player_id}'",
        ]
        if from_time:
            filters.append(f"time >= '{_iso(from_time)}'")
        if to_time:
            filters.append(f"time < '{_iso(to_time)}'")
        sql = (
            "SELECT x, y FROM posiciones_jugador WHERE "
            + " AND ".join(filters)
            + " ORDER BY time LIMIT 10001"
        )
        rows = self.client.query(self.detail_database, sql)
        if len(rows) > 10000:
            raise DomainError(
                413,
                "HEATMAP_WINDOW_TOO_LARGE",
                "La ventana supera 10.000 puntos; acote desde/hasta",
            )
        cells = {}
        cell_size = 100.0 / resolution
        for row in rows:
            x = min(100.0, max(0.0, float(row["x"])))
            y = min(100.0, max(0.0, float(row["y"])))
            cell_x = min(resolution - 1, int(x / cell_size))
            cell_y = min(resolution - 1, int(y / cell_size))
            cells[(cell_x, cell_y)] = cells.get((cell_x, cell_y), 0) + 1
        result = [
            {
                "celdaX": cell_x,
                "celdaY": cell_y,
                "xDesde": round(cell_x * cell_size, 6),
                "xHasta": round((cell_x + 1) * cell_size, 6),
                "yDesde": round(cell_y * cell_size, 6),
                "yHasta": round((cell_y + 1) * cell_size, 6),
                "muestras": count,
            }
            for (cell_x, cell_y), count in sorted(cells.items())
        ]
        return {
            "partidoId": match_id,
            "jugadorId": player_id,
            "resolucion": resolution,
            "totalMuestras": len(rows),
            "celdas": result,
        }

    def aggregate_team_statistics(self, match_id):
        sql = f"""
SELECT date_bin(INTERVAL '15 minutes', time) AS ventana,
       equipo_id,
       ROUND(AVG(posesion_pct), 2) AS posesion_promedio,
       SUM(pases_intervalo) AS pases_total,
       MAX(tiros_acumulados) AS tiros_finales,
       MAX(goles_acumulados) AS goles_finales,
       COUNT(*) AS muestras
FROM estadisticas_equipo
WHERE partido_id = '{match_id}'
GROUP BY ventana, equipo_id
ORDER BY ventana, equipo_id
""".strip()
        rows = self.client.query(self.detail_database, sql)
        lines = []
        for row in rows:
            window = _parse_time(row["ventana"])
            lines.append(
                "resumen_equipo_15m,"
                f"partido_id={_tag(match_id)},equipo_id={_tag(row['equipo_id'])} "
                f"posesion_promedio={_number(row['posesion_promedio'])},"
                f"pases_total={int(row['pases_total'])}i,"
                f"tiros_finales={int(row['tiros_finales'])}i,"
                f"goles_finales={int(row['goles_finales'])}i,"
                f"muestras={int(row['muestras'])}i "
                f"{_timestamp_ns(window)}"
            )
        self.client.write_lines(self.historical_database, lines)
        return {
            "partidoId": match_id,
            "resumenesGenerados": len(lines),
            "ventanaMinutos": 15,
            "baseDestino": self.historical_database,
        }

    def list_historical_summaries(self, match_id):
        sql = (
            "SELECT time, equipo_id, posesion_promedio, pases_total, "
            "tiros_finales, goles_finales, muestras FROM resumen_equipo_15m "
            f"WHERE partido_id = '{match_id}' ORDER BY time, equipo_id"
        )
        rows = self.client.query(self.historical_database, sql)
        return {
            "items": [
                {
                    "partidoId": match_id,
                    "equipoId": row["equipo_id"],
                    "ventanaInicio": _iso(_parse_time(row["time"])),
                    "posesionPromedio": float(row["posesion_promedio"]),
                    "pasesTotal": int(row["pases_total"]),
                    "tirosFinales": int(row["tiros_finales"]),
                    "golesFinales": int(row["goles_finales"]),
                    "muestras": int(row["muestras"]),
                }
                for row in rows
            ]
        }

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

from pymongo import ASCENDING

from .cassandra_client import get_cassandra_session
from .cassandra_service import CassandraCommentService
from .config import settings
from .database import get_client
from .errors import DomainError
from .influx_client import get_influx_client
from .influx_service import InfluxTelemetryService
from .models import PelotaMuestra, PosicionMuestra
from .metrics import (
    COMMENT_OPERATIONS,
    EVENTS_CONFIRMED,
    SIMULATION_ERRORS,
    SIMULATION_RUNNING,
    SIMULATION_SECOND,
    SIMULATION_SPEED,
    TELEMETRY_OPERATIONS,
)
from .repository import MongoRepository
from .redis_client import get_redis_client
from .simulator_engine import (
    COMMENT_TEMPLATES,
    MATCH_SECONDS,
    TELEMETRY_STEP_SECONDS,
    ball_sample,
    event_comment,
    position_samples,
)


LOGGER = logging.getLogger("fixture2030.simulation")
COMMENT_RETRY_ATTEMPTS = 4


def _utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class SimulationWorker:
    def __init__(self, poll_seconds=0.25):
        client = get_client()
        self.repository = MongoRepository(client)
        self.db = client[settings.mongodb_database]
        self.comments = None
        self.telemetry = None
        self.redis = None
        self.poll_seconds = poll_seconds
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.run_forever, name="fixture2030-simulator", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)

    def _rosters(self, simulation):
        match = self.db.partidos.find_one({"_id": simulation["partidoId"]})
        ids = match["alineaciones"]["local"]["titulares"] + match["alineaciones"]["local"]["suplentes"]
        ids += match["alineaciones"]["visitante"]["titulares"] + match["alineaciones"]["visitante"]["suplentes"]
        players = {
            row["jugadorId"]: {"jugadorId": row["jugadorId"], "equipoId": row["equipoId"], "posicion": row["posicion"], "nombre": row["nombre"]}
            for row in self.db.jugadores.find({"jugadorId": {"$in": ids}})
        }
        teams = match["equipos"]
        starters = {
            teams["localId"]: [players[value] for value in match["alineaciones"]["local"]["titulares"]],
            teams["visitanteId"]: [players[value] for value in match["alineaciones"]["visitante"]["titulares"]],
        }
        benches = {
            teams["localId"]: [players[value] for value in match["alineaciones"]["local"]["suplentes"]],
            teams["visitanteId"]: [players[value] for value in match["alineaciones"]["visitante"]["suplentes"]],
        }
        return match, starters, benches

    @staticmethod
    def _event_payload(event):
        allowed = {
            "INICIO_PARTIDO": (),
            "GOL": ("periodo", "minuto", "equipoId", "jugadorId", "asistenteJugadorId", "x", "y"),
            "TARJETA": ("periodo", "minuto", "equipoId", "jugadorId", "color", "motivo"),
            "SUSTITUCION": ("periodo", "minuto", "equipoId", "saleJugadorId", "entraJugadorId"),
            "GOL_ANULADO_VAR": ("periodo", "minuto", "equipoId", "jugadorId", "motivo", "x", "y"),
            "FIN_PARTIDO": ("periodo", "minuto"),
        }
        payload = {"tipo": event["tipo"], "ocurridoEn": event["ocurridoEn"]}
        payload.update({key: event[key] for key in allowed[event["tipo"]] if event.get(key) is not None})
        return payload

    def _publish_comment(self, simulation, sequence, content, suffix):
        if self.comments is None:
            self.comments = CassandraCommentService(get_cassandra_session())
        user = f"USR-{(sequence % 200) + 1:04d}"
        key = f"simulacion:{simulation['simulacionId']}:{suffix}:{sequence:05d}"
        for attempt in range(1, COMMENT_RETRY_ATTEMPTS + 1):
            try:
                self.comments.publish(simulation["partidoId"], user, content, key)
                COMMENT_OPERATIONS.labels("simulation_publish", "OK").inc()
                return
            except DomainError as error:
                if error.code != "CASSANDRA_UNAVAILABLE" or attempt == COMMENT_RETRY_ATTEMPTS:
                    COMMENT_OPERATIONS.labels("simulation_publish", "ERROR").inc()
                    raise
                delay = 0.25 * (2 ** (attempt - 1))
                LOGGER.warning(
                    "simulacion=%s comentario=%s Cassandra temporalmente no disponible; "
                    "reintento=%s/%s en %.2fs",
                    simulation["simulacionId"],
                    key,
                    attempt + 1,
                    COMMENT_RETRY_ATTEMPTS,
                    delay,
                )
                time.sleep(delay)

    def _process_events(self, simulation, target_second):
        next_index = int(simulation["siguienteEvento"])
        plan = simulation["plan"]
        while next_index < len(plan) and plan[next_index]["segundo"] <= target_second:
            event = plan[next_index]
            payload = self._event_payload(event)
            result = self.repository.register_event(
                simulation["partidoId"],
                f"simulacion:{simulation['simulacionId']}:evento:{next_index:03d}",
                payload,
                datetime.fromisoformat(event["ocurridoEn"].replace("Z", "+00:00")),
            )
            if not result.replayed:
                EVENTS_CONFIRMED.labels(payload["tipo"]).inc()
            self._publish_comment(simulation, next_index, event_comment(event), "evento")
            reactions = 3 if event["tipo"] in {"GOL", "GOL_ANULADO_VAR"} else 1
            for reaction in range(reactions):
                content = COMMENT_TEMPLATES[(simulation["semilla"] + next_index + reaction) % len(COMMENT_TEMPLATES)]
                self._publish_comment(
                    simulation,
                    next_index * 10 + reaction + 1,
                    content,
                    "reaccion",
                )
            next_index += 1
        return next_index

    def _write_telemetry(self, simulation, target_second, match, starters, benches):
        if self.telemetry is None:
            self.telemetry = InfluxTelemetryService(
                get_influx_client(),
                settings.influxdb_detail_database,
                settings.influxdb_historical_database,
            )
        last = int(simulation["ultimoSegundoTelemetria"])
        seconds = list(range(last + TELEMETRY_STEP_SECONDS, int(target_second) + 1, TELEMETRY_STEP_SECONDS))
        if not seconds:
            return last
        local = match["equipos"]["localId"]
        visitor = match["equipos"]["visitanteId"]
        plan = simulation["plan"]
        logical_start = datetime.fromisoformat(plan[0]["ocurridoEn"].replace("Z", "+00:00"))
        for offset in range(0, len(seconds), 10):
            position_batch = []
            ball_batch = []
            for second in seconds[offset:offset + 10]:
                captured = logical_start + timedelta(seconds=second)
                raw_positions, possession = position_samples(
                    simulation["semilla"], second, local, visitor, starters, benches, plan, captured
                )
                raw_ball = ball_sample(simulation["semilla"], second, possession, raw_positions, plan, captured)
                position_batch.extend(PosicionMuestra.model_validate(item) for item in raw_positions)
                ball_batch.append(PelotaMuestra.model_validate(raw_ball))
            self.telemetry.write_positions(simulation["partidoId"], position_batch)
            self.telemetry.write_ball_positions(simulation["partidoId"], ball_batch)
            TELEMETRY_OPERATIONS.labels("simulation_positions", "OK").inc()
            TELEMETRY_OPERATIONS.labels("simulation_ball", "OK").inc()
        return seconds[-1]

    def _write_regular_comments(self, simulation, target_second):
        next_second = int(simulation["siguienteComentario"])
        sequence = next_second
        while next_second <= target_second:
            template = COMMENT_TEMPLATES[(simulation["semilla"] + next_second) % len(COMMENT_TEMPLATES)]
            self._publish_comment(simulation, sequence, template, "comentario")
            interval = 35 + ((simulation["semilla"] + next_second * 17) % 31)
            next_second += interval
            sequence = next_second
        return next_second

    def run_once(self):
        simulation = self.db.simulaciones.find_one({"estado": "EJECUTANDO"}, sort=[("creadoEn", ASCENDING)])
        if simulation is None:
            SIMULATION_RUNNING.set(0)
            return False
        SIMULATION_RUNNING.set(1)
        SIMULATION_SECOND.set(float(simulation["segundoPartido"]))
        SIMULATION_SPEED.set(float(simulation["velocidad"]))
        now = datetime.now(timezone.utc)
        previous_tick = _utc(simulation.get("ultimoTickEn") or now)
        elapsed = min(2.0, max(0.0, (now - previous_tick).total_seconds()))
        target = min(MATCH_SECONDS, float(simulation["segundoPartido"]) + elapsed * float(simulation["velocidad"]))
        try:
            match, starters, benches = self._rosters(simulation)
            next_event = self._process_events(simulation, target)
            last_telemetry = self._write_telemetry(simulation, target, match, starters, benches)
            next_comment = self._write_regular_comments(simulation, target)
            final = target >= MATCH_SECONDS and next_event >= len(simulation["plan"])
            if self.redis is None:
                self.redis = get_redis_client()
            self.redis.hset(
                f"marcador:partido:{simulation['partidoId']}",
                mapping={
                    "segundoPartido": int(target),
                    "minuto": round(target / 60.0, 2),
                    "velocidad": float(simulation["velocidad"]),
                    "simulacionEstado": "FINALIZADA" if final else "EJECUTANDO",
                },
            )
            self.db.simulaciones.update_one(
                {"_id": simulation["_id"], "estado": "EJECUTANDO"},
                {"$set": {
                    "segundoPartido": float(target), "siguienteEvento": next_event,
                    "ultimoSegundoTelemetria": last_telemetry, "siguienteComentario": next_comment,
                    "estado": "FINALIZADA" if final else "EJECUTANDO",
                    "ultimoTickEn": None if final else now, "actualizadoEn": now, "error": None,
                }},
            )
            SIMULATION_SECOND.set(float(target))
            if final:
                SIMULATION_RUNNING.set(0)
        except Exception as error:
            LOGGER.exception("simulacion=%s error", simulation["simulacionId"])
            self.db.simulaciones.update_one(
                {"_id": simulation["_id"]},
                {"$set": {"estado": "ERROR", "error": f"{type(error).__name__}: {error}"[:500], "actualizadoEn": now}},
            )
            SIMULATION_ERRORS.inc()
            SIMULATION_RUNNING.set(0)
        return True

    def run_forever(self):
        while not self.stop_event.is_set():
            processed = self.run_once()
            self.stop_event.wait(0.05 if processed else self.poll_seconds)


_worker = None


def start_simulation_worker():
    global _worker
    _worker = SimulationWorker()
    _worker.start()


def stop_simulation_worker():
    global _worker
    if _worker:
        _worker.stop()
    _worker = None


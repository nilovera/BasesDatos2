"""Metadatos de auditoria. Las sesiones del laboratorio no prueban identidad real."""
import re
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid4, uuid5

from .errors import DomainError

_context = ContextVar("audit_context", default=None)
SAFE_ID = re.compile(r"^[A-Za-z0-9:_-]{1,128}$")
DETAIL_FIELDS = {"estado", "tipoEvento", "partidoId", "autorComentario", "eventoOriginalId", "eventoId",
                 "velocidad", "estadoAnterior", "estadoNuevo", "motivoHash"}


@contextmanager
def audit_scope(actor_id="interno", actor_type="SERVICIO", request_id=None,
                method="INTERNO", route="", role=None):
    token = _context.set({"actorId": actor_id, "actorTipo": actor_type,
                          "requestId": request_id or str(uuid4()), "metodo": method,
                          "ruta": route, "rol": role})
    try:
        yield
    finally:
        _context.reset(token)


def current_context():
    return _context.get() or {"actorId": "interno", "actorTipo": "SERVICIO", "rol": None,
                              "requestId": None, "metodo": "INTERNO", "ruta": ""}


def actor_from_session(session):
    return {"actor_id": session["usuarioId"], "actor_type": "SESION_LAB",
            "role": session["rol"]}


def require_audit_admin():
    ctx = current_context()
    if ctx["actorTipo"] != "SESION_LAB" or ctx["rol"] != "ADMIN":
        raise DomainError(403, "AUDIT_ADMIN_REQUIRED", "Usa una sesion ADMIN del laboratorio mediante X-Session-ID")


def request_dependencies(route, method):
    if route.startswith("/api/v1/auditoria"):
        return ["mongodb"] if route.endswith("/pendientes") else ["cassandra"]
    if "/directo" in route:
        if route.endswith("/cancha"):
            return ["mongodb", "influxdb"]
        if route.endswith("/comentarios"):
            return ["mongodb", "cassandra"]
        if route.endswith("/equipos") or route.endswith("/partidos"):
            return ["mongodb"]
        return ["mongodb", "redis"]
    if "/telemetria" in route or "/mapa-calor" in route:
        return ["mongodb", "influxdb"] if method == "POST" else ["influxdb"]
    if "/comentarios" in route:
        return ["mongodb", "cassandra"] if method == "POST" else ["cassandra"]
    if "/sesiones" in route:
        return ["redis"]
    if "/grafo" in route:
        return ["neo4j"]
    if "/datamart" in route:
        return ["mongodb", "influxdb", "postgresql"] if route.endswith("/refrescar") else ["postgresql"]
    if route == "/api/v1/partidos/{partidoId}":
        return ["mongodb", "redis"]
    if "/simulaciones/" in route and method in {"POST", "PATCH"}:
        return ["mongodb", "redis"]
    if route == "unmatched":
        return []
    return ["mongodb"]


def make_audit_event(action, resource_type, resource_id, *, operation_id=None,
                     occurred_at=None, declared_actor=None, detail=None, result="OK"):
    ctx = dict(current_context())
    if declared_actor:
        if ctx["actorTipo"] == "SESION_LAB" and ctx["actorId"] != declared_actor:
            raise DomainError(403, "AUDIT_ACTOR_MISMATCH", "El usuario no coincide con la sesion de laboratorio")
        if ctx["actorTipo"] == "ANONIMO":
            ctx.update(actorId=declared_actor, actorTipo="DECLARADO")
    detail = dict(detail or {})
    if set(detail) - DETAIL_FIELDS:
        raise ValueError("La auditoria solo admite metadatos expresamente permitidos")
    for value in detail.values():
        if not isinstance(value, (str, int, float, bool)) or len(str(value)) > 128:
            raise ValueError("Detalle de auditoria no admitido")
    operation_id = operation_id or str(uuid4())
    if not SAFE_ID.fullmatch(operation_id):
        raise ValueError("Identificador de operacion invalido")
    when = occurred_at or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    when = when.astimezone(timezone.utc)
    # Cassandra timestamp tiene precision de milisegundos; el cursor usa la misma.
    when = when.replace(microsecond=(when.microsecond // 1000) * 1000)
    return {"auditoriaId": str(uuid5(NAMESPACE_URL, "fixture2030:audit:" + operation_id)),
            "operacionId": operation_id, "actorId": ctx["actorId"], "actorTipo": ctx["actorTipo"],
            "fecha": when.isoformat().replace("+00:00", "Z"), "accion": action,
            "recursoTipo": resource_type, "recursoId": resource_id, "resultado": result,
            "requestId": ctx["requestId"] or str(uuid4()), "metodo": ctx["metodo"],
            "ruta": ctx["ruta"], "detalle": detail}


def enqueue_audit(db, event, session):
    """Se invoca dentro de la misma transaccion que el cambio en MongoDB."""
    now = datetime.now(timezone.utc)
    db.auditoria_pendiente.insert_one(
        {"_id": event["operacionId"], "evento": event, "estado": "PENDIENTE",
         "intentos": 0, "proximoIntentoEn": now, "creadoEn": now}, session=session)

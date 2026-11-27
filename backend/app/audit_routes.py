"""Consultas de auditoria de laboratorio; sin endpoints para editar o borrar."""
from fastapi import APIRouter, Header, Query
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

from .audit_context import require_audit_admin
from .audit_service import CassandraAuditService
from .cassandra_client import get_cassandra_session
from .config import settings
from .database import get_client
from .errors import DomainError

router = APIRouter(prefix="/api/v1/auditoria", tags=["Auditoria"])


def document_lab_session(sesion: str | None = Header(
        None, alias="X-Session-ID", description="Sesion de laboratorio en Redis. No es autenticacion de produccion.")):
    return sesion


class AuditEventResponse(BaseModel):
    auditoriaId: str
    operacionId: str
    actorId: str
    actorTipo: Literal["SESION_LAB", "DECLARADO", "ANONIMO", "SERVICIO"]
    fecha: datetime
    accion: str
    recursoTipo: str
    recursoId: str
    resultado: str
    requestId: str
    metodo: str
    ruta: str
    detalle: dict[str, str | int | float | bool]


class AuditPageResponse(BaseModel):
    items: list[AuditEventResponse]
    siguienteCursor: str | None


class AuditPendingResponse(BaseModel):
    pendientes: int = Field(ge=0)
    destino: Literal["Cassandra"]


ERRORS = {400: {"description": "Dia, recurso o cursor invalido"},
          403: {"description": "Requiere sesion ADMIN del laboratorio"},
          404: {"description": "Sesion inexistente o expirada"},
          503: {"description": "Dependencia de auditoria no disponible"}}


@router.get("/actores/{actorId}", response_model=AuditPageResponse, responses=ERRORS)
def audit_by_actor(actorId: str, dia: str = Query(pattern=r"^[0-9]{8}$"),
                   cursor: str | None = Query(None, max_length=2048),
                   limite: int = Query(50, ge=1, le=100)):
    require_audit_admin()
    if not 1 <= len(actorId) <= 128:
        raise DomainError(400, "INVALID_AUDIT_ACTOR", "Actor invalido")
    return CassandraAuditService(get_cassandra_session()).by_actor(actorId, dia, cursor, limite)


@router.get("/recursos/{tipo}/{recursoId}", response_model=AuditPageResponse, responses=ERRORS)
def audit_by_resource(tipo: str, recursoId: str, dia: str = Query(pattern=r"^[0-9]{8}$"),
                      cursor: str | None = Query(None, max_length=2048),
                      limite: int = Query(50, ge=1, le=100)):
    require_audit_admin()
    if tipo not in {"COMENTARIO", "EVENTO", "SIMULACION"} or not 1 <= len(recursoId) <= 128:
        raise DomainError(400, "INVALID_AUDIT_RESOURCE", "Recurso de auditoria invalido")
    return CassandraAuditService(get_cassandra_session()).by_resource(tipo, recursoId, dia, cursor, limite)


@router.get("/pendientes", response_model=AuditPendingResponse, responses=ERRORS)
def audit_pending():
    require_audit_admin()
    try:
        count = get_client()[settings.mongodb_database].auditoria_pendiente.count_documents({})
        return {"pendientes": count, "destino": "Cassandra"}
    except Exception as error:
        raise DomainError(503, "AUDIT_QUEUE_UNAVAILABLE", "No se pudo consultar la cola de auditoria") from error

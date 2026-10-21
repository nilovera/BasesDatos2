from typing import Literal

from pydantic import BaseModel


EstadoDependencia = Literal["up", "down", "unknown", "not_configured"]
EstadoReadiness = Literal["ready", "degraded", "not_ready"]


class HealthResponse(BaseModel):
    estado: Literal["ok"]
    servicio: str
    version: str
    entorno: str


class ReadinessResponse(BaseModel):
    estado: EstadoReadiness
    dependencias: dict[str, EstadoDependencia]
    desde_cache: bool
    antiguedad_segundos: float


class DependenciaEstado(BaseModel):
    dependencia: str
    estado: EstadoDependencia
    clasificacion: str
    detalle: str
    duracion_ms: float
    verificado_en: str


class DependenciasResponse(BaseModel):
    estado_general: EstadoReadiness
    dependencias: list[DependenciaEstado]
    desde_cache: bool
    antiguedad_segundos: float
    ttl_cache_segundos: float
    timeout_por_dependencia_segundos: float

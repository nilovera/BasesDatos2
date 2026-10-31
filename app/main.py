from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.cassandra import CassandraAdapter
from app.adapters.influxdb import InfluxDBAdapter
from app.adapters.iris import IRISAdapter
from app.adapters.mongodb import MongoAdapter
from app.adapters.neo4j import Neo4jAdapter
from app.adapters.redis import RedisAdapter
from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.middleware.error_handlers import (
    register_error_handlers,
)
from app.middleware.metrics import PrometheusMiddleware
from app.middleware.request_context import (
    RequestContextMiddleware,
)
from app.routes.cassandra import router as cassandra_router
from app.routes.health import router as health_router
from app.routes.influxdb import router as influxdb_router
from app.routes.iris import router as iris_router
from app.routes.metrics import router as metrics_router
from app.routes.mongodb import router as mongodb_router
from app.routes.neo4j import router as neo4j_router
from app.routes.redis import router as redis_router
from app.services.corte_rapido import AdaptadorProtegido, CorteRapido
from app.services.dependency_health import DependencyHealthChecker


settings = get_settings()

configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    # Hito 13: cada adaptador queda envuelto por el corte rápido. Con
    # CORTE_RAPIDO_SEGUNDOS=0 el envoltorio no cambia el comportamiento.
    corte_rapido = CorteRapido(settings.corte_rapido_segundos)
    application.state.corte_rapido = corte_rapido

    mongo_adapter = AdaptadorProtegido(MongoAdapter(settings), "MongoDB", corte_rapido)
    neo4j_adapter = AdaptadorProtegido(Neo4jAdapter(settings), "Neo4j", corte_rapido)
    cassandra_adapter = AdaptadorProtegido(CassandraAdapter(settings), "Cassandra", corte_rapido)
    redis_adapter = AdaptadorProtegido(RedisAdapter(settings), "Redis", corte_rapido)
    influxdb_adapter = AdaptadorProtegido(InfluxDBAdapter(settings), "InfluxDB", corte_rapido)
    iris_adapter = AdaptadorProtegido(IRISAdapter(settings), "InterSystems IRIS", corte_rapido)

    application.state.mongo_adapter = mongo_adapter
    application.state.neo4j_adapter = neo4j_adapter
    application.state.cassandra_adapter = cassandra_adapter
    application.state.redis_adapter = redis_adapter
    application.state.influxdb_adapter = influxdb_adapter
    application.state.iris_adapter = iris_adapter

    # Hito 11: diagnóstico por dependencia para /health/ready y
    # /health/dependencias. Cada chequeo tiene un límite propio levemente
    # superior al timeout de los drivers, para que el driver informe su
    # propio error antes de que el diagnóstico corte la espera.
    health_checker = DependencyHealthChecker(
        checks={
            "MongoDB": mongo_adapter.ping,
            "Neo4j": neo4j_adapter.ping,
            "Cassandra": cassandra_adapter.ping,
            "Redis": redis_adapter.ping,
            "InfluxDB": influxdb_adapter.ping,
            "InterSystems IRIS": iris_adapter.ping,
        },
        timeout_seconds=settings.dependency_timeout_seconds + 1,
    )
    application.state.health_checker = health_checker

    try:
        yield
    finally:
        health_checker.close()
        iris_adapter.close()
        influxdb_adapter.close()
        redis_adapter.close()
        cassandra_adapter.close()
        neo4j_adapter.close()
        mongo_adapter.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API REST integrada del proyecto Fixture 2030. "
        "Expone casos de uso sobre MongoDB, Neo4j, "
        "Cassandra, Redis, InfluxDB e InterSystems IRIS."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
# Hito 13: métricas de aplicación para Prometheus (queda por fuera del
# contexto de solicitud, así mide también el costo de ese middleware).
app.add_middleware(PrometheusMiddleware)

register_error_handlers(app)

app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(mongodb_router)
app.include_router(neo4j_router)
app.include_router(cassandra_router)
app.include_router(redis_router)
app.include_router(influxdb_router)
app.include_router(iris_router)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "servicio": settings.app_name,
        "documentacion": "/docs",
    }
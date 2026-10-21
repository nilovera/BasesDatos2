"""Utilidades compartidas del diagnóstico de conectividad (Hito 11).

Contiene:

- carga de configuración externa (sin mostrar secretos);
- modelo de resultado por capa;
- redacción de secretos en cualquier texto que se imprima o guarde;
- clasificación de errores de red;
- agregación de estados por producto;
- escritura de evidencias (TXT + JSON) y de la matriz de conectividad.

Los scripts se ejecutan con el intérprete del entorno virtual de la API
(``.venv``), porque reutilizan exactamente los mismos drivers que la API.
"""

from __future__ import annotations

import errno
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urlparse

try:
    from zoneinfo import ZoneInfo

    TZ = ZoneInfo("America/Argentina/Buenos_Aires")
except Exception:  # pragma: no cover - tzdata ausente
    TZ = None


# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent
HITO_DIR = SCRIPTS_DIR.parent
REPO_ROOT = HITO_DIR.parent
DOCS_DIR = HITO_DIR / "docs"
EVIDENCIA_DIR = DOCS_DIR / "evidencia"

CONFIG_LOCAL = HITO_DIR / "config" / "conectividad.env"
CONFIG_API = REPO_ROOT / ".env"


def preparar_consola() -> None:
    """Evita errores de codificación en la consola de Windows y silencia
    las trazas internas de los drivers (el diagnóstico ya las clasifica)."""
    import logging

    logging.getLogger("cassandra").setLevel(logging.CRITICAL)
    logging.getLogger("neo4j").setLevel(logging.CRITICAL)
    logging.getLogger("pymongo").setLevel(logging.CRITICAL)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


# --------------------------------------------------------------------------
# Estados, capas y productos
# --------------------------------------------------------------------------

# Estado de una prueba individual.
OK = "OK"                  # la prueba concreta funcionó
FALLA = "FALLA"            # se intentó y falló
ADVERTENCIA = "ADVERTENCIA"  # funcionó con una observación relevante
SKIP = "SKIP"              # no se ejecutó por falta de herramienta o config
BLOQUEADA = "BLOQUEADA"    # no se ejecutó porque una capa previa falló
NO_APLICA = "NO_APLICA"    # la capa no existe en este entorno (ej. sin auth)

# Estado agregado de un producto (RNF9).
DISPONIBLE = "disponible"
NO_DISPONIBLE = "no disponible"
DEGRADADO = "degradado"
NO_PROBADO = "no probado"
DESCONOCIDO = "desconocido"
NO_CONFIGURADO = "no configurado"

CAPAS = [
    "configuracion",
    "proceso",
    "resolucion",
    "tcp",
    "protocolo",
    "autenticacion",
    "autorizacion",
    "contexto",
    "operacion",
    "api",
]

PRODUCTOS: dict[str, dict[str, Any]] = {
    "mongodb": {
        "nombre": "MongoDB",
        "modulo": "Equipos y jugadores (Hito 4)",
        "requeridas": [
            "MONGODB_HOST",
            "MONGODB_PORT",
            "MONGODB_DATABASE",
            "MONGODB_AUTH_SOURCE",
            "MONGODB_USERNAME",
            "MONGODB_PASSWORD",
        ],
        "secretos": ["MONGODB_PASSWORD"],
        "imagen": "mongo",
        "contenedor_var": "MONGODB_CONTAINER",
        "contenedor_def": "fixture2030-mongodb",
    },
    "neo4j": {
        "nombre": "Neo4j",
        "modulo": "Partidos, equipos, sedes y eventos (Hito 5)",
        "requeridas": [
            "NEO4J_URI",
            "NEO4J_DATABASE",
            "NEO4J_USERNAME",
            "NEO4J_PASSWORD",
        ],
        "secretos": ["NEO4J_PASSWORD"],
        "imagen": "neo4j",
        "contenedor_var": "NEO4J_CONTAINER",
        "contenedor_def": "fixture2030-neo4j",
    },
    "cassandra": {
        "nombre": "Cassandra",
        "modulo": "Comentarios por partido (Hito 6)",
        "requeridas": [
            "CASSANDRA_HOSTS",
            "CASSANDRA_PORT",
            "CASSANDRA_KEYSPACE",
        ],
        "secretos": ["CASSANDRA_PASSWORD"],
        "imagen": "cassandra",
        "contenedor_var": "CASSANDRA_CONTAINER",
        "contenedor_def": "fixture2030-cassandra",
    },
    "redis": {
        "nombre": "Redis",
        "modulo": "Sesiones con expiración (Hito 7)",
        "requeridas": ["REDIS_HOST", "REDIS_PORT", "REDIS_DATABASE"],
        "secretos": ["REDIS_PASSWORD"],
        "imagen": "redis",
        "contenedor_var": "REDIS_CONTAINER",
        "contenedor_def": "fixture2030-redis",
    },
    "influxdb": {
        "nombre": "InfluxDB",
        "modulo": "Estadísticas temporales (Hito 8)",
        "requeridas": [
            "INFLUXDB_URL",
            "INFLUXDB_TOKEN",
            "INFLUXDB_DETAIL_DATABASE",
            "INFLUXDB_HISTORICAL_DATABASE",
        ],
        "secretos": ["INFLUXDB_TOKEN"],
        "imagen": "influxdb",
        "contenedor_var": "INFLUXDB_CONTAINER",
        "contenedor_def": "fixture2030-influxdb",
    },
    "iris": {
        "nombre": "InterSystems IRIS",
        "modulo": "Objetos persistentes de partido (Hito 9)",
        "requeridas": [
            "IRIS_HOST",
            "IRIS_PORT",
            "IRIS_NAMESPACE",
            "IRIS_USERNAME",
            "IRIS_PASSWORD",
        ],
        "secretos": ["IRIS_PASSWORD"],
        "imagen": "intersystems/iris",
        "contenedor_var": "IRIS_CONTAINER",
        "contenedor_def": "fixture2030-iris",
    },
}

NOMBRE_A_CLAVE = {v["nombre"]: k for k, v in PRODUCTOS.items()}

# Valores por defecto de variables propias del Hito 11 (no secretas).
DEFAULTS = {
    "API_BASE_URL": "http://127.0.0.1:8000",
    "API_LOG_FILE": "logs/api.stderr.log",
    "DIAG_TIMEOUT_SECONDS": "3",
    "DIAG_ENTORNO": "",
    "NEO4J_HTTP_URL": "http://127.0.0.1:7474",
    "IRIS_PORTAL_PORT": "52773",
    "MONGO_EQUIPO_DEMO": "EQ-01",
    "NEO4J_PARTIDO_DEMO": "PAR-0001",
    "CASSANDRA_PARTIDO_DEMO": "PAR-0001",
    "CASSANDRA_BUCKET_DEMO": "203006131800",
    "CASSANDRA_TABLA": "comentarios_por_partido",
    "REDIS_SESION_DEMO": "SES-API-0001",
    "INFLUX_PARTIDO_DEMO": "PAR-0001",
    "INFLUX_DESDE": "2030-06-13T20:00:00Z",
    "INFLUX_HASTA": "2030-06-13T20:01:00Z",
    "INFLUX_TABLA_DETALLE": "estadisticas_equipo",
    "INFLUX_TABLA_HISTORICO": "resumen_equipo_minuto",
    "IRIS_PARTIDO_DEMO": "PAR-0001",
}


# --------------------------------------------------------------------------
# Configuración externa
# --------------------------------------------------------------------------

def _leer_env(path: Path) -> dict[str, str]:
    """Lee un archivo KEY=VALUE sin ejecutar nada (sin python-dotenv)."""
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if " #" in value and not value.startswith(("'", '"')):
            value = value.split(" #", 1)[0].strip()

        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]

        values[key.upper()] = value

    return values


class Config:
    """Configuración con precedencia explícita.

    1. ``--set CLAVE=VALOR`` en la línea de comandos (escenarios de falla).
    2. Variables de entorno del proceso.
    3. ``hito11-conectividad/config/conectividad.env`` (local, no versionado).
    4. ``.env`` de la API del Hito 10 (local, no versionado).
    5. Valores por defecto no secretos (``DEFAULTS``).
    """

    def __init__(self, overrides: dict[str, str] | None = None) -> None:
        self.archivo_api = _leer_env(CONFIG_API)
        self.archivo_local = _leer_env(CONFIG_LOCAL)
        self.overrides = {k.upper(): v for k, v in (overrides or {}).items()}

        self._origen: dict[str, str] = {}
        self._values: dict[str, str] = {}

        for key, value in DEFAULTS.items():
            self._values[key] = value
            self._origen[key] = "default"

        for key, value in self.archivo_api.items():
            self._values[key] = value
            self._origen[key] = ".env (API)"

        for key, value in self.archivo_local.items():
            self._values[key] = value
            self._origen[key] = "config/conectividad.env"

        conocidas = set(self._values) | {
            var for p in PRODUCTOS.values() for var in p["requeridas"]
        } | {var for p in PRODUCTOS.values() for var in p["secretos"]}

        for key in conocidas:
            if key in os.environ:
                self._values[key] = os.environ[key]
                self._origen[key] = "variable de entorno"

        for key, value in self.overrides.items():
            self._values[key] = value
            self._origen[key] = "--set (override)"

    def get(self, key: str, default: str | None = None) -> str | None:
        value = self._values.get(key.upper())
        if value is None or value == "":
            return default
        return value

    def get_int(self, key: str, default: int) -> int:
        try:
            return int(self.get(key, str(default)))
        except (TypeError, ValueError):
            return default

    def get_float(self, key: str, default: float) -> float:
        try:
            return float(self.get(key, str(default)))
        except (TypeError, ValueError):
            return default

    def origen(self, key: str) -> str:
        return self._origen.get(key.upper(), "no definida")

    def definida(self, key: str) -> bool:
        value = self.get(key)
        return value is not None and value != "" and value != "<completar>"

    @property
    def timeout(self) -> float:
        return max(0.001, self.get_float("DIAG_TIMEOUT_SECONDS", 3.0))

    def secretos(self) -> list[str]:
        nombres = {
            var for p in PRODUCTOS.values() for var in p["secretos"]
        }
        nombres |= {
            key for key in self._values
            if any(t in key for t in ("PASSWORD", "TOKEN", "SECRET"))
        }
        valores = []
        for nombre in nombres:
            value = self._values.get(nombre)
            if value and len(value) >= 3:
                valores.append(value)
        return sorted(valores, key=len, reverse=True)

    def contenedor(self, producto: str) -> str:
        spec = PRODUCTOS[producto]
        return self.get(spec["contenedor_var"], spec["contenedor_def"])


def parse_overrides(items: Iterable[str] | None) -> dict[str, str]:
    result = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--set requiere CLAVE=VALOR (recibido: {item})")
        key, value = item.split("=", 1)
        result[key.strip().upper()] = value
    return result


def host_port_from_url(url: str, default_port: int) -> tuple[str, int]:
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or default_port
    return host, port


# --------------------------------------------------------------------------
# Redacción de secretos (RNF7, RNF8)
# --------------------------------------------------------------------------

_PATRONES = [
    (re.compile(r"(://[^:/\s@]+:)[^@\s]+@"), r"\1****@"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=\-]+"), r"\1****"),
    (re.compile(r"(?i)((?:password|passwd|pwd|token|secret)\s*[=:]\s*)[^\s,;'\"}]+"), r"\1****"),
    (re.compile(r"(?i)(--password\s+|-p\s+)\S+"), r"\1****"),
]


class Redactor:
    def __init__(self, secretos: Iterable[str]) -> None:
        self._secretos = [s for s in secretos if s]

    def __call__(self, texto: Any) -> str:
        if texto is None:
            return ""
        out = str(texto)
        for secreto in self._secretos:
            out = out.replace(secreto, "****")
        for patron, reemplazo in _PATRONES:
            out = patron.sub(reemplazo, out)
        return out


# --------------------------------------------------------------------------
# Modelo de resultado
# --------------------------------------------------------------------------

@dataclass
class Resultado:
    producto: str
    capa: str
    prueba: str
    objetivo: str
    estado: str
    clasificacion: str
    detalle: str = ""
    duracion_ms: float | None = None
    origen: str = "notebook (mismo entorno que la API)"
    cliente: str = ""
    requerida: bool = True
    pregunta: str = ""
    no_concluye: str = ""
    hipotesis: str = ""
    siguiente_paso: str = ""
    timestamp: str = field(default_factory=lambda: ahora_iso())

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


def ahora() -> datetime:
    return datetime.now(TZ) if TZ else datetime.now().astimezone()


def ahora_iso() -> str:
    return ahora().isoformat(timespec="seconds")


# Hipótesis y siguiente paso por clasificación (RNF10).
DIAGNOSTICO: dict[str, tuple[str, str]] = {
    "variables_faltantes": (
        "La configuración del entorno no define todas las variables del producto.",
        "Completar config/conectividad.env o el .env de la API a partir de config/configuracion-ejemplo.env.",
    ),
    "host_no_resuelto": (
        "El nombre de host no se puede resolver desde este entorno. Es típico usar el nombre de un servicio Docker "
        "(ej. 'mongodb') desde la notebook, donde ese nombre solo existe dentro de la red Compose.",
        "Desde la notebook usar 127.0.0.1 y el puerto publicado; dentro de la red Compose usar el nombre del servicio y el puerto interno.",
    ),
    "connection_refused": (
        "El host responde pero no hay un proceso escuchando en ese puerto: contenedor detenido, puerto no publicado, "
        "proceso aún iniciando o puerto equivocado.",
        "Revisar 'docker ps' y la columna PORTS; comparar con el puerto configurado; revisar 'docker logs <contenedor>'.",
    ),
    "timeout": (
        "No hubo respuesta dentro del límite: firewall, ruta inexistente, host equivocado o servicio saturado.",
        "Verificar host/IP, reglas de firewall y carga del contenedor; repetir con DIAG_TIMEOUT_SECONDS mayor solo para diagnosticar.",
    ),
    "red_inalcanzable": (
        "El sistema operativo no encuentra ruta hacia el host.",
        "Verificar la IP configurada y la conectividad de red del origen.",
    ),
    "protocolo_inesperado": (
        "Hay un listener en el puerto, pero no habla el protocolo esperado: probablemente es otro servicio (puerto incorrecto).",
        "Comparar el puerto con el mapeo de 'docker ps' y la documentación del producto (Bolt 7687, CQL 9042, RESP 6379, etc.).",
    ),
    "auth_fallida": (
        "La identidad configurada fue rechazada por el servidor.",
        "Verificar usuario, contraseña/token y base de autenticación en el .env local (sin publicarlos).",
    ),
    "auth_requerida_sin_credencial": (
        "El servidor exige autenticación y la configuración no provee credencial.",
        "Agregar la credencial en el .env local o ajustar la configuración del servidor de laboratorio.",
    ),
    "sin_permiso": (
        "La identidad se autenticó pero no tiene permisos sobre el contexto requerido.",
        "Revisar roles/privilegios del usuario sobre la database, keyspace o namespace.",
    ),
    "contexto_inexistente": (
        "El servidor responde y la identidad es válida, pero la database/keyspace/namespace configurado no existe.",
        "Verificar el nombre del contexto en la configuración y que la carga del hito correspondiente se haya ejecutado.",
    ),
    "tabla_inexistente": (
        "El contexto existe pero falta la colección/tabla/clase esperada.",
        "Ejecutar los scripts de creación del hito correspondiente.",
    ),
    "consulta_invalida": (
        "La consulta enviada no es válida para el motor (sintaxis o esquema).",
        "Revisar la consulta; no confundir con un problema de red.",
    ),
    "herramienta_no_disponible": (
        "El cliente o driver necesario no está instalado en este entorno.",
        "Instalar dependencias con 'pip install -r requirements.txt' o usar el cliente dentro del contenedor.",
    ),
    "dependencia_no_disponible": (
        "La API está viva pero el adaptador no pudo usar la dependencia.",
        "Correr el modo nativos para el producto y ubicar la capa que falla.",
    ),
    "dependencia_mal_configurada": (
        "La API alcanza la dependencia pero ésta rechaza la identidad o el contexto.",
        "Revisar la variable indicada en 'detalles.capa' en el .env de la API.",
    ),
    "api_no_alcanzable": (
        "No hay un proceso escuchando en la dirección de la API o la URL es incorrecta.",
        "Iniciar la API con scripts/reiniciar_api.ps1 y verificar API_BASE_URL.",
    ),
    "error_interno": (
        "La API produjo un error no controlado.",
        "Buscar el request_id en logs/api.stderr.log para ver la excepción.",
    ),
    "respuesta_inesperada": (
        "El status HTTP no coincide con el esperado para el caso.",
        "Comparar con la tabla de casos y revisar el log asociado al request_id.",
    ),
    "error_driver": (
        "El driver informó un error no clasificado automáticamente.",
        "Leer el detalle (redactado) y repetir la prueba aislando la capa.",
    ),
}


def completar_diagnostico(resultado: Resultado) -> Resultado:
    if resultado.estado in (FALLA, ADVERTENCIA) and not resultado.hipotesis:
        hip, paso = DIAGNOSTICO.get(
            resultado.clasificacion,
            DIAGNOSTICO["error_driver"],
        )
        resultado.hipotesis = hip
        resultado.siguiente_paso = paso
    return resultado


# --------------------------------------------------------------------------
# Clasificación de errores de red
# --------------------------------------------------------------------------

def clasificar_error_red(error: BaseException) -> str:
    texto = str(error).lower()

    if isinstance(error, socket.gaierror) or any(
        t in texto for t in (
            "name or service not known",
            "nodename nor servname",
            "getaddrinfo failed",
            "no address associated",
            "temporary failure in name resolution",
            "name resolution",
        )
    ):
        return "host_no_resuelto"

    if isinstance(error, ConnectionRefusedError) or any(
        t in texto for t in (
            "connection refused",
            "actively refused",
            "denegó",
            "errno 111",
            "10061",
        )
    ):
        return "connection_refused"

    if isinstance(error, (socket.timeout, TimeoutError)) or any(
        t in texto for t in ("timed out", "timeout", "tiempo de espera")
    ):
        return "timeout"

    if isinstance(error, OSError) and getattr(error, "errno", None) in (
        errno.ENETUNREACH,
        errno.EHOSTUNREACH,
    ):
        return "red_inalcanzable"

    if "unreachable" in texto:
        return "red_inalcanzable"

    return "error_driver"


def medir(fn: Callable[[], Any]) -> tuple[Any, float]:
    inicio = time.perf_counter()
    valor = fn()
    return valor, round((time.perf_counter() - inicio) * 1000, 2)


# --------------------------------------------------------------------------
# Cadena de capas: una capa requerida fallida bloquea las siguientes
# --------------------------------------------------------------------------

class Cadena:
    """Ejecuta pasos en orden de menor a mayor costo (sección 5.2).

    Cada paso devuelve ``(estado, clasificacion, detalle)``. Si un paso
    requerido termina en FALLA, los pasos requeridos posteriores se marcan
    BLOQUEADA (no se ejecutan y no se presentan como caídos). Los pasos no
    requeridos (pruebas negativas, portales) se ejecutan solo si la cadena
    llegó al menos hasta la capa que necesitan.
    """

    def __init__(
        self,
        producto: str,
        clasificador: Callable[[BaseException], str],
        redactar: Redactor,
        cliente: str,
        objetivo_base: str,
    ) -> None:
        self.producto = producto
        self.clasificador = clasificador
        self.redactar = redactar
        self.cliente = cliente
        self.objetivo_base = objetivo_base
        self.resultados: list[Resultado] = []
        self.bloqueada_por: str | None = None
        self.estado_compartido: dict[str, Any] = {}

    def paso(
        self,
        capa: str,
        prueba: str,
        fn: Callable[[], tuple[str, str, str]],
        pregunta: str,
        no_concluye: str,
        requerida: bool = True,
        objetivo: str | None = None,
        cliente: str | None = None,
        necesita_cadena: bool = True,
    ) -> Resultado:
        objetivo = objetivo or self.objetivo_base

        if self.bloqueada_por and (requerida or necesita_cadena):
            resultado = Resultado(
                producto=self.producto,
                capa=capa,
                prueba=prueba,
                objetivo=objetivo,
                estado=BLOQUEADA,
                clasificacion="bloqueada_por_capa_previa",
                detalle=f"No se ejecutó: falló la capa '{self.bloqueada_por}'.",
                cliente=cliente or self.cliente,
                requerida=requerida,
                pregunta=pregunta,
                no_concluye=no_concluye,
            )
            self.resultados.append(resultado)
            return resultado

        inicio = time.perf_counter()

        try:
            estado, clasificacion, detalle = fn()
        except Exception as error:  # noqa: BLE001
            estado = FALLA
            clasificacion = self.clasificador(error)
            detalle = f"{type(error).__name__}: {error}"

        duracion = round((time.perf_counter() - inicio) * 1000, 2)

        resultado = completar_diagnostico(
            Resultado(
                producto=self.producto,
                capa=capa,
                prueba=prueba,
                objetivo=self.redactar(objetivo),
                estado=estado,
                clasificacion=clasificacion,
                detalle=self.redactar(detalle)[:900],
                duracion_ms=duracion,
                cliente=cliente or self.cliente,
                requerida=requerida,
                pregunta=pregunta,
                no_concluye=no_concluye,
            )
        )

        if requerida and estado == FALLA and not self.bloqueada_por:
            self.bloqueada_por = capa

        self.resultados.append(resultado)
        return resultado

    def omitir_todo(self, motivo: str, clasificacion: str, capas: list[tuple[str, str]]) -> None:
        for capa, prueba in capas:
            self.resultados.append(
                completar_diagnostico(
                    Resultado(
                        producto=self.producto,
                        capa=capa,
                        prueba=prueba,
                        objetivo=self.objetivo_base,
                        estado=SKIP,
                        clasificacion=clasificacion,
                        detalle=motivo,
                        cliente=self.cliente,
                    )
                )
            )


# --------------------------------------------------------------------------
# Contexto de ejecución y trazabilidad (RNF3, RNF18)
# --------------------------------------------------------------------------

def en_contenedor() -> bool:
    if Path("/.dockerenv").exists():
        return True
    try:
        return "docker" in Path("/proc/1/cgroup").read_text()
    except Exception:
        return False


def git_info() -> dict[str, str]:
    def run(*args: str) -> str:
        try:
            out = subprocess.run(
                ["git", *args],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return out.stdout.strip() if out.returncode == 0 else ""
        except Exception:
            return ""

    commit = run("rev-parse", "--short", "HEAD") or "desconocido"
    rama = run("rev-parse", "--abbrev-ref", "HEAD") or "desconocida"
    sucio = run("status", "--porcelain", "--untracked-files=no")

    return {
        "commit": commit + (" (con cambios sin commit)" if sucio else ""),
        "rama": rama,
    }


def contexto_ejecucion(cfg: Config, modo: str) -> dict[str, Any]:
    contenedor = en_contenedor()
    entorno = cfg.get("DIAG_ENTORNO") or (
        "contenedor Docker" if contenedor else
        f"notebook del equipo ({platform.system()}), proceso Python local"
    )
    info = git_info()
    return {
        "hito": "Hito 11 - Evaluación de la conectividad",
        "fecha": ahora_iso(),
        "modo": modo,
        "entorno": entorno,
        "origen_de_las_pruebas": (
            "dentro de un contenedor" if contenedor else
            "notebook (mismo proceso/entorno desde el que corre la API)"
        ),
        "sistema_operativo": platform.platform(terse=True),
        "python": platform.python_version(),
        "commit": info["commit"],
        "rama": info["rama"],
        "timeout_por_prueba_s": cfg.timeout,
        "archivos_de_configuracion": {
            "config/conectividad.env": "presente" if CONFIG_LOCAL.exists() else "ausente",
            ".env (API)": "presente" if CONFIG_API.exists() else "ausente",
        },
    }


def version_paquete(nombre: str) -> str:
    try:
        from importlib.metadata import version

        return version(nombre)
    except Exception:
        return "no instalado"


def docker_disponible() -> bool:
    try:
        out = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        return out.returncode == 0
    except Exception:
        return False


def docker_contenedores() -> dict[str, str]:
    """Nombre -> imagen de los contenedores en ejecución."""
    try:
        out = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Image}}"],
            capture_output=True,
            text=True,
            timeout=8,
        )
    except Exception:
        return {}
    if out.returncode != 0:
        return {}
    result = {}
    for line in out.stdout.splitlines():
        if "|" in line:
            name, image = line.split("|", 1)
            result[name.strip()] = image.strip()
    return result


def resolver_contenedor(cfg: Config, producto: str, activos: dict[str, str] | None = None) -> str | None:
    """Devuelve el contenedor configurado o lo detecta por imagen."""
    activos = activos if activos is not None else docker_contenedores()
    configurado = cfg.contenedor(producto)
    if configurado in activos:
        return configurado
    imagen = PRODUCTOS[producto]["imagen"]
    for name, image in activos.items():
        if image.split(":")[0].endswith(imagen) or image.startswith(imagen):
            return name
    return None


# --------------------------------------------------------------------------
# Agregación de estados por producto
# --------------------------------------------------------------------------

def estado_producto(resultados: list[Resultado]) -> tuple[str, str]:
    """Devuelve (estado agregado, motivo)."""
    if not resultados:
        return NO_PROBADO, "sin pruebas ejecutadas"

    if resultados[0].producto == "Repositorio":
        if any(r.estado == FALLA for r in resultados):
            return "no cumple", "hay archivos con secretos versionados"
        return "cumple", "archivos con secretos ignorados por Git"

    if any(
        r.capa == "configuracion" and r.clasificacion == "variables_faltantes"
        for r in resultados
    ):
        return NO_CONFIGURADO, "faltan variables de configuración"

    requeridas = [r for r in resultados if r.requerida]
    fallas = [r for r in requeridas if r.estado == FALLA]

    if fallas:
        primera = fallas[0]
        return NO_DISPONIBLE, f"falló la capa {primera.capa} ({primera.clasificacion})"

    operacion_ok = any(
        r.capa in ("operacion", "api") and r.estado in (OK, ADVERTENCIA) and r.requerida
        for r in resultados
    )

    secundarias_mal = [
        r for r in resultados
        if (not r.requerida and r.estado == FALLA) or r.estado == ADVERTENCIA
    ]

    if operacion_ok and secundarias_mal:
        r = secundarias_mal[0]
        return DEGRADADO, f"operación correcta, pero {r.prueba}: {r.clasificacion}"

    if operacion_ok:
        return DISPONIBLE, "todas las capas requeridas probadas terminaron OK"

    ejecutadas = [r for r in requeridas if r.estado not in (SKIP, BLOQUEADA)]
    if not ejecutadas:
        return NO_PROBADO, "pruebas omitidas (SKIP) por falta de herramienta o configuración"

    return DESCONOCIDO, "las capas ejecutadas no alcanzan para concluir"


# --------------------------------------------------------------------------
# Salida por consola y evidencias
# --------------------------------------------------------------------------

def imprimir_resultado(r: Resultado) -> None:
    dur = f"{r.duracion_ms:.1f} ms" if r.duracion_ms is not None else "-"
    marca = "" if r.requerida else " (complementaria)"
    print(
        f"[{r.estado:<11}] {r.producto:<17} | {r.capa:<13} | "
        f"{r.prueba}{marca} | {r.clasificacion} | {dur}"
    )
    if r.detalle:
        print(f"{'':16}-> {r.detalle}")
    if r.estado in (FALLA, ADVERTENCIA) and r.siguiente_paso:
        print(f"{'':16}   siguiente paso: {r.siguiente_paso}")


def resumen_por_producto(resultados: list[Resultado]) -> dict[str, dict[str, Any]]:
    grupos: dict[str, list[Resultado]] = {}
    for r in resultados:
        grupos.setdefault(r.producto, []).append(r)

    resumen = {}
    for producto, items in grupos.items():
        estado, motivo = estado_producto(items)
        conteo: dict[str, int] = {}
        for r in items:
            conteo[r.estado] = conteo.get(r.estado, 0) + 1
        resumen[producto] = {
            "estado": estado,
            "motivo": motivo,
            "conteo": conteo,
        }
    return resumen


def imprimir_resumen(resultados: list[Resultado]) -> None:
    print()
    print("=== RESUMEN DE ESTADOS POR PRODUCTO ===")
    for producto, info in resumen_por_producto(resultados).items():
        conteo = ", ".join(f"{k}={v}" for k, v in sorted(info["conteo"].items()))
        print(f"  {producto:<18} {info['estado'].upper():<15} {info['motivo']}  [{conteo}]")
    print()
    print("Referencias: OK = esa prueba concreta funcionó (no garantiza rendimiento ni disponibilidad permanente).")
    print("             SKIP = prueba no ejecutada por falta de herramienta o configuración, NO producto caído.")
    print("             BLOQUEADA = no se ejecutó porque falló una capa anterior.")


def escribir_evidencia(
    nombre: str,
    contexto: dict[str, Any],
    resultados: list[Resultado],
    redactar: Redactor,
    etiqueta: str = "",
    extra: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    EVIDENCIA_DIR.mkdir(parents=True, exist_ok=True)
    sufijo = f"_{etiqueta}" if etiqueta else ""
    json_path = EVIDENCIA_DIR / f"{nombre}{sufijo}.json"
    txt_path = EVIDENCIA_DIR / f"{nombre}{sufijo}.txt"

    payload = {
        "contexto": contexto,
        "resumen": resumen_por_producto(resultados),
        "resultados": [r.como_dict() for r in resultados],
    }
    if extra:
        payload.update(extra)

    texto_json = redactar(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    json_path.write_text(texto_json + "\n", encoding="utf-8")

    lineas = [f"=== {contexto['hito'].upper()} - {nombre.upper()} ==="]
    for clave, valor in contexto.items():
        if clave == "hito":
            continue
        lineas.append(f"{clave}: {valor}")
    lineas.append("")
    for r in resultados:
        dur = f"{r.duracion_ms:.1f} ms" if r.duracion_ms is not None else "-"
        comp = "" if r.requerida else " (complementaria)"
        lineas.append(
            f"[{r.estado}] {r.timestamp} | {r.producto} | {r.capa} | {r.prueba}{comp} | "
            f"objetivo={r.objetivo} | cliente={r.cliente} | {r.clasificacion} | {dur}"
        )
        if r.detalle:
            lineas.append(f"    detalle: {r.detalle}")
        if r.pregunta:
            lineas.append(f"    responde: {r.pregunta}")
        if r.no_concluye:
            lineas.append(f"    no permite concluir: {r.no_concluye}")
        if r.hipotesis:
            lineas.append(f"    hipotesis: {r.hipotesis}")
            lineas.append(f"    siguiente paso: {r.siguiente_paso}")
    lineas.append("")
    lineas.append("=== RESUMEN ===")
    for producto, info in resumen_por_producto(resultados).items():
        lineas.append(f"{producto}: {info['estado']} - {info['motivo']} {info['conteo']}")

    txt_path.write_text(redactar("\n".join(lineas)) + "\n", encoding="utf-8")
    return txt_path, json_path

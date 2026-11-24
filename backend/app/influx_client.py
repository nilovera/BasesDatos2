import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import settings
from .errors import DomainError


class InfluxHttpClient:
    def __init__(self, base_url, token_file, timeout_seconds):
        self.base_url = base_url.rstrip("/")
        self.token_file = Path(token_file)
        self.timeout_seconds = timeout_seconds
        self._cached_token = None

    def _token(self):
        if self._cached_token is None:
            try:
                token = self.token_file.read_text(encoding="utf-8").strip()
            except OSError as error:
                raise DomainError(
                    503,
                    "TELEMETRY_STORE_UNAVAILABLE",
                    "No se pudo leer la credencial local de InfluxDB",
                ) from error
            if not token.startswith("apiv3_"):
                raise DomainError(
                    503,
                    "TELEMETRY_STORE_UNAVAILABLE",
                    "La credencial local de InfluxDB no es valida",
                )
            self._cached_token = token
        return self._cached_token

    def _request(self, method, path, body=None, content_type=None):
        headers = {"Authorization": f"Bearer {self._token()}"}
        if content_type:
            headers["Content-Type"] = content_type
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            raise DomainError(
                503,
                "TELEMETRY_STORE_UNAVAILABLE",
                "InfluxDB no pudo completar la operacion",
            ) from error

    def health(self):
        try:
            self._request("GET", "/health")
        except DomainError:
            return "DOWN"
        return "UP"

    def write_lines(self, database, lines):
        if not lines:
            return
        query = urlencode(
            {
                "db": database,
                "precision": "nanosecond",
                "accept_partial": "false",
            }
        )
        payload = ("\n".join(lines) + "\n").encode("utf-8")
        self._request(
            "POST",
            f"/api/v3/write_lp?{query}",
            payload,
            "text/plain; charset=utf-8",
        )

    def query(self, database, sql):
        payload = json.dumps(
            {"db": database, "q": sql, "format": "jsonl"},
            separators=(",", ":"),
        ).encode("utf-8")
        raw = self._request(
            "POST", "/api/v3/query_sql", payload, "application/json"
        ).strip()
        if not raw:
            return []
        if raw.startswith("["):
            result = json.loads(raw)
            return result if isinstance(result, list) else [result]
        return [json.loads(line) for line in raw.splitlines() if line.strip()]


_client = None


def get_influx_client():
    global _client
    if _client is None:
        _client = InfluxHttpClient(
            settings.influxdb_url,
            settings.influxdb_token_file,
            settings.influxdb_timeout_seconds,
        )
    return _client


def close_influx_client():
    global _client
    _client = None

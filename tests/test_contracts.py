import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = ROOT / "backend" / "openapi.json"
MONGO_SCHEMA_PATH = ROOT / "mongodb" / "init" / "01_schema.js"
MONGO_SEED_PATH = ROOT / "mongodb" / "init" / "02_seed_catalogo.js"
COMPOSE_PATH = ROOT / "docker-compose.yml"
START_SCRIPT_PATH = ROOT / "scripts" / "iniciar_mongodb.ps1"
VERIFY_SCRIPT_PATH = ROOT / "scripts" / "verificar_mongodb.ps1"


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.openapi = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
        cls.mongo_schema = MONGO_SCHEMA_PATH.read_text(encoding="utf-8")
        cls.mongo_seed = MONGO_SEED_PATH.read_text(encoding="utf-8")
        cls.compose = COMPOSE_PATH.read_text(encoding="utf-8")

    def test_openapi_is_valid_json_and_uses_31(self):
        self.assertEqual("3.1.0", self.openapi["openapi"])
        self.assertEqual("Fixture 2030 API", self.openapi["info"]["title"])

    def test_event_write_requires_idempotency_key(self):
        post = self.openapi["paths"]["/api/v1/partidos/{partidoId}/eventos"]["post"]
        parameter = next(
            item for item in post["parameters"] if item.get("name") == "Idempotency-Key"
        )
        self.assertEqual("Idempotency-Key", parameter["name"])
        self.assertEqual("header", parameter["in"])
        self.assertTrue(parameter["required"])

    def test_event_contract_contains_first_vertical_flow(self):
        variants = self.openapi["paths"]["/api/v1/partidos/{partidoId}/eventos"]["post"][
            "requestBody"
        ]["content"]["application/json"]["schema"]["oneOf"]
        names = {item["$ref"].rsplit("/", 1)[-1] for item in variants}
        self.assertEqual(
            {
                "InicioPartidoCommand",
                "GolCommand",
                "SustitucionCommand",
                "CorreccionEventoCommand",
            },
            names,
        )

    def test_event_write_documents_new_replay_conflict_and_failure(self):
        responses = self.openapi["paths"]["/api/v1/partidos/{partidoId}/eventos"]["post"]["responses"]
        self.assertTrue({"200", "201", "400", "404", "409", "422", "503"}.issubset(responses))
        replay = responses["200"]["headers"]["Idempotency-Replayed"]["schema"]
        self.assertIs(replay["const"], True)

    def test_event_pagination_uses_sequence_cursor(self):
        get = self.openapi["paths"]["/api/v1/partidos/{partidoId}/eventos"]["get"]
        query_names = {
            parameter["name"]
            for parameter in get["parameters"]
            if parameter.get("in") == "query"
        }
        self.assertEqual({"desdeSecuencia", "limite"}, query_names)

    def test_session_contract_exposes_explicit_renewal(self):
        paths = self.openapi["paths"]
        self.assertIn("/api/v1/sesiones", paths)
        self.assertIn("post", paths["/api/v1/sesiones"])
        self.assertIn("get", paths["/api/v1/sesiones/{sesionId}"])
        self.assertIn("delete", paths["/api/v1/sesiones/{sesionId}"])
        renewal = paths["/api/v1/sesiones/{sesionId}/renovacion"]["post"]
        schema = renewal["requestBody"]["content"]["application/json"]["schema"]
        self.assertEqual("#/components/schemas/SesionRenovacion", schema["$ref"])

    def test_match_read_documents_cache_result_header(self):
        response = self.openapi["paths"]["/api/v1/partidos/{partidoId}"]["get"][
            "responses"
        ]["200"]
        header = response["headers"]["X-Cache"]["schema"]
        self.assertEqual(["HIT", "MISS", "BYPASS"], header["enum"])

    def test_mongodb_schema_has_authoritative_collections_and_unique_guards(self):
        for collection in (
            "equipos",
            "jugadores",
            "partidos",
            "eventos_oficiales",
            "outbox",
            "contadores",
        ):
            self.assertIn(f'ensureCollection("{collection}"', self.mongo_schema)

        for index_name in (
            "uq_eventos_eventoId",
            "uq_eventos_partido_secuencia",
            "uq_eventos_idempotencia",
            "uq_outbox_eventoId",
        ):
            self.assertIn(index_name, self.mongo_schema)

        self.assertIn('partialFilterExpression: { estado: "PUBLICADO"', self.mongo_schema)

    def test_executable_increment_contains_no_iris_dependency(self):
        files = [
            OPENAPI_PATH,
            MONGO_SCHEMA_PATH,
            MONGO_SEED_PATH,
            COMPOSE_PATH,
            ROOT / "scripts" / "catalogo.py",
        ]
        for path in files:
            self.assertNotIn("iris", path.read_text(encoding="utf-8").lower(), path)

    def test_compose_uses_local_single_member_replica_set(self):
        self.assertIn("--replSet", self.compose)
        self.assertIn("rs0", self.compose)
        self.assertIn('127.0.0.1:27017:27017', self.compose)
        self.assertIn("00_replica_init.js", self.compose)
        self.assertIn("03_verify.js", self.compose)

    def test_compose_passes_init_pipeline_as_one_bash_argument(self):
        self.assertIn('entrypoint: ["/bin/bash", "-lc"]', self.compose)
        self.assertIn("command:\n      - |", self.compose)
        self.assertIn(
            "mongodb://mongo:27017/?directConnection=true",
            self.compose,
        )

    def test_powershell_scripts_reject_native_command_failures(self):
        for path in (START_SCRIPT_PATH, VERIFY_SCRIPT_PATH):
            script = path.read_text(encoding="utf-8")
            self.assertIn("$LASTEXITCODE -ne 0", script, path)
            self.assertIn("throw", script, path)

    def test_seed_is_idempotent_and_uses_reference_catalog(self):
        self.assertIn("bulkWrite", self.mongo_seed)
        self.assertIn("upsert: true", self.mongo_seed)
        self.assertIn("equipos.length !== 64", self.mongo_seed)
        self.assertIn("jugadores.length !== 1024", self.mongo_seed)
        self.assertIn('readJson("equipos.json")', self.mongo_seed)

    def test_deferred_integration_tasks_are_registered(self):
        backlog = (ROOT / "docs" / "tareas_integracion_final.md").read_text(encoding="utf-8")
        for task in ("Usuarios sintéticos", "Asistencias", "Telemetría", "Simulador", "Escenarios de carga", "SLI, SLO y SLA"):
            self.assertIn(task, backlog)


if __name__ == "__main__":
    unittest.main()

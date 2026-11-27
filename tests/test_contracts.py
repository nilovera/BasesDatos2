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
    def test_datamart_contract_exposes_refresh_summary_and_comparison(self):
        contract = json.loads((ROOT / "backend" / "openapi.json").read_text(encoding="utf-8"))
        paths = contract["paths"]
        for path in (
            "/api/v1/analitica/datamart/refrescar",
            "/api/v1/analitica/datamart/resumen",
            "/api/v1/analitica/datamart/goles-por-equipo",
            "/api/v1/analitica/operacional/goles-por-equipo",
        ):
            self.assertIn(path, paths)

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
                "TarjetaCommand",
                "GolAnuladoVarCommand",
                "FinPartidoCommand",
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

    def test_comment_contract_exposes_query_views_and_moderation(self):
        paths = self.openapi["paths"]
        match_path = "/api/v1/partidos/{partidoId}/comentarios"
        user_path = "/api/v1/usuarios/{usuarioId}/comentarios"
        moderation_path = "/api/v1/comentarios/{comentarioId}/moderacion"
        self.assertIn("post", paths[match_path])
        self.assertIn("get", paths[match_path])
        self.assertIn("get", paths[user_path])
        self.assertIn("patch", paths[moderation_path])
        parameter = next(
            item for item in paths[match_path]["post"]["parameters"]
            if item.get("name") == "Idempotency-Key"
        )
        self.assertTrue(parameter["required"])
        query_names = {
            item["name"] for item in paths[match_path]["get"]["parameters"]
            if item.get("in") == "query"
        }
        self.assertEqual({"bucket", "antesDe", "limite", "incluirOcultos"}, query_names)
        cursor_parameter = next(
            item for item in paths[match_path]["get"]["parameters"]
            if item.get("name") == "antesDe"
        )
        cursor_types = {
            variant.get("type") for variant in cursor_parameter["schema"]["anyOf"]
        }
        self.assertEqual({"string", "null"}, cursor_types)
        self.assertIn("Cursor opaco", cursor_parameter["description"])
        response_cursor = self.openapi["components"]["schemas"]["PaginaComentarios"][
            "properties"
        ]["siguienteCursor"]
        self.assertNotIn("format", response_cursor["anyOf"][0])

    def test_telemetry_contract_exposes_batch_cursor_heatmap_and_history(self):
        paths = self.openapi["paths"]
        positions = "/api/v1/partidos/{partidoId}/telemetria/posiciones"
        statistics = "/api/v1/partidos/{partidoId}/telemetria/estadisticas-equipos"
        heatmap = "/api/v1/partidos/{partidoId}/jugadores/{jugadorId}/mapa-calor"
        aggregation = "/api/v1/partidos/{partidoId}/telemetria/agregaciones/15m"
        summaries = "/api/v1/partidos/{partidoId}/telemetria/resumenes-equipos/15m"
        for path in (positions, statistics, heatmap, aggregation, summaries):
            self.assertIn(path, paths)
        self.assertIn("post", paths[positions])
        self.assertIn("get", paths[positions])
        query_names = {
            parameter["name"]
            for parameter in paths[positions]["get"]["parameters"]
            if parameter.get("in") == "query"
        }
        self.assertEqual(
            {"jugadorId", "desde", "hasta", "cursor", "limite"}, query_names
        )
        cursor = next(
            parameter for parameter in paths[positions]["get"]["parameters"]
            if parameter["name"] == "cursor"
        )
        self.assertIn("null", {item.get("type") for item in cursor["schema"]["anyOf"]})
        self.assertEqual("0.10.0", self.openapi["info"]["version"])

    def test_simulator_contract_exposes_controls_and_ball(self):
        paths = self.openapi["paths"]
        for path in (
            "/api/v1/simulaciones",
            "/api/v1/simulaciones/{simulacionId}",
            "/api/v1/simulaciones/{simulacionId}/iniciar",
            "/api/v1/simulaciones/{simulacionId}/pausar",
            "/api/v1/simulaciones/{simulacionId}/reanudar",
            "/api/v1/simulaciones/{simulacionId}/velocidad",
            "/api/v1/partidos/{partidoId}/telemetria/pelota",
        ):
            self.assertIn(path, paths)
        schemas = json.dumps(self.openapi["components"]["schemas"], ensure_ascii=False)
        for event_type in ("TARJETA", "GOL_ANULADO_VAR", "FIN_PARTIDO"):
            self.assertIn(event_type, schemas)

    def test_graph_contract_exposes_summary_rivals_recommendations_and_path(self):
        paths = self.openapi["paths"]
        expected = (
            "/api/v1/grafo/resumen",
            "/api/v1/grafo/equipos/{equipoId}/rivales",
            "/api/v1/grafo/jugadores/{jugadorId}/recomendaciones",
            "/api/v1/grafo/equipos/{origenId}/camino/{destinoId}",
        )
        for path in expected:
            self.assertIn(path, paths)
            self.assertIn("get", paths[path])
        self.assertEqual("0.10.0", self.openapi["info"]["version"])

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
            "simulaciones",
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

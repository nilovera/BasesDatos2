import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "simulador_carga.py"
SPEC = importlib.util.spec_from_file_location("simulador_carga", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LoadSimulatorTests(unittest.TestCase):
    def setUp(self):
        self.config = MODULE.load_config(ROOT / "config" / "carga" / "perfiles.json")

    def test_profiles_have_distinct_reproducible_seeds(self):
        profiles = self.config["profiles"]
        self.assertEqual(2030, profiles["normal"]["seed"])
        self.assertEqual(3, profiles["normal"]["repetitions"])
        self.assertEqual(3, len({item["seed"] for item in profiles.values()}))

    def test_load_increases_from_smoke_to_stress(self):
        profiles = self.config["profiles"]
        for key in ("concurrency", "targetRps"):
            self.assertLess(profiles["humo"][key], profiles["normal"][key])
            self.assertLess(profiles["normal"][key], profiles["estres"][key])

    def test_operation_mix_is_safe_and_covers_all_stores(self):
        operations = self.config["operations"]
        self.assertEqual(100, sum(item["weight"] for item in operations))
        paths = "\n".join(item["path"] for item in operations)
        for fragment in ("comentarios", "telemetria", "grafo", "datamart", "partidos"):
            self.assertIn(fragment, paths)
        self.assertTrue(all(item.get("method", "GET") == "GET" for item in operations))

    def test_percentiles_and_resource_units_are_deterministic(self):
        self.assertEqual(3, MODULE.percentile([5, 1, 4, 2, 3], 0.50))
        self.assertEqual(4, MODULE.percentile([5, 1, 4, 2, 3], 0.95))
        self.assertEqual(512, MODULE.parse_size_mib("512MiB"))
        self.assertEqual(1024, MODULE.parse_size_mib("1GiB"))

    def test_stress_is_informational_and_normal_has_slo(self):
        self.assertIsNone(self.config["profiles"]["estres"]["slo"])
        normal = self.config["profiles"]["normal"]["slo"]
        self.assertEqual(1.0, normal["maxErrorRatePct"])
        self.assertTrue(MODULE.evaluate_slo({"errorRatePct": 0, "p95Ms": 100, "p99Ms": 200}, normal)["passed"])

    def test_previous_load_evidence_does_not_block_next_profile(self):
        status = "\n".join(
            [
                "?? evidencia/ejecuciones/carga-humo-20300101T000000Z/resultado.json",
                " M scripts/simulador_carga.py",
            ]
        )
        self.assertEqual(
            [" M scripts/simulador_carga.py"], MODULE.blocking_git_changes(status)
        )

    def test_wrapper_rejects_native_failures(self):
        wrapper = (ROOT / "scripts" / "probar_carga.ps1").read_text(encoding="utf-8")
        self.assertIn("$LASTEXITCODE -ne 0", wrapper)
        self.assertIn('ValidateSet("humo", "normal", "estres", "todos")', wrapper)

    def test_documentation_does_not_present_slo_as_sla(self):
        document = (ROOT / "docs" / "rendimiento" / "pruebas_carga_sla_slo.md").read_text(encoding="utf-8")
        self.assertIn("no SLA contractual", document)
        self.assertIn("código y configuración estén versionados", document)
        self.assertIn("escrituras sintéticas", document)


if __name__ == "__main__":
    unittest.main()

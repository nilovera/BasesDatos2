import ast
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DataMartServiceTests(unittest.TestCase):
    def test_schema_separates_two_fact_grains(self):
        schema = (ROOT / "datamart" / "init" / "01_schema.sql").read_text(encoding="utf-8")
        self.assertIn("fact_evento_partido", schema)
        self.assertIn("fact_estadistica_equipo_15m", schema)
        self.assertIn("PRIMARY KEY (partido_key, equipo_key, ventana_inicio)", schema)
        self.assertIn("evento_id text PRIMARY KEY", schema)

    def test_schema_has_conformed_dimensions_and_indexes(self):
        schema = (ROOT / "datamart" / "init" / "01_schema.sql").read_text(encoding="utf-8")
        for dimension in ("dim_fecha", "dim_torneo", "dim_equipo", "dim_jugador", "dim_partido", "dim_tipo_evento"):
            self.assertIn(dimension, schema)
        self.assertIn("ix_fact_evento_partido_fecha_tipo", schema)

    def test_etl_uses_upserts_and_audit_table(self):
        service = (ROOT / "backend" / "app" / "datamart_service.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(service.count("ON CONFLICT"), 7)
        self.assertIn("etl_ejecucion", service)
        self.assertIn("eventos_cargados", service)
        ast.parse(service)

    def test_snapshot_resolves_corrections_before_projection(self):
        repository = (ROOT / "backend" / "app" / "repository.py").read_text(encoding="utf-8")
        self.assertIn("def datamart_snapshot", repository)
        self.assertIn('event["eventoId"] in corrected', repository)
        self.assertIn('data.get("reemplazo")', repository)

    def test_runtime_is_isolated_from_official_write_path(self):
        repository = (ROOT / "backend" / "app" / "repository.py").read_text(encoding="utf-8")
        register = repository.split("def register_event", 1)[1].split("def pending_outbox", 1)[0]
        self.assertNotIn("datamart", register.lower())

    def test_comparison_script_reports_percentiles_and_warning(self):
        script = (ROOT / "scripts" / "comparar_rendimiento_datamart.ps1").read_text(encoding="utf-8")
        for percentile in ("p50Ms", "p95Ms", "p99Ms"):
            self.assertIn(percentile, script)
        self.assertIn("no demuestra por si sola", script)


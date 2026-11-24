import ast
import unittest
from datetime import datetime, timezone
from pathlib import Path

from backend.app.cassandra_service import day_bucket, ensure_utc, minute_bucket, stable_shard


ROOT = Path(__file__).resolve().parents[1]


class CassandraServiceTests(unittest.TestCase):
    def test_buckets_are_utc_and_reproducible(self):
        value = datetime(2030, 6, 13, 20, 5, 59, tzinfo=timezone.utc)
        self.assertEqual("203006132005", minute_bucket(value))
        self.assertEqual("20300613", day_bucket(value))

    def test_shard_is_stable_and_bounded(self):
        first = stable_shard("USR-0003", 4)
        self.assertEqual(first, stable_shard("USR-0003", 4))
        self.assertIn(first, range(4))

    def test_naive_cassandra_timestamp_is_exposed_as_utc(self):
        value = datetime(2030, 6, 13, 20, 5, 59)
        normalized = ensure_utc(value)
        self.assertEqual(timezone.utc, normalized.tzinfo)
        self.assertEqual("2030-06-13T20:05:59+00:00", normalized.isoformat())

    def test_schema_models_each_query_without_filtering(self):
        schema = (ROOT / "cassandra" / "init" / "01_schema.cql").read_text(encoding="utf-8")
        self.assertIn("comments_by_match_bucket_shard", schema)
        self.assertIn("PRIMARY KEY ((match_id, bucket, shard), created_at, comment_id)", schema)
        self.assertIn("comments_by_user_day", schema)
        self.assertIn("PRIMARY KEY ((user_id, day_bucket), created_at, comment_id)", schema)
        self.assertNotIn("ALLOW FILTERING", schema.upper())

    def test_service_uses_lwt_and_bounded_logged_batches(self):
        source = (ROOT / "backend" / "app" / "cassandra_service.py").read_text(encoding="utf-8")
        self.assertIn("IF NOT EXISTS", source)
        self.assertIn("BatchType.LOGGED", source)
        self.assertIn("ConsistencyLevel.LOCAL_ONE", source)
        self.assertNotIn("ALLOW FILTERING", source.upper())
        ast.parse(source)

    def test_failure_script_recovers_only_cassandra(self):
        script = (ROOT / "scripts" / "probar_falla_cassandra.ps1").read_text(encoding="utf-8")
        self.assertIn("finally {", script)
        self.assertIn("docker stop fixture2030-cassandra", script)
        self.assertIn("docker start fixture2030-cassandra", script)
        self.assertNotIn("down -v", script.lower())

    def test_powershell_counts_pipeline_results_as_arrays(self):
        script = (ROOT / "scripts" / "probar_comentarios_cassandra.ps1").read_text(encoding="utf-8")
        self.assertGreaterEqual(script.count("@($"), 4)


if __name__ == "__main__":
    unittest.main()

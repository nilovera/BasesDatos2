import ast
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

from backend.app.cassandra_service import (
    CassandraCommentService,
    day_bucket,
    decode_cursor,
    encode_cursor,
    ensure_utc,
    minute_bucket,
    stable_shard,
)
from backend.app.errors import DomainError


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
        self.assertIn("comment_id > %s", source)
        self.assertIn("encode_cursor", source)
        self.assertNotIn("created_at < %s LIMIT %s", source)
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

    def test_opaque_cursor_preserves_timestamp_and_comment_id(self):
        created_at = datetime(2030, 6, 13, 20, 5, 59, tzinfo=timezone.utc)
        comment_id = UUID("00000000-0000-0000-0000-000000000002")
        cursor = encode_cursor(created_at, comment_id)
        decoded_at, decoded_id = decode_cursor(cursor)
        self.assertEqual(created_at, decoded_at)
        self.assertEqual(comment_id, decoded_id)
        self.assertNotIn("2030", cursor)

    def test_invalid_comment_cursor_is_rejected(self):
        with self.assertRaises(DomainError) as context:
            decode_cursor("cursor-invalido")
        self.assertEqual(400, context.exception.status)
        self.assertEqual("INVALID_COMMENT_CURSOR", context.exception.code)

    def test_page_cursor_does_not_skip_equal_timestamps(self):
        created_at = datetime(2030, 6, 13, 20, 5, 59, tzinfo=timezone.utc)
        rows = [
            SimpleNamespace(
                comment_id=UUID(int=value),
                match_id="PAR-0001",
                user_id=f"USR-{value:04d}",
                content=str(value),
                status="VISIBLE",
                created_at=created_at,
            )
            for value in (3, 1, 2)
        ]
        page = CassandraCommentService._page(rows, 2, False)
        self.assertEqual(
            [str(UUID(int=1)), str(UUID(int=2))],
            [item["comentarioId"] for item in page["items"]],
        )
        self.assertEqual(UUID(int=2), decode_cursor(page["siguienteCursor"])[1])

    def test_hidden_rows_do_not_exhaust_public_page(self):
        created_at = datetime(2030, 6, 13, 20, 5, 59, tzinfo=timezone.utc)
        rows = [
            SimpleNamespace(status=status, comment_id=UUID(int=index), created_at=created_at)
            for index, status in enumerate(
                ("OCULTO", "OCULTO", "OCULTO", "VISIBLE", "VISIBLE"), start=1
            )
        ]
        selected = CassandraCommentService._take_eligible([rows], 1, False)
        self.assertEqual(2, len(selected))
        self.assertTrue(all(row.status == "VISIBLE" for row in selected))


if __name__ == "__main__":
    unittest.main()

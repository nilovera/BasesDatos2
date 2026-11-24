import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeIncrementTests(unittest.TestCase):
    def test_backend_python_files_have_valid_syntax(self):
        for path in sorted((ROOT / "backend" / "app").glob("*.py")):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_direct_dependencies_are_pinned(self):
        requirements = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        for dependency in ("fastapi", "cassandra-driver", "pymongo", "prometheus-client", "redis", "uvicorn"):
            self.assertRegex(requirements, rf"(?m)^{dependency}==[^\s]+$")

    def test_compose_contains_api_prometheus_and_grafana(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        for service in ("  api:", "  prometheus:", "  grafana:"):
            self.assertIn(service, compose)
        self.assertIn("prom/prometheus:v3.16.0", compose)
        self.assertIn("grafana/grafana:13.3.1", compose)
        self.assertIn("127.0.0.1:8000:8000", compose)
        self.assertIn("127.0.0.1:3000:3000", compose)

    def test_api_transaction_writes_event_match_and_outbox(self):
        repository = (ROOT / "backend" / "app" / "repository.py").read_text(encoding="utf-8")
        self.assertIn("with_transaction", repository)
        self.assertIn("self.db.partidos.update_one", repository)
        self.assertIn("self.db.eventos_oficiales.insert_one", repository)
        self.assertIn("self.db.outbox.insert_one", repository)
        self.assertIn('WriteConcern("majority"', repository)

    def test_seed_does_not_reset_operational_matches(self):
        seed = (ROOT / "mongodb" / "init" / "02_seed_catalogo.js").read_text(encoding="utf-8")
        match_section = seed.split("db.partidos.bulkWrite", 1)[1]
        self.assertIn("$setOnInsert", match_section)
        self.assertNotIn("$set:", match_section)

    def test_prometheus_scrapes_the_api(self):
        config = (ROOT / "infra" / "prometheus" / "prometheus.yml").read_text(encoding="utf-8")
        self.assertIn("job_name: fixture2030-api", config)
        self.assertIn('targets: ["api:8000"]', config)

    def test_prometheus_loads_versioned_alert_rules(self):
        config = (ROOT / "infra" / "prometheus" / "prometheus.yml").read_text(encoding="utf-8")
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        rules = (
            ROOT / "infra" / "prometheus" / "rules" / "fixture2030-alerts.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("rule_files:", config)
        self.assertIn("/etc/prometheus/rules/*.yml", config)
        self.assertIn("./infra/prometheus/rules:/etc/prometheus/rules:ro", compose)
        for alert in (
            "Fixture2030ApiDown",
            "Fixture2030ApiHighErrorRate",
            "Fixture2030OutboxBacklog",
            "Fixture2030RedisDown",
            "Fixture2030RedisHighMemory",
            "Fixture2030RedisEvictions",
            "Fixture2030CassandraDown",
        ):
            self.assertIn(f"alert: {alert}", rules)
        self.assertIn("owner: plataforma", rules)
        self.assertIn("owner: backend", rules)
        self.assertIn("owner: integracion", rules)

    def test_monitoring_evidence_is_documented(self):
        expected = (
            "inventario_componentes.md",
            "metricas_y_consultas.md",
            "alertas_y_umbrales.md",
            "evidencia_y_limitaciones.md",
        )
        for filename in expected:
            self.assertTrue((ROOT / "docs" / "monitoreo" / filename).is_file(), filename)
        self.assertTrue((ROOT / "evidencia" / "README.md").is_file())
        queries = (ROOT / "docs" / "monitoreo" / "metricas_y_consultas.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('up{job="fixture2030-api"}', queries)
        self.assertIn("histogram_quantile(0.95", queries)

    def test_controlled_failure_always_recovers_api(self):
        script = (ROOT / "scripts" / "probar_falla_api.ps1").read_text(encoding="utf-8")
        self.assertIn("finally {", script)
        self.assertIn("docker stop fixture2030-api", script)
        self.assertIn("docker start fixture2030-api", script)
        self.assertIn('api/v1/alerts', script)
        self.assertIn('Fixture2030ApiDown', script)
        self.assertIn('"firing"', script)
        self.assertNotIn("down -v", script.lower())
        self.assertNotIn("docker rm", script.lower())

    def test_evidence_capture_does_not_dump_environment(self):
        script = (ROOT / "scripts" / "capturar_evidencia.ps1").read_text(encoding="utf-8")
        self.assertIn("git rev-parse HEAD", script)
        self.assertIn("api/v1/targets", script)
        self.assertIn("api/v1/rules", script)
        self.assertNotIn("Get-ChildItem Env:", script)
        self.assertNotIn("docker inspect", script)

    def test_grafana_dashboard_is_valid_and_provisioned(self):
        dashboard = json.loads(
            (ROOT / "infra" / "grafana" / "dashboards" / "fixture2030-api.json").read_text(encoding="utf-8")
        )
        self.assertEqual("fixture2030-api", dashboard["uid"])
        self.assertGreaterEqual(len(dashboard["panels"]), 10)
        datasource = (
            ROOT
            / "infra"
            / "grafana"
            / "provisioning"
            / "datasources"
            / "prometheus.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("url: http://prometheus:9090", datasource)

    def test_runtime_contains_no_iris_dependency(self):
        paths = list((ROOT / "backend" / "app").glob("*.py")) + [
            ROOT / "docker-compose.yml",
            ROOT / "infra" / "prometheus" / "prometheus.yml",
        ]
        for path in paths:
            self.assertNotIn("iris", path.read_text(encoding="utf-8").lower(), path)

    def test_redis_is_persistent_observable_and_memory_bounded(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        config = (ROOT / "redis" / "redis.conf").read_text(encoding="utf-8")
        prometheus = (ROOT / "infra" / "prometheus" / "prometheus.yml").read_text(
            encoding="utf-8"
        )
        for service in ("  redis:", "  redis-exporter:"):
            self.assertIn(service, compose)
        self.assertIn("fixture2030_redis_data:/data", compose)
        self.assertIn("maxmemory 256mb", config)
        self.assertIn("maxmemory-policy allkeys-lfu", config)
        self.assertIn("protected-mode no", config)
        self.assertIn("save 60 1", config)
        self.assertIn("appendonly yes", config)
        self.assertIn("appendfsync everysec", config)
        self.assertIn("job_name: fixture2030-redis", prometheus)
        self.assertIn('targets: ["redis-exporter:9121"]', prometheus)

    def test_redis_patterns_are_executable_and_safe(self):
        service = (ROOT / "backend" / "app" / "redis_service.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('f"cache:partido:{partido_id}"', service)
        self.assertIn("self.client.set", service)
        self.assertIn("self.client.delete", service)
        self.assertIn("self.client.eval", service)
        self.assertIn("pipeline.incr", service)
        self.assertIn("pipeline.zincrby", service)
        for script_name in (
            "verificar_redis.ps1",
            "probar_patrones_redis.ps1",
            "probar_persistencia_redis.ps1",
            "probar_falla_redis.ps1",
        ):
            script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
            self.assertNotIn("KEYS *", script.upper())
            self.assertNotIn("down -v", script.lower())

        failure_script = (ROOT / "scripts" / "probar_falla_redis.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("finally {", failure_script)
        self.assertIn("docker stop fixture2030-redis", failure_script)
        self.assertIn("docker start fixture2030-redis", failure_script)
        self.assertIn('"BYPASS"', failure_script)

    def test_cassandra_is_persistent_partitioned_and_observable(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        schema = (ROOT / "cassandra" / "init" / "01_schema.cql").read_text(encoding="utf-8")
        metrics = (ROOT / "backend" / "app" / "metrics.py").read_text(encoding="utf-8")
        for service in ("  cassandra:", "  cassandra-init:"):
            self.assertIn(service, compose)
        self.assertIn("cassandra:5.0.9", compose)
        self.assertIn("fixture2030_cassandra_data:/var/lib/cassandra", compose)
        self.assertIn("/opt/cassandra/bin/cqlsh cassandra 9042", compose)
        self.assertIn("comments_by_match_bucket_shard", schema)
        self.assertIn("comments_by_user_day", schema)
        self.assertNotIn("ALLOW FILTERING", schema.upper())
        self.assertIn("fixture2030_dependency_up", metrics)

    def test_cassandra_scripts_are_safe_and_recoverable(self):
        for name in ("verificar_cassandra.ps1", "probar_comentarios_cassandra.ps1", "probar_falla_cassandra.ps1"):
            source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            self.assertNotIn("down -v", source.lower())
            self.assertNotIn("ALLOW FILTERING", source.upper())
        failure = (ROOT / "scripts" / "probar_falla_cassandra.ps1").read_text(encoding="utf-8")
        self.assertIn("finally {", failure)
        self.assertIn("docker start fixture2030-cassandra", failure)

    def test_powershell_query_string_delimits_base_url_variable(self):
        script = (ROOT / "scripts" / "probar_flujo_mongodb.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn('"${baseUrl}?desdeSecuencia=0&limite=100"', script)
        self.assertNotIn('"$baseUrl?desdeSecuencia=0&limite=100"', script)


if __name__ == "__main__":
    unittest.main()

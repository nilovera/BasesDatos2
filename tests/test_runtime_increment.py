import ast
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeIncrementTests(unittest.TestCase):
    def test_backend_python_files_have_valid_syntax(self):
        for path in sorted((ROOT / "backend" / "app").glob("*.py")):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_direct_dependencies_are_pinned(self):
        requirements = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")
        for dependency in ("fastapi", "cassandra-driver", "neo4j", "psycopg[binary]", "psycopg-pool", "pymongo", "prometheus-client", "redis", "uvicorn"):
            self.assertRegex(requirements, rf"(?m)^{re.escape(dependency)}==[^\s]+$")

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
            "Fixture2030MongoDown",
            "Fixture2030InfluxDown",
            "Fixture2030TelemetryWriteErrors",
            "Fixture2030Neo4jDown",
            "Fixture2030GraphErrors",
            "Fixture2030DataMartDown",
            "Fixture2030DataMartErrors",
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
        self.assertIn("Start-Process", script)
        self.assertIn("workingTreeCleanBeforeCapture", script)
        self.assertIn("manifest-sha256.json", script)
        self.assertNotIn("verificacion-incremento-03", script)
        self.assertNotIn("Get-ChildItem Env:", script)
        self.assertNotIn("docker inspect", script)

        matrix = (
            ROOT / "docs" / "monitoreo" / "matriz_cumplimiento_hito_13.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Implementado no equivale", matrix.replace("**", ""))
        self.assertIn("Pruebas de humo, tráfico normal y estrés", matrix)
        self.assertIn("Defensa de 20 minutos", matrix)
        self.assertIn("no se declara completamente cerrado", matrix)

    def test_grafana_dashboard_is_valid_and_provisioned(self):
        dashboard = json.loads(
            (ROOT / "infra" / "grafana" / "dashboards" / "fixture2030-api.json").read_text(encoding="utf-8")
        )
        self.assertEqual("fixture2030-api", dashboard["uid"])
        self.assertGreaterEqual(len(dashboard["panels"]), 10)
        expressions = {
            target["expr"]
            for panel in dashboard["panels"]
            for target in panel.get("targets", [])
        }
        self.assertIn('fixture2030_dependency_up{dependency="mongodb"}', expressions)
        self.assertIn(
            'fixture2030_dependency_up{dependency=~"mongodb|redis|cassandra|influxdb|neo4j|datamart"}',
            expressions,
        )
        self.assertIn('fixture2030_dependency_up{dependency="influxdb"}', expressions)
        self.assertIn('fixture2030_dependency_up{dependency="neo4j"}', expressions)
        self.assertIn('fixture2030_dependency_up{dependency="datamart"}', expressions)
        self.assertTrue(
            any("fixture2030_telemetry_operations_total" in expression for expression in expressions)
        )
        self.assertTrue(
            any("increase(fixture2030_http_requests_total" in expression for expression in expressions)
        )
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

    def test_datamart_is_persistent_isolated_and_observable(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        metrics = (ROOT / "backend" / "app" / "metrics.py").read_text(encoding="utf-8")
        self.assertIn("  datamart:", compose)
        self.assertIn("postgres:18.7-alpine3.24", compose)
        self.assertIn("127.0.0.1:5433:5432", compose)
        self.assertIn("fixture2030_datamart_data:/var/lib/postgresql", compose)
        self.assertIn("POSTGRES_PASSWORD_FILE", compose)
        self.assertIn("fixture2030_datamart_operations", metrics)
        self.assertNotIn("datamart", (ROOT / "mongodb" / "init" / "01_schema.js").read_text(encoding="utf-8").lower())

    def test_datamart_scripts_are_safe_and_reproducible(self):
        for name in ("verificar_datamart.ps1", "probar_datamart.ps1", "probar_persistencia_datamart.ps1", "probar_falla_datamart.ps1", "comparar_rendimiento_datamart.ps1"):
            script = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            self.assertNotIn("down -v", script.lower())
            self.assertNotIn("docker rm", script.lower())
        failure = (ROOT / "scripts" / "probar_falla_datamart.ps1").read_text(encoding="utf-8")
        self.assertIn("finally {", failure)
        self.assertIn("docker stop fixture2030-datamart", failure)
        self.assertIn("officialReadAvailable", failure)

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
        self.assertIn("Fixture2030CassandraDown", failure)
        self.assertIn("resultado.json", failure)

    def test_dependency_health_and_failures_are_observable(self):
        main = (ROOT / "backend" / "app" / "main.py").read_text(encoding="utf-8")
        repository = (ROOT / "backend" / "app" / "repository.py").read_text(encoding="utf-8")
        self.assertIn("def health_status(self):", repository)
        self.assertIn("mongo_status = repository().health_status()", main)
        self.assertIn('DEPENDENCY_UP.labels("mongodb")', main)

        mongo_failure = (ROOT / "scripts" / "probar_falla_mongodb.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("docker stop fixture2030-mongo", mongo_failure)
        self.assertIn("docker start fixture2030-mongo", mongo_failure)
        self.assertIn("Fixture2030MongoDown", mongo_failure)
        self.assertIn("resultado.json", mongo_failure)
        self.assertIn("finally {", mongo_failure)
        self.assertNotIn("down -v", mongo_failure.lower())

    def test_outbox_worker_is_leased_idempotent_and_observable(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        worker = (ROOT / "backend" / "app" / "outbox_worker.py").read_text(
            encoding="utf-8"
        )
        prometheus = (ROOT / "infra" / "prometheus" / "prometheus.yml").read_text(
            encoding="utf-8"
        )
        rules = (ROOT / "infra" / "prometheus" / "rules" / "fixture2030-alerts.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("  outbox-worker:", compose)
        self.assertIn('command: ["python", "-m", "app.outbox_worker"]', compose)
        self.assertIn('job_name: fixture2030-outbox', prometheus)
        self.assertIn("find_one_and_update", worker)
        self.assertIn('"bloqueo.hasta"', worker)
        self.assertIn("PROJECT_EVENT_LUA", worker)
        self.assertIn("HEXISTS", worker)
        self.assertIn("XADD", worker)
        self.assertIn("Fixture2030OutboxWorkerDown", rules)
        self.assertIn("fixture2030_outbox_oldest_pending_seconds", rules)

    def test_outbox_failure_script_recovers_worker_and_preserves_evidence(self):
        script = (ROOT / "scripts" / "probar_outbox.ps1").read_text(encoding="utf-8")
        self.assertIn("docker compose stop outbox-worker", script)
        self.assertIn("docker compose start outbox-worker", script)
        self.assertIn("finally {", script)
        self.assertIn("Fixture2030OutboxWorkerDown", script)
        self.assertIn("resultado.json", script)
        self.assertNotIn("down -v", script.lower())

    def test_influxdb_is_pinned_persistent_authenticated_and_observable(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        prometheus = (ROOT / "infra" / "prometheus" / "prometheus.yml").read_text(
            encoding="utf-8"
        )
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        for service in ("  influxdb-permissions:", "  influxdb:", "  influxdb-init:"):
            self.assertIn(service, compose)
        self.assertIn("influxdb:3.12.3-core", compose)
        self.assertNotIn("image: influxdb:3-core\n", compose)
        self.assertIn("fixture2030_influxdb_data:/var/lib/influxdb3/data", compose)
        self.assertIn('user: "0:0"', compose)
        self.assertIn("chown -R influxdb3:influxdb3 /var/lib/influxdb3/data", compose)
        self.assertIn("condition: service_completed_successfully", compose)
        self.assertIn("--admin-token-file=/run/secrets/influxdb-admin-token", compose)
        self.assertIn("fixture2030-detalle 7d", compose)
        self.assertIn("fixture2030-historico 365d", compose)
        self.assertIn("posiciones_jugador", compose)
        self.assertIn("resumen_equipo_15m", compose)
        self.assertIn("job_name: fixture2030-influxdb", prometheus)
        self.assertIn("credentials_file: /run/secrets/influxdb-admin-token-raw", prometheus)
        self.assertIn(".secretos", dockerignore)

    def test_influxdb_scripts_are_safe_reproducible_and_recoverable(self):
        functional = (ROOT / "scripts" / "probar_telemetria_influxdb.ps1").read_text(
            encoding="utf-8"
        )
        token_setup = (ROOT / "scripts" / "preparar_influxdb.ps1").read_text(
            encoding="utf-8"
        )
        platform_check = (ROOT / "scripts" / "verificar_plataforma.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("1080", functional)
        self.assertIn("EQ-01", functional)
        self.assertIn("EQ-33", functional)
        self.assertNotIn("equipoId=\"ARG\"", functional)
        self.assertNotIn("equipoId=\"MEX\"", functional)
        self.assertIn("*> $null", token_setup)
        self.assertIn('$health.influxdb -eq "UP"', platform_check)
        self.assertIn('$health.influxdb -ne "UP"', platform_check)
        influx_check = (ROOT / "scripts" / "verificar_influxdb.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("http://localhost:8181/api/v3/query_sql", influx_check)
        self.assertIn("Get-Content -Raw -Path $tokenPath", influx_check)
        self.assertIn('Authorization = "Bearer $token"', influx_check)
        self.assertIn("[System.Text.Encoding]::UTF8.GetString", influx_check)
        self.assertIn("return [string]$response.Content", influx_check)
        self.assertNotIn("/bin/sh -ec $show", influx_check)
        self.assertNotIn("docker compose exec -T influxdb /bin/sh", influx_check)
        for name in (
            "preparar_influxdb.ps1",
            "verificar_influxdb.ps1",
            "probar_telemetria_influxdb.ps1",
            "probar_persistencia_influxdb.ps1",
            "probar_falla_influxdb.ps1",
        ):
            source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            self.assertNotIn("down -v", source.lower())
            self.assertNotIn("docker rm", source.lower())
        failure = (ROOT / "scripts" / "probar_falla_influxdb.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("finally {", failure)
        self.assertIn("docker stop fixture2030-influxdb", failure)
        self.assertIn("docker start fixture2030-influxdb", failure)
        self.assertIn("Fixture2030InfluxDown", failure)
        self.assertIn("resultado.json", failure)

    def test_powershell_query_string_delimits_base_url_variable(self):
        script = (ROOT / "scripts" / "probar_flujo_mongodb.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn('"${baseUrl}?desdeSecuencia=0&limite=100"', script)
        self.assertNotIn('"$baseUrl?desdeSecuencia=0&limite=100"', script)

    def test_neo4j_is_pinned_persistent_authenticated_and_observable(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        seed = (ROOT / "neo4j" / "init" / "seed.py").read_text(encoding="utf-8")
        metrics = (ROOT / "backend" / "app" / "metrics.py").read_text(encoding="utf-8")
        for service in ("  neo4j:", "  neo4j-init:"):
            self.assertIn(service, compose)
        self.assertIn("neo4j:5.26.34-community-trixie", compose)
        self.assertNotIn("image: neo4j:latest", compose)
        self.assertIn("NEO4J_AUTH_FILE: /run/secrets/neo4j-auth", compose)
        self.assertIn("fixture2030_neo4j_data:/data", compose)
        self.assertIn("fixture2030_neo4j_logs:/logs", compose)
        self.assertIn("fixture2030_neo4j_import:/var/lib/neo4j/import", compose)
        self.assertIn("CREATE CONSTRAINT fixture2030_equipo_id IF NOT EXISTS", seed)
        self.assertIn("MERGE (j:Jugador", seed)
        self.assertIn("jugadoresHuerfanos", seed)
        self.assertIn("fixture2030_graph_operations", metrics)

    def test_neo4j_scripts_are_safe_idempotent_and_recoverable(self):
        graph_test = (ROOT / "scripts" / "probar_grafo_neo4j.ps1").read_text(
            encoding="utf-8"
        )
        platform_check = (ROOT / "scripts" / "verificar_plataforma.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("docker compose run --rm neo4j-init", graph_test)
        self.assertIn("--demo-crud", graph_test)
        self.assertIn("camino/EQ-33", graph_test)
        self.assertIn('$health.neo4j -eq "UP"', platform_check)
        self.assertIn('$health.neo4j -ne "UP"', platform_check)
        for name in (
            "preparar_neo4j.ps1",
            "verificar_neo4j.ps1",
            "probar_grafo_neo4j.ps1",
            "probar_persistencia_neo4j.ps1",
            "probar_falla_neo4j.ps1",
        ):
            source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            self.assertNotIn("down -v", source.lower())
            self.assertNotIn("docker rm", source.lower())
        failure = (ROOT / "scripts" / "probar_falla_neo4j.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("finally {", failure)
        self.assertIn("docker stop fixture2030-neo4j", failure)
        self.assertIn("docker start fixture2030-neo4j", failure)
        self.assertIn("Fixture2030Neo4jDown", failure)
        self.assertIn("resultado.json", failure)


if __name__ == "__main__":
    unittest.main()

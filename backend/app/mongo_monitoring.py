"""Métricas de MongoDB leídas en el scrape, sin exponer documentos ni secretos."""

from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily
from pymongo.errors import PyMongoError


class MongoMonitoringCollector:
    def __init__(self, client_factory, database):
        self.client_factory = client_factory
        self.database = database

    def describe(self):
        # Registrar el collector no debe conectarse a MongoDB al importar la API.
        for name in ("fixture2030_mongodb_metrics_up", "fixture2030_mongodb_connections",
                     "fixture2030_mongodb_data_bytes", "fixture2030_mongodb_storage_bytes",
                     "fixture2030_mongodb_index_bytes"):
            yield GaugeMetricFamily(name, "Métrica de MongoDB")
        yield CounterMetricFamily("fixture2030_mongodb_operations", "Operaciones del servidor", labels=["operation"])

    def collect(self):
        up = GaugeMetricFamily("fixture2030_mongodb_metrics_up", "Lectura de métricas MongoDB completada")
        try:
            client = self.client_factory()
            status = client.admin.command("serverStatus")
            stats = client.get_database(self.database).command("dbStats", scale=1)
        except (PyMongoError, OSError):
            up.add_metric([], 0)
            yield up
            return
        up.add_metric([], 1)
        yield up
        current = status.get("connections", {}).get("current")
        if current is not None:
            metric = GaugeMetricFamily("fixture2030_mongodb_connections", "Conexiones abiertas de todos los clientes MongoDB")
            metric.add_metric([], current)
            yield metric
        operations = CounterMetricFamily(
            "fixture2030_mongodb_operations", "Operaciones acumuladas del servidor MongoDB", labels=["operation"]
        )
        for operation in ("insert", "query", "update", "delete", "getmore", "command"):
            value = status.get("opcounters", {}).get(operation)
            if value is not None:
                operations.add_metric([operation], value)
        yield operations
        for field, name in (("dataSize", "data"), ("storageSize", "storage"), ("indexSize", "index")):
            if stats.get(field) is not None:
                metric = GaugeMetricFamily(f"fixture2030_mongodb_{name}_bytes", f"Bytes MongoDB: {field}")
                metric.add_metric([], stats[field])
                yield metric

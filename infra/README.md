# Entorno integrado — próximo incremento

Pendiente de implementación.

El nuevo Compose deberá levantar MongoDB, Cassandra, Redis, InfluxDB y Neo4j, además de la API y la capa de observabilidad. Definirá nombres, puertos y volúmenes propios para evitar colisiones con los laboratorios históricos. No se deben reutilizar volúmenes anteriores ni eliminarlos automáticamente.

Los adaptadores de semillas consumirán `data/catalogo`. Ningún motor tendrá una carga deportiva independiente contradictoria. IRIS no tendrá contenedor, volumen, secreto, exporter ni healthcheck en la arquitectura final.

Prometheus y Grafana se incorporarán con configuración reproducible. El inventario deberá distinguir qué componentes están realmente monitoreados, cuáles solo exponen healthchecks y qué mediciones todavía son propuestas.

Configuraciones de laboratorio, réplicas y topología distribuida objetivo deben documentarse por separado. El arranque de contenedores no demuestra alta disponibilidad ni capacidad productiva.


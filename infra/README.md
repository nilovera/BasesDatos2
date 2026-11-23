# Entorno integrado — próximo incremento

Implementación incremental: MongoDB ya tiene un servicio de laboratorio y un
inicializador reproducible. Los demás motores y la observabilidad permanecen
pendientes.

El nuevo Compose deberá levantar MongoDB, Cassandra, Redis, InfluxDB y Neo4j, además de la API y la capa de observabilidad. Definirá nombres, puertos y volúmenes propios para evitar colisiones con los laboratorios históricos. No se deben reutilizar volúmenes anteriores ni eliminarlos automáticamente.

Los adaptadores de semillas consumirán `data/catalogo`. Ningún motor tendrá una carga deportiva independiente contradictoria. IRIS no tendrá contenedor, volumen, secreto, exporter ni healthcheck en la arquitectura final.

Prometheus y Grafana se incorporarán con configuración reproducible. El inventario deberá distinguir qué componentes están realmente monitoreados, cuáles solo exponen healthchecks y qué mediciones todavía son propuestas.

Configuraciones de laboratorio, réplicas y topología distribuida objetivo deben documentarse por separado. El arranque de contenedores no demuestra alta disponibilidad ni capacidad productiva.

El replica set MongoDB actual contiene un solo miembro: habilita transacciones,
pero no tolera la pérdida del nodo. Esta limitación debe mostrarse explícitamente
en la defensa y no presentarse como replicación productiva.


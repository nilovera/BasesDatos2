# MongoDB — núcleo deportivo

Este directorio contiene el primer artefacto ejecutable del diseño físico.

## Contenido

- `init/00_replica_init.js`: inicialización idempotente de `rs0`.
- `init/01_schema.js`: colecciones, validadores e índices idempotentes.
- `init/02_seed_catalogo.js`: carga reproducible de 64 equipos, 1.024 jugadores y el partido de demostración.
- `init/03_verify.js`: comprobación de réplica, conteos, referencias e índices.

El Compose configura un replica set de un nodo para habilitar transacciones en
laboratorio. Esto no representa alta disponibilidad: una réplica de un miembro
no tolera la caída de ese miembro.

## Ejecución en Windows

Desde la raíz del repositorio:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_mongodb.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_mongodb.ps1
```

Para detener sin borrar el volumen:

```text
powershell -ExecutionPolicy Bypass -File scripts\detener_mongodb.ps1
```

La base utilizada es `fixture2030`. La carga usa `bulkWrite` con `upsert`, el
esquema usa `collMod` cuando la colección existe y los índices conservan nombres
estables. Los partidos se crean con `$setOnInsert`: repetir la inicialización no
crea duplicados ni reinicia marcador, estado, secuencia o versión.

Desde Windows, la conexión de inspección es:

```text
mongodb://localhost:27017/?directConnection=true
```

La API, dentro de la red Docker, utiliza:

```text
mongodb://mongo:27017/fixture2030?replicaSet=rs0
```

## Decisiones

- MongoDB es autoridad de equipos, jugadores, partidos y eventos deportivos.
- `eventos_oficiales` conserva la historia ordenada por partido.
- `partidos` mantiene la vista vigente y su versión de concurrencia.
- `outbox` propaga hechos confirmados a vistas derivadas.
- `contadores` asigna IDs secuenciales `EVE-xxxxxx` dentro de la transacción.
- El esquema y los índices no contienen componentes de IRIS.

## Seguridad y alcance

El puerto se publica solamente en `127.0.0.1`. Esta configuración de laboratorio
no habilita autenticación y no debe exponerse a otra red. Las credenciales y el
keyfile se incorporarán antes de considerar un despliegue fuera del equipo local.

Ver `docs/diseno/06_2_modelo_fisico_mongodb.md` y
`docs/diseno/07_contratos_eventos_idempotencia_outbox.md`.

Referencia del procedimiento de replica set para desarrollo y pruebas:
https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-for-testing/

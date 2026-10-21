# Hito 11 — Evaluación de la conectividad a los productos del Fixture 2030

Ingeniería de Datos II · Grupo 10

Procedimiento reproducible para comprobar, **capa por capa**, que la API integrada del Hito 10 puede localizar, alcanzar, autenticar y usar cada producto NoSQL. Incluye un diagnóstico de fallas, la matriz de conectividad, health/readiness en la API y una falla controlada con recuperación.

> Un contenedor activo no equivale a una dependencia disponible, y un puerto abierto no equivale a un protocolo válido. Por eso cada producto se evalúa desde el mismo entorno que la API y con su propio driver, desde la configuración hasta la lectura mínima.

## Estructura

```text
hito11-conectividad/
├── README.md
├── scripts/
│   ├── evaluar_conectividad.ps1     # punto de entrada (PowerShell)
│   ├── evaluar_conectividad.py      # orquestador: modos completo/config/tcp/nativos/api
│   ├── prueba_config.py             # capa de configuración, sin mostrar secretos
│   ├── prueba_tcp.py                # proceso (docker), resolución y TCP
│   ├── prueba_clientes_nativos.py   # protocolo, auth, autorización, contexto, lectura
│   ├── prueba_api.py                # rutas de la API con request ID y log asociado
│   ├── falla_controlada.ps1 / .py   # dependencia detenida / configuración incorrecta
│   ├── limpieza.py                  # limpieza opcional (modo limpieza)
│   └── common.py                    # configuración, redacción, estados, evidencias
├── config/
│   ├── configuracion-ejemplo.env    # todas las variables, sin secretos
│   └── .gitignore                   # conectividad.env (local) nunca se versiona
└── docs/
    ├── mapa_de_dependencias.md
    ├── topologia_y_entornos.md
    ├── capas_de_evaluacion.md
    ├── matriz_de_conectividad.md    # GENERADO por el modo completo
    ├── diagnostico_de_fallas.md
    ├── health_readiness.md
    ├── limitaciones_y_coherencia.md
    └── evidencia/
        ├── resultados_config.*      # GENERADOS (.txt legible + .json)
        ├── resultados_tcp.*
        ├── resultados_clientes.*
        ├── resultados_api.*
        ├── falla_controlada_*.md/.json
        └── capturas_redactadas/
```

Cambios en la API del Hito 10 (misma rama):

- `app/routes/health.py`, `app/services/dependency_health.py`: `/health/live`, `/health/ready`, `/health/dependencias`.
- `app/adapters/*.py`: `ping()` liviano y errores diferenciados de autenticación, autorización y contexto. Cassandra con conexión diferida. IRIS con timeout.
- `tests/unit/test_dependency_health.py`: pruebas del diagnóstico que no requieren motores.

## Requisitos

- Windows con PowerShell 5.1 o superior (también funciona con `pwsh` en Linux/macOS).
- Docker Desktop con los seis contenedores de los hitos 4 a 9 iniciados y con sus datos cargados.
- Python 3.10 y el entorno virtual de la API (`.venv`) con `requirements.txt` instalado. El diagnóstico usa **los mismos drivers** que la API.
- `.env` de la API completo (ver `.env.example` en la raíz del repositorio).

No hace falta instalar `mongosh`, `cqlsh` ni otros clientes en la notebook. Si se usa `-Cli`, se ejecutan dentro de cada contenedor y, si no están, se informa `SKIP`.

## Variables

Los scripts leen la configuración en este orden (gana el primero):

1. `-Set CLAVE=VALOR` en la línea de comandos (solo para esa ejecución).
2. Variables de entorno del proceso.
3. `hito11-conectividad/config/conectividad.env` (opcional, local, ignorado por Git).
4. `.env` de la API (raíz del repositorio, ignorado por Git).
5. Valores por defecto no secretos.

La lista completa, con valores de ejemplo y sin secretos, está en [`config/configuracion-ejemplo.env`](config/configuracion-ejemplo.env). Las más importantes:

| Variable | Uso | Ejemplo |
|---|---|---|
| `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_DATABASE`, `MONGODB_AUTH_SOURCE` | MongoDB | `127.0.0.1`, `27017`, `fixture2030`, `admin` |
| `NEO4J_URI`, `NEO4J_HTTP_URL`, `NEO4J_DATABASE` | Neo4j Bolt y Browser | `bolt://127.0.0.1:7687`, `http://127.0.0.1:7474`, `neo4j` |
| `CASSANDRA_HOSTS`, `CASSANDRA_PORT`, `CASSANDRA_KEYSPACE` | Cassandra | `127.0.0.1`, `9042`, `fixture2030_comentarios` |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DATABASE` | Redis | `127.0.0.1`, `6379`, `0` |
| `INFLUXDB_URL`, `INFLUXDB_DETAIL_DATABASE`, `INFLUXDB_HISTORICAL_DATABASE` | InfluxDB 3 | `http://127.0.0.1:8181`, `fixture2030_detalle`, `fixture2030_historico` |
| `IRIS_HOST`, `IRIS_PORT`, `IRIS_PORTAL_PORT`, `IRIS_NAMESPACE` | IRIS | `127.0.0.1`, `1972`, `52773`, `USER` |
| `*_USERNAME`, `*_PASSWORD`, `INFLUXDB_TOKEN` | credenciales (**nunca** se imprimen) | — |
| `API_BASE_URL`, `API_LOG_FILE` | API y su log | `http://127.0.0.1:8000`, `logs/api.stderr.log` |
| `DIAG_TIMEOUT_SECONDS` | límite de espera por prueba | `3` |
| `DIAG_ENTORNO` | etiqueta del entorno en la evidencia | `notebook Windows del grupo` |

## Preparación

Todo desde la **raíz del repositorio**:

```powershell
# 1. Entorno virtual de la API (solo la primera vez)
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# 2. Configuración local (solo la primera vez; completar credenciales)
Copy-Item .env.example .env

# 3. Contenedores de los hitos 4 a 9 iniciados
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 4. Sesión de demostración en Redis (para que la ruta de sesiones dé 200)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\preparar_sesiones_redis.ps1"

# 5. Iniciar o reiniciar la API (deja el log en logs\api.stderr.log)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\reiniciar_api.ps1"
```

Si PowerShell bloquea los scripts: `Set-ExecutionPolicy -Scope Process Bypass`.

## Orden de ejecución

```powershell
# A. Evaluación completa: config → TCP → nativos → API + matriz
.\hito11-conectividad\scripts\evaluar_conectividad.ps1

# B. (opcional) Demostración de que localhost cambia según el origen (RNF3)
.\hito11-conectividad\scripts\evaluar_conectividad.ps1 -Modo tcp -DesdeContenedor fixture2030-mongodb -SinMatriz -Etiqueta desde_contenedor

# C. (opcional) Clientes CLI dentro de los contenedores
.\hito11-conectividad\scripts\evaluar_conectividad.ps1 -Modo nativos -Cli -SinMatriz -Etiqueta cli

# D. Falla controlada y recuperación (requiere la API iniciada)
.\hito11-conectividad\scripts\falla_controlada.ps1 -Producto mongodb

# E. (opcional) Configuración incorrecta en una API temporal
.\hito11-conectividad\scripts\falla_controlada.ps1 -Escenario config -Producto neo4j -Set "NEO4J_DATABASE=noexiste"

# F. Pruebas unitarias del diagnóstico (no requieren motores)
.\.venv\Scripts\python.exe -m pytest tests\unit -v

# G. (opcional) Limpieza: primero simula, después ejecuta
.\hito11-conectividad\scripts\evaluar_conectividad.ps1 -Modo limpieza
.\hito11-conectividad\scripts\evaluar_conectividad.ps1 -Modo limpieza -Confirmar
```

Después de A y D, revisar `docs/matriz_de_conectividad.md` y `docs/evidencia/`, sacar las capturas indicadas en `docs/evidencia/capturas_redactadas/README.md` y hacer commit.

### Modos y opciones

| Modo / opción | Qué ejecuta |
|---|---|
| `-Modo completo` (por defecto) | todas las capas + API, regenera la matriz |
| `-Modo config` | variables, origen de cada valor, secretos fuera de Git |
| `-Modo tcp` | estado del contenedor (`docker inspect`), resolución y TCP |
| `-Modo nativos` | protocolo, autenticación, autorización, contexto, lectura mínima y pruebas negativas |
| `-Modo api` | rutas de la API con request ID, status, tiempo y log asociado |
| `-Modo limpieza` | limpieza opcional: claves `diag:hito11:*` en Redis, logs de la API temporal y cachés; verifica que no quede la API temporal en `:8001`. Simula salvo `-Confirmar`. No toca datos de dominio, contenedores, volúmenes ni evidencias |
| `-Producto mongodb\|neo4j\|cassandra\|redis\|influxdb\|iris` | limita la evaluación a un producto (RNF13) |
| `-Set "CLAVE=VALOR"` | sobrescribe una variable solo en esa ejecución |
| `-Etiqueta texto` | sufijo para no sobrescribir evidencias (ej. `antes`, `despues`) |
| `-Cli` | agrega los clientes CLI dentro de los contenedores |
| `-SinEscritura` | no crea la clave temporal `diag:hito11:*` en Redis |
| `-DesdeContenedor nombre` | repite TCP desde dentro de un contenedor |
| `-SinMatriz` | no regenera la matriz |

El script devuelve código 0 si ninguna capa **requerida** terminó en `FALLA` y 1 en caso contrario.

También se pueden ejecutar los scripts Python por separado, por ejemplo `.\.venv\Scripts\python.exe hito11-conectividad\scripts\prueba_tcp.py --producto redis`.

## Cómo leer los resultados

| Estado | Significado |
|---|---|
| `OK` | Esa prueba concreta funcionó. **No** garantiza rendimiento ni disponibilidad permanente |
| `FALLA` | Se intentó y falló. La evidencia incluye hipótesis y siguiente paso |
| `ADVERTENCIA` | Funcionó con una observación |
| `BLOQUEADA` | No se ejecutó porque falló una capa anterior |
| `SKIP` | **Prueba no ejecutada por falta de herramienta o configuración. No significa "producto caído"** |
| `NO_APLICA` | La capa no existe en este entorno (ej. Redis sin password) |

Estados por producto: **disponible**, **degradado**, **no disponible**, **no probado**, **desconocido**, **no configurado**. Las reglas están en [`docs/diagnostico_de_fallas.md`](docs/diagnostico_de_fallas.md).

## Seguridad de la evidencia

- Ninguna salida imprime passwords, tokens ni URI con credenciales. Los valores configurados se reemplazan por `****` antes de escribir consola, `.txt`, `.json` y `.md`.
- El modo `config` verifica que `.env` y `config/conectividad.env` estén ignorados por Git y no versionados.
- Las capturas se guardan solo redactadas (ver `docs/evidencia/capturas_redactadas/README.md`).
- Todas las operaciones son de lectura, ping o retorno constante. La falla controlada usa `docker stop` / `docker start` y nunca borra volúmenes.

## Documentación

| Apartado de la consigna | Documento |
|---|---|
| Mapa de dependencias | [`docs/mapa_de_dependencias.md`](docs/mapa_de_dependencias.md) |
| Topología | [`docs/topologia_y_entornos.md`](docs/topologia_y_entornos.md) |
| Capas de evaluación y pruebas nativas | [`docs/capas_de_evaluacion.md`](docs/capas_de_evaluacion.md) |
| Matriz de conectividad | [`docs/matriz_de_conectividad.md`](docs/matriz_de_conectividad.md) (generada) |
| Pruebas de API | `docs/evidencia/resultados_api.*` (generada) |
| Fallo controlado y diagnóstico | [`docs/diagnostico_de_fallas.md`](docs/diagnostico_de_fallas.md) + `docs/evidencia/falla_controlada_*` |
| Health y readiness | [`docs/health_readiness.md`](docs/health_readiness.md) |
| Configuración | este README + [`config/configuracion-ejemplo.env`](config/configuracion-ejemplo.env) |
| Evidencia | `docs/evidencia/` |
| Limitaciones y coherencia con el TPO | [`docs/limitaciones_y_coherencia.md`](docs/limitaciones_y_coherencia.md) |

## Trazabilidad con los requisitos

| Requisito | Dónde se cumple |
|---|---|
| RF1, RF2 | `mapa_de_dependencias.md`, `topologia_y_entornos.md` |
| RF3 | `prueba_config.py` |
| RF4, RF5 | `prueba_tcp.py` |
| RF6 – RF14 | `prueba_clientes_nativos.py` (una función por producto) |
| RF15, RF18, RF19 | `prueba_api.py` + contrato de errores de la API |
| RF16 | `matriz_de_conectividad.md` generada |
| RF17 | `DependencyMisconfiguredError`, timeouts y `diagnostico_de_fallas.md` |
| RF20, RF21 | `falla_controlada.py` (tabla de cambio de estado) |
| RF22, RNF16 | esta carpeta en la rama `Conectividad`, con historial de commits |
| RNF1 | este README |
| RNF2, RNF15 | un script por capa (configuración, TCP, nativos, API), resumen en el orquestador y `limpieza.py` como limpieza opcional; `Cadena` en `common.py` bloquea capas posteriores |
| RNF3 | origen registrado en cada resultado; `-DesdeContenedor`; advertencia de localhost |
| RNF4 | un driver/protocolo por producto; sin `curl` para Bolt, CQL, RESP ni Superserver |
| RNF5, RNF12 | `DIAG_TIMEOUT_SECONDS`, timeouts de adaptadores, sin reintentos ilimitados |
| RNF6 | solo lecturas, ping y retorno constante; clave Redis de diagnóstico con TTL de 2 s |
| RNF7, RNF8 | `Redactor` en `common.py`; `.gitignore`; capturas redactadas |
| RNF9, RNF10 | estados por producto; hipótesis y siguiente paso automáticos |
| RNF11 | log JSON por request y por chequeo de dependencia |
| RNF13 | `-Producto` y `-Modo`; un producto que falla no corta a los demás |
| RNF14 | cada resultado guarda objetivo, database/keyspace/namespace, clave o ventana |
| RNF17 | leyenda de OK en la consola y en la matriz |
| RNF18 | fecha, commit, rama, entorno, producto, prueba y resultado en cada evidencia |

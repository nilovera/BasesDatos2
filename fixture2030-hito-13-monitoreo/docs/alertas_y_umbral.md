# Alertas y umbrales (RF9, punto 5.4)

Las 8 alertas están en [`prometheus/reglas-o-alertas.yml`](../prometheus/reglas-o-alertas.yml). Prometheus las evalúa cada 15 s y las muestra en `http://localhost:9090/alerts` y en el panel "Alertas activas" del dashboard. Cada alerta lleva tres anotaciones (`resumen`, `impacto`, `accion`) y dos etiquetas (`severidad`, `atiende`), así quien la ve sabe qué pasa, a quién afecta y qué hacer.

**Notificación:** no se configuró Alertmanager (no es necesario en el laboratorio). En producción, la etiqueta `atiende` serviría para enrutar cada alerta: `equipo-api` y `equipo-monitoreo` a la guardia de la plataforma, `dba-*` al responsable de cada base, `infraestructura` a quien opera los servidores.

**Estados:** *inactive* → *pending* (la condición se cumple, pero todavía no durante todo el `for`) → *firing*. El `for` evita alertar por un parpadeo de un solo scraping.

## 1. Alertas de disponibilidad

### FixtureApiCaida · crítica

| Campo | Valor |
|---|---|
| Métrica evaluada | `up{job="fixture-api"}` |
| Condición | `== 0` (Prometheus no pudo leer `/metrics` de la API) |
| Duración mínima | 30 s (2 scrapings seguidos) |
| Componente afectado | API integrada |
| Impacto en el Fixture | **Total.** Ningún front, Swagger o cliente puede consultar partidos, comentarios, sesiones ni estadísticas: la API es el único punto de acceso |
| Investigación / recuperación | `logs\api.stderr.log` → `scripts\reiniciar_api.ps1` → confirmar `GET /health/live` |
| Atiende | `equipo-api` |
| Por qué el umbral | Es binario. 30 s y no 15 s: un scraping perdido por un reinicio controlado no debe despertar a nadie |

### FixtureBaseNoDisponibleParaLaApi · crítica

| Campo | Valor |
|---|---|
| Métrica evaluada | `fixture_dependencia_up` (una serie por base) |
| Condición | `== 0` |
| Duración mínima | 1 min |
| Componente afectado | La base indicada en la etiqueta `dependencia` |
| Impacto en el Fixture | **Parcial.** Las rutas de esa base responden 503; las demás siguen funcionando (aislamiento por adaptador, medido: 0 errores en las otras 5 bases en las 3 pruebas). Ejemplo: sin Redis no se validan sesiones, pero se siguen viendo partidos y comentarios |
| Investigación / recuperación | `GET /health/dependencias?refrescar=true` para ver la clasificación del Hito 11 (`no_disponible`, `timeout`, `rechazo_autenticacion`, `rechazo_contexto`); `docker ps -a`, `docker logs <contenedor>` |
| Atiende | `dba-de-la-base` |
| Por qué el umbral | 1 min = 4 evaluaciones. Junto con los 15 s de caché de la API, la alerta pasa a *firing* ~80-95 s después de la caída (**medido**: 140-155 s desde el inicio con el `stop` en 60 s). Es un tiempo razonable para una base que **no** tiene réplica en el laboratorio; con réplicas, este umbral podría subir a 2-3 min porque la caída de un nodo no corta el servicio |

### FixturePuertoDeBaseCerrado · crítica

| Campo | Valor |
|---|---|
| Métrica evaluada | `probe_success{job="sonda-tcp"}` |
| Condición | `== 0` |
| Duración mínima | 1 min |
| Componente afectado | La base indicada en `componente` |
| Impacto en el Fixture | Igual que la anterior, pero señala que la falla es de **infraestructura** (contenedor detenido, puerto no publicado), no de credenciales ni de la API |
| Investigación / recuperación | `docker ps -a --filter name=fixture2030`, `docker start <contenedor>`, revisar `docker logs` |
| Atiende | `infraestructura` |
| Por qué el umbral | Mismo criterio que la anterior. Si esta alerta está activa **y** la anterior también, la causa es la base; si solo está la anterior, la causa está entre la API y la base (ver el incidente de IRIS en [`limitaciones_y_evidencia.md`](limitaciones_y_evidencia.md)) |

### FixtureSinVisibilidadDeUnComponente · advertencia

| Campo | Valor |
|---|---|
| Métrica evaluada | `up{job=~"mongodb|redis|iris|influxdb|node-exporter"}` |
| Condición | `== 0` |
| Duración mínima | 2 min |
| Componente afectado | El exporter o el endpoint de métricas del motor |
| Impacto en el Fixture | **Ninguno directo:** se pierde visibilidad. Si al mismo tiempo la sonda TCP de la base está en 0, la que cayó es la base |
| Investigación / recuperación | `scripts\verificar_targets.ps1`; procedimiento "target DOWN" del README |
| Atiende | `equipo-monitoreo` |
| Por qué el umbral | Advertencia y 2 min: no afecta a usuarios, se puede atender en horario normal. `cadvisor` se excluye porque es opcional |

## 2. Alertas de rendimiento

### FixtureLatenciaP95Alta · advertencia

| Campo | Valor |
|---|---|
| Métrica evaluada | `fixture:latencia_p95_global_segundos:5m` (P95 del histograma de la API, ventana de 5 min) |
| Condición | `> 0.25` **y** tráfico de negocio `> 1 req/s` |
| Duración mínima | 2 min |
| Componente afectado | API (y la base que la explique, ver panel "P95 por base") |
| Impacto en el Fixture | La "consulta del partido en vivo" se percibe lenta. En un pico de gol es la primera señal antes de los errores |
| Investigación / recuperación | Panel "Latencia P95 por base" para ubicar el motor; comparar CPU del proceso de la API con la de la base; revisar si el corte rápido está abierto |
| Atiende | `equipo-api` |
| Por qué el umbral | **Experimental, basado en mediciones.** P95 interno normal: ~21 ms (Hito 13); P95 visto por el cliente con 80 usuarios: 120-135 ms (Hito 12). 250 ms es ~2 veces el peor valor sano medido. La condición de tráfico mínimo evita alertar con 3 solicitudes, donde el percentil no significa nada. En la prueba sin corte rápido el P95 global llegó a ~2 s y la alerta quedó *pending*: la falla duró menos que ventana + `for` |

### FixtureErrores5xxAltos · crítica

| Campo | Valor |
|---|---|
| Métrica evaluada | `fixture:proporcion_errores_5xx:2m` |
| Condición | `> 0.05` **y** tráfico de negocio `> 1 req/s` |
| Duración mínima | 1 min |
| Componente afectado | API / la base donde se concentren (panel "Errores 5xx por base") |
| Impacto en el Fixture | Usuarios reciben errores |
| Investigación / recuperación | Si los errores se concentran en una base → revisar esa dependencia; si aparecen en todas → revisar la API |
| Atiende | `equipo-api` |
| Por qué el umbral | En todas las corridas normales del Hito 12 y del Hito 13 la tasa fue **0 %**: cualquier valor sostenido es anormal. 5 % separa errores aislados de una falla real. Una base que cae se lleva su porción de la mezcla (Redis = 15 %), así que la alerta se dispara aunque la caída sea de una sola base. **Medido:** se disparó con 12,9 %. Ventana de 2 min (no 5): con 5 min, la caída de una sola base tardaba más de 2 min en superar el 5 % |

## 3. Alertas de capacidad

### RedisMemoriaCercaDelLimite · advertencia

| Campo | Valor |
|---|---|
| Métrica evaluada | `redis_memory_used_bytes / redis_memory_max_bytes` |
| Condición | `> 0.85` |
| Duración mínima | 5 min |
| Componente afectado | Redis (sesiones, Hito 7) |
| Impacto en el Fixture | Con la política `noeviction` elegida en el Hito 7, al llegar al 100 % Redis **rechaza escrituras**: no se pueden crear sesiones nuevas (no borra sesiones existentes, que era el objetivo de esa decisión) |
| Investigación / recuperación | Buscar claves sin TTL (sesiones que nunca vencen), revisar el TTL de 30 min, subir `maxmemory` o escalar Redis |
| Atiende | `dba-redis` |
| Por qué el umbral | 85 % deja margen para reaccionar antes del rechazo. 5 min: la memoria crece de forma gradual, no tiene sentido alertar por un pico. Uso medido: 0,65 % |

### IrisLicenciasCasiAgotadas · advertencia

| Campo | Valor |
|---|---|
| Métrica evaluada | `iris_license_percent_used` (métrica nativa de IRIS) |
| Condición | `> 75` |
| Duración mínima | 5 min |
| Componente afectado | InterSystems IRIS (detalle del partido, Hito 9) |
| Impacto en el Fixture | Si se agotan, `GET /partidos/{codigo}/detalle` responde 503 |
| Investigación / recuperación | Revisar cuántas instancias de la API corren y su `IRIS_POOL_SIZE` (5 por instancia), y otras conexiones abiertas (portal, terminal) |
| Atiende | `dba-iris` |
| Por qué el umbral | IRIS Community admite **8 conexiones simultáneas** (medido en el Hito 12). 75 % ≈ 6 de 8: una segunda instancia de la API con el mismo pool ya lo superaría. Uso medido: 13 % |

## 4. Verificación de las reglas

1. **Pruebas unitarias con `promtool`** ([`prometheus/pruebas-reglas.yml`](../prometheus/pruebas-reglas.yml)): 5 casos con series simuladas. Comprueban que la alerta de base caída se dispara recién después del `for` y se resuelve al volver; que 10 % de 5xx con 20 req/s dispara la alerta y que pocos errores con poco tráfico no; que el P95 > 250 ms dispara la de latencia, y que Redis al 90 % dispara la de memoria. Resultado: `SUCCESS`.

   ```powershell
   docker run --rm -v "${PWD}\fixture2030-hito-13-monitoreo\prometheus:/r" --entrypoint promtool prom/prometheus:v3.5.0 test rules /r/pruebas-reglas.yml
   ```

2. **Prueba real** (prueba controlada con Redis detenido 120 s): se dispararon `FixturePuertoDeBaseCerrado`, `FixtureBaseNoDisponibleParaLaApi` y `FixtureErrores5xxAltos`, y las tres se resolvieron solas al volver Redis. Los momentos exactos están en la tabla "Alertas registradas" de cada `evidencia/prueba_de_falla_redis_*/README.md`, y las capturas en `evidencia/dashboards/04` a `06`.

| Alerta | Pasa a *firing* (s desde el `docker stop`) | Se resuelve (s desde el `docker start`) |
|---|---:|---:|
| FixturePuertoDeBaseCerrado | 80-90 | 15-30 |
| FixtureBaseNoDisponibleParaLaApi | 80-95 | 15-25 |
| FixtureErrores5xxAltos | 115-150 | 70-95 (cuando la ventana de 2 min deja de incluir la falla) |

Valores tomados de las tres corridas (`corte0`, `corte10v1` y `corte10v2`).

# Hito 7 - Redis | Fixture 2030

## Objetivo

Implementar en Redis el módulo temporal de Fixture 2030 para administrar sesiones, caché de equipos, contadores y rankings. El proyecto demuestra TTL, invalidación, operaciones atómicas, persistencia, métricas y una medición local de rendimiento.

Redis complementa los hitos anteriores y no reemplaza sus fuentes persistentes. En particular, MongoDB continúa siendo la fuente de verdad del perfil de los equipos; Redis conserva solamente una copia temporal reconstruible.

## Requisitos

- Windows con PowerShell.
- Docker Desktop en ejecución.
- Docker Compose.
- Puerto local `6379` disponible.

## Estructura

```text
fixture2030-redis/
|-- docker-compose.yml
|-- README.md
|-- scripts/
|   |-- inicializacion.redis
|   |-- carga_muestra.redis
|   |-- sesiones.redis
|   |-- cache.redis
|   |-- concurrencia.redis
|   `-- metricas.redis
`-- docs/
    |-- patrones_de_acceso.md
    |-- modelo_clave_valor.md
    |-- ciclo_de_vida_e_invalidacion.md
    |-- memoria_y_escalabilidad.md
    |-- rendimiento.md
    `-- evidencia/
```

## Configuración principal

| Elemento | Configuración |
|---|---|
| Imagen | `redis:latest` |
| Contenedor | `fixture2030-redis` |
| Puerto | `6379` |
| Modo | Standalone |
| Persistencia | AOF habilitado |
| Volumen | `~/docker/data/redis:/data` |
| Memoria máxima | 256 MB |
| Política | `noeviction` |

## Puesta en marcha

Desde PowerShell:

```powershell
cd C:\fixture2030-redis
docker compose up -d
docker compose ps
docker exec fixture2030-redis redis-cli PING
docker exec fixture2030-redis redis-cli INFO server
```

La verificación de disponibilidad debe devolver `PONG`.

## Ejecución de los scripts

Los scripts se ejecutan desde la raíz del proyecto en el siguiente orden.

### 1. Inicialización segura

```powershell
Get-Content -Raw ".\scripts\inicializacion.redis" |
docker exec -i fixture2030-redis redis-cli
```

Este script elimina únicamente las claves conocidas de la demostración, verifica la configuración e inspecciona las familias con `SCAN`. No utiliza `FLUSHALL` ni `KEYS *`.

### 2. Carga reproducible

```powershell
Get-Content -Raw ".\scripts\carga_muestra.redis" |
docker exec -i fixture2030-redis redis-cli
```

Puede ejecutarse nuevamente sin duplicar miembros del ranking ni crear nuevas familias de claves. La segunda ejecución conserva el estado esperado.

### 3. Ciclo de vida de sesiones

```powershell
Get-Content -Raw ".\scripts\sesiones.redis" |
docker exec -i fixture2030-redis redis-cli
```

Para comprobar la expiración corta:

```powershell
Start-Sleep -Seconds 7
docker exec fixture2030-redis redis-cli TTL sesion:SES-EXPIRA
docker exec fixture2030-redis redis-cli EXISTS sesion:SES-EXPIRA
```

Los resultados esperados son `-2` para `TTL` y `0` para `EXISTS`.

### 4. Cache-Aside e invalidación

```powershell
Get-Content -Raw ".\scripts\cache.redis" |
docker exec -i fixture2030-redis redis-cli
```

La prueba demuestra miss, carga desde la fuente de verdad simulada, hit, invalidación con `DEL` y reconstrucción de la copia actualizada.

### 5. Operaciones atómicas y ranking

```powershell
Get-Content -Raw ".\scripts\concurrencia.redis" |
docker exec -i fixture2030-redis redis-cli
```

El ranking utiliza `ZINCRBY` y se consulta con `ZREVRANGE ... WITHSCORES`. El contador utiliza `INCR`, una operación atómica que evita actualizaciones perdidas.

Prueba concurrente con diez trabajos de cien incrementos cada uno:

```powershell
$jobs = 1..10 | ForEach-Object {
    Start-Job {
        1..100 | ForEach-Object {
            docker exec fixture2030-redis redis-cli INCR contador:partido:PAR-0001:visitas | Out-Null
        }
    }
}

$jobs | Wait-Job | Out-Null
$jobs | Receive-Job | Out-Null
$jobs | Remove-Job
docker exec fixture2030-redis redis-cli GET contador:partido:PAR-0001:visitas
```

Partiendo de cero, el resultado esperado es `1000`.

### 6. Métricas

```powershell
Get-Content -Raw ".\scripts\metricas.redis" |
docker exec -i fixture2030-redis redis-cli
```

Consultas resumidas:

```powershell
docker exec fixture2030-redis redis-cli INFO stats |
Select-String "keyspace_hits|keyspace_misses|expired_keys|evicted_keys"

docker exec fixture2030-redis redis-cli INFO memory |
Select-String "used_memory_human|maxmemory_human|maxmemory_policy"

docker exec fixture2030-redis redis-cli DBSIZE
```

## Familias de claves

| Familia | Estructura | TTL | Uso |
|---|---|---:|---|
| `sesion:<id>` | Hash | 1800 s | Estado temporal de sesión |
| `cache:equipo:<id>` | String serializado | 300 s | Copia reconstruible de MongoDB |
| `ranking:partido:<id>:figura` | Sorted Set | 86400 s | Votos y Top 5 |
| `contador:partido:<id>:visitas` | String numérico | 86400 s | Contador atómico |

## Persistencia

El contenedor utiliza AOF y un volumen montado en el equipo anfitrión. La recuperación puede verificarse con:

```powershell
docker exec fixture2030-redis redis-cli SET prueba:persistencia "dato-conservado"
docker compose restart redis
docker exec fixture2030-redis redis-cli PING
docker exec fixture2030-redis redis-cli GET prueba:persistencia
docker exec fixture2030-redis redis-cli DEL prueba:persistencia
```

La prueba realizada devolvió `dato-conservado` después del reinicio.

Para detener el ambiente sin borrar el volumen:

```powershell
docker compose down
```

Para iniciarlo nuevamente:

```powershell
docker compose up -d
```

## Resultados observados

- Redis 8.10.2 en modo standalone.
- `appendonly`: `yes`.
- Memoria utilizada: 1,81 MB.
- Memoria máxima: 256 MB.
- Política: `noeviction`.
- Cache hits acumulados: 40.
- Cache misses acumulados: 7.
- Claves expiradas: 4.
- Claves expulsadas por memoria: 0.
- Medición `INCR`: 10.000 operaciones en 24,357 s, aproximadamente 410,56 ops/s.
- Medición `GET`: 10.000 operaciones en 2,903 s, aproximadamente 3.444,27 ops/s.

Las cifras de rendimiento corresponden al ambiente local completo, incluyendo Docker, `redis-cli` y el procesamiento de su salida. No representan el rendimiento máximo aislado de Redis ni deben extrapolarse directamente a producción.

## Decisiones principales

- Los patrones de acceso se definieron antes de diseñar las claves.
- Las sesiones se modelaron como Hash para actualizar atributos individuales.
- La caché usa Cache-Aside y MongoDB conserva la autoridad del dato.
- Los votos y contadores usan operaciones nativas atómicas.
- El TTL expresa el ciclo de vida funcional de los datos.
- `noeviction` evita que la presión de memoria elimine silenciosamente sesiones.
- Se usa `SCAN` para inspección segura y no `KEYS *`.

## Limitaciones

El laboratorio utiliza un único nodo. No demuestra replicación, failover, Sentinel, Redis Cluster ni alta disponibilidad. Estas alternativas se documentan como una posible evolución, pero no forman parte de la implementación del Hito 7.

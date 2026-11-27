# Redis en Fixture2030

Redis almacena únicamente información temporal o reconstruible. MongoDB sigue
siendo la fuente oficial de los partidos y eventos.

`protected-mode` está desactivado para permitir el acceso de la API y Redis
Exporter desde la red interna de Docker. El puerto se publica solamente sobre
`127.0.0.1`, por lo que no queda expuesto a otras interfaces del equipo. Esta
configuración es exclusiva del laboratorio; un despliegue productivo requiere
autenticación, TLS y reglas de red.

| Namespace | Estructura | TTL | Uso |
|---|---|---:|---|
| `cache:partido:{id}` | String JSON | 60 s | Cache-Aside de partidos |
| `sesion:{id}` | Hash | explícito, 60–3600 s | sesiones sintéticas |
| `contador:partido:{id}:consultas` | String contador | 24 h | incremento atómico |
| `ranking:partidos:consultas` | Sorted Set | 24 h | ranking por consultas |

La política `allkeys-lfu` puede eliminar una clave antes de su TTL cuando se
alcanza `maxmemory`. Es aceptable en este laboratorio porque todas las claves
son temporales o reconstruibles. En producción, sesiones y caché podrían
separarse en instancias con políticas distintas.

RDB y AOF están activos simultáneamente. RDB toma snapshots (`save 60 1`) y AOF
registra escrituras con `appendfsync everysec`. Esto permite demostrar ambos
mecanismos, pero no convierte a Redis en fuente de verdad.


## Proyección y evidencia

El worker Outbox invalida la caché y proyecta marcador y Stream después de la
confirmación MongoDB. El destino sigue siendo eventual y reconstruible; una
sesión perdida debe recrearse y no se reconstruye como identidad autenticada.

La verificación Docker, bypass durante falla y replay sin duplicación están
registrados en [estado de validación](../docs/estado_validacion.md).

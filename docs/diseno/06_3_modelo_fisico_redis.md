# Modelo físico de Redis

## Decisión de alcance

Redis contiene datos calientes, temporales o reconstruibles. MongoDB conserva
la autoridad sobre partidos y eventos. La persistencia RDB/AOF mejora la
recuperación operativa, pero no modifica esa responsabilidad.

## Patrones implementados

### Cache-Aside

`GET /api/v1/partidos/{partidoId}` consulta primero
`cache:partido:{partidoId}`. Un hit responde desde Redis; un miss consulta
MongoDB, serializa la respuesta y la guarda durante 60 segundos. Si Redis está
caído, la lectura usa MongoDB y responde con `X-Cache: BYPASS`.

Después de confirmar un evento en MongoDB se elimina la clave. El TTL limita la
vida máxima, pero la invalidación explícita evita servir una versión vieja
durante todo ese intervalo.

### Sesiones y renovación explícita

Las sesiones sintéticas se representan como Hash y siempre poseen TTL. Un GET
no renueva la sesión. La renovación tiene un endpoint explícito y ejecuta en
Redis, de forma atómica, la actualización del último acceso, el contador de
renovaciones y `EXPIRE`. La operación no recrea una clave que ya expiró.

La colección durable de usuarios en MongoDB continúa pendiente; por eso estas
sesiones usan identificadores sintéticos `USR-0001` y no prueban autenticación.

### Operaciones atómicas y Sorted Set

Cada lectura incrementa `contador:partido:{id}:consultas` con `INCR` y actualiza
`ranking:partidos:consultas` con `ZINCRBY`. No se implementa el antipatrón
GET-sumar-SET. Ambas estructuras vencen después de 24 horas.

## Expiración y evicción

El TTL expresa una regla funcional. La evicción ocurre solamente cuando Redis
alcanza `maxmemory`. El laboratorio limita la memoria a 256 MB y utiliza
`allkeys-lfu`: conserva aproximadamente las claves consultadas con mayor
frecuencia. Una clave puede ser expulsada antes de vencer; por eso toda caché
se reconstruye desde MongoDB y una sesión ausente se trata como expirada.

La política es defendible porque esta instancia contiene exclusivamente datos
temporales. En producción convendría separar caché y sesiones si requieren
políticas o garantías diferentes.

## Persistencia

- RDB: snapshot después de 60 segundos si hubo al menos una escritura, con
  compresión y checksum.
- AOF: registro de operaciones con `appendfsync everysec` y preámbulo RDB.
- Volumen: `fixture2030-redis-data`, montado en `/data`.

RDB puede perder cambios posteriores al último snapshot. AOF reduce esa ventana
a aproximadamente el intervalo de sincronización configurado, a cambio de más
I/O. El script de persistencia fuerza `BGSAVE`, verifica ambos artefactos,
reinicia solamente Redis y consulta la sesión recuperada.

## Inspección segura

Los scripts conocen claves exactas y no usan `KEYS *`. Para una inspección por
patrón se debe utilizar `SCAN` con cursor y lotes acotados.

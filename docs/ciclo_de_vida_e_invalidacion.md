# Ciclo de vida e invalidación - Fixture 2030

## 1. Ciclo de vida de una sesión

La sesión representa estado temporal de navegación. Se almacena en un Hash y tiene un TTL de 1800 segundos, equivalentes a 30 minutos de inactividad.

### 1.1. Creación

Después de una autenticación válida, la aplicación:

1. Construye un identificador de sesión de demostración que no contiene credenciales.
2. Crea el Hash con el usuario, rol, estado, último acceso y contexto de navegación.
3. Aplica `EXPIRE` por 1800 segundos.
4. Verifica el tiempo restante con `TTL`.

La sesión se considera válida cuando la clave existe, su estado es `activa` y conserva un TTL positivo.

### 1.2. Consulta

La aplicación conoce el identificador de sesión y ejecuta `HGETALL` sobre la clave correspondiente. No necesita recorrer otras sesiones.

- Si la clave existe, se validan sus atributos.
- Si no existe, la respuesta de Redis es vacía y la aplicación solicita un nuevo inicio de sesión.

### 1.3. Renovación por actividad

Solo una acción válida del usuario renueva la sesión. Por ejemplo, consultar un partido, navegar a un equipo o emitir un voto.

La renovación debe:

1. Actualizar `ultimo_acceso`.
2. Incrementar el contador de acciones cuando corresponda.
3. Restablecer el TTL a 1800 segundos.

Como `HSET` no renueva automáticamente el TTL, la actualización y la renovación se ejecutan deliberadamente mediante `MULTI` y `EXEC`. Redis ejecuta los comandos encolados de forma consecutiva, sin que otro cliente intercale operaciones entre ellos. No se presenta este mecanismo como una transacción relacional con rollback.

### 1.4. Expiración por inactividad

Si transcurren 30 minutos sin una actividad válida, Redis elimina la clave mediante sus mecanismos nativos de expiración. No se implementa un proceso manual que recorra todas las sesiones.

Interpretación de `TTL`:

- Valor positivo o cero: segundos restantes.
- `-1`: la clave existe, pero no tiene expiración; sería un error para una sesión.
- `-2`: la clave ya no existe.

La prueba utilizará una sesión adicional con un TTL corto para demostrar el vencimiento sin esperar 30 minutos. La política real documentada continúa siendo de 1800 segundos.

### 1.5. Cierre e invalidación explícita

El cierre de sesión elimina inmediatamente el Hash con `DEL`. También puede eliminarse ante una decisión de seguridad o un cambio que invalide el acceso. No se espera al vencimiento natural cuando la sesión debe dejar de ser válida en ese momento.

## 2. Ciclo de vida de la caché

Se utiliza el patrón Cache-Aside para el perfil de un equipo. Redis contiene una copia reconstruible y MongoDB conserva la fuente de verdad.

### 2.1. Cache hit

1. La aplicación recibe el identificador del equipo.
2. Construye la clave `cache:equipo:<equipo_id>`.
3. Ejecuta `GET`.
4. Si obtiene un valor, responde desde Redis.

La lectura desde Redis evita consultar repetidamente MongoDB para la misma ficha.

### 2.2. Cache miss

1. `GET` no encuentra la clave.
2. La aplicación consulta la colección `equipos` de MongoDB.
3. Devuelve el dato obtenido de la fuente de verdad.
4. Guarda una copia serializada con `SET ... EX 300`.

Si Redis no está disponible, la aplicación debe consultar directamente MongoDB y continuar sin caché. La falta de Redis puede aumentar la latencia y la carga sobre la fuente, pero no debe convertir la copia temporal en el único origen del dato.

### 2.3. Expiración de la copia

La caché tiene un TTL de 300 segundos. Este valor limita a cinco minutos la permanencia máxima de una copia que no recibió una invalidación explícita y evita conservar indefinidamente perfiles poco consultados.

### 2.4. Invalidación ante un cambio

El TTL no reemplaza la coherencia. Cuando se modifica un equipo:

1. La aplicación actualiza primero MongoDB.
2. Si la actualización fue confirmada, ejecuta `DEL cache:equipo:<equipo_id>`.
3. La siguiente consulta produce un cache miss.
4. La aplicación recupera la versión actual de MongoDB y reconstruye la caché.

Con este orden, Redis no elimina la copia antes de saber si el cambio en la fuente de verdad fue exitoso.

## 3. Ciclo de vida de rankings y contadores

El ranking y el contador son datos temporales del módulo:

- Los votos se actualizan atómicamente con `ZINCRBY`.
- El ranking se consulta mediante `ZREVRANGE ... WITHSCORES`.
- Las visitas se incrementan atómicamente con `INCR`.
- Ambas claves reciben un TTL de 86400 segundos para la demostración.

Si una de estas claves no existe, se interpreta que todavía no hubo actividad o que el período temporal ya terminó. No se realiza una búsqueda global para reconstruirla.

## 4. TTL y evicción

Los mecanismos responden a problemas diferentes:

- **TTL:** decisión funcional sobre cuándo el dato deja de ser válido.
- **Evicción:** comportamiento de Redis cuando alcanza el límite de memoria.

El laboratorio utiliza `maxmemory 256mb` y `maxmemory-policy noeviction`. Al alcanzar el límite, Redis no eliminará silenciosamente sesiones ni claves de caché: rechazará las nuevas escrituras que requieran memoria y la aplicación deberá manejar el error. Esta política no evita el vencimiento normal de claves por TTL.

## 5. Persistencia y recuperación

El ambiente activa AOF y monta `~/docker/data/redis` en `/data`. Esto permite recuperar el estado tras un reinicio normal del contenedor. Sin embargo:

- La persistencia no convierte la caché en fuente de verdad.
- Las copias de equipos deben poder reconstruirse desde MongoDB.
- Una sesión ausente se trata como inválida.
- El nodo único continúa siendo un punto único de falla.

## 6. Evidencia prevista

La entrega demostrará:

- Sesión creada con TTL positivo.
- Renovación del TTL después de una actividad válida.
- Expiración de una sesión de prueba con TTL corto.
- Eliminación explícita mediante cierre de sesión.
- Cache miss seguido de carga.
- Cache hit posterior.
- Invalidación con `DEL` y nuevo miss.
- Incrementos atómicos y ranking ordenado.
- Métricas de hits, misses, expiraciones, evicciones y memoria.

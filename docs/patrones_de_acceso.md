# Patrones de acceso - Caché de usuarios y sesiones

## 1. Objetivo

El módulo Redis del Fixture 2030 administrará información temporal que requiere baja latencia: sesiones de usuarios, copias en caché de perfiles de equipos y una votación temporal por partido. Redis no reemplaza a los módulos persistentes desarrollados en los hitos anteriores.

## 2. Problema de concurrencia

Durante un partido pueden existir muchas consultas y actualizaciones simultáneas. Distintos usuarios pueden renovar su sesión, consultar repetidamente un equipo o votar al mismo jugador al mismo tiempo. El diseño debe evitar que las lecturas repetidas sobrecarguen la fuente de verdad y que dos votos concurrentes se pisen entre sí.

## 3. Patrones de acceso

### PA1 - Crear una sesión

- **Quién solicita:** usuario autenticado de la plataforma.
- **Entrada disponible:** identificador de sesión, identificador de usuario, rol y fecha de acceso.
- **Respuesta esperada:** confirmación de creación y tiempo restante de la sesión.
- **Frecuencia:** escritura media; aumenta durante el inicio de un partido.
- **Ciclo de vida:** temporal. La sesión vence después de 30 minutos de inactividad.
- **Estructura elegida:** Hash, porque permite guardar y actualizar los atributos de la sesión por separado.
- **Operaciones previstas:** `HSET`, `EXPIRE` y `TTL`.

### PA2 - Recuperar y renovar una sesión activa

- **Quién solicita:** aplicación ante una acción válida del usuario.
- **Entrada disponible:** identificador de sesión.
- **Respuesta esperada:** atributos de la sesión y renovación del tiempo de inactividad.
- **Frecuencia:** lectura y actualización altas durante la navegación.
- **Ciclo de vida:** el último acceso y el TTL se renuevan únicamente ante actividad válida.
- **Estructura elegida:** Hash con TTL aplicado a la clave completa.
- **Operaciones previstas:** `HGETALL`, `HSET`, `EXPIRE`, `MULTI` y `EXEC`.
- **Clave ausente:** la aplicación considera la sesión vencida o inválida y solicita un nuevo inicio de sesión.

### PA3 - Cerrar o invalidar una sesión

- **Quién solicita:** usuario al cerrar sesión o sistema ante una invalidación explícita.
- **Entrada disponible:** identificador de sesión.
- **Respuesta esperada:** confirmación de eliminación.
- **Frecuencia:** escritura baja o media.
- **Ciclo de vida:** la sesión se elimina inmediatamente; no se espera a que finalice el TTL.
- **Estructura elegida:** eliminación de la clave completa del Hash.
- **Operación prevista:** `DEL`.

### PA4 - Consultar el perfil de un equipo mediante caché

- **Quién solicita:** usuarios que consultan repetidamente la ficha de un equipo.
- **Entrada disponible:** identificador estable del equipo.
- **Respuesta esperada:** datos resumidos del equipo con baja latencia.
- **Frecuencia:** lectura alta y escritura baja.
- **Fuente de verdad:** colección `equipos` de MongoDB, desarrollada en el Hito 4.
- **Dato en Redis:** copia temporal y reconstruible del perfil consultado.
- **Estructura elegida:** String con una respuesta serializada, porque la ficha se recupera completa.
- **Operaciones previstas:** `GET`, `SET` con expiración y `DEL`.
- **Cache hit:** Redis contiene la copia y la aplicación responde desde la caché.
- **Cache miss:** la aplicación consulta MongoDB, responde y almacena una copia temporal en Redis.
- **Ciclo de vida:** TTL de 300 segundos. Este TTL limita la antigüedad máxima, pero no reemplaza la invalidación.

### PA5 - Invalidar la caché ante un cambio

- **Quién actualiza:** proceso que modifica el equipo en la fuente de verdad.
- **Entrada disponible:** identificador del equipo actualizado.
- **Respuesta esperada:** la siguiente consulta no debe recibir la copia anterior.
- **Frecuencia:** baja.
- **Fuente de verdad:** MongoDB se actualiza primero.
- **Estrategia:** después de confirmar el cambio en MongoDB, se elimina la copia correspondiente en Redis.
- **Operación prevista:** `DEL`.
- **Recuperación:** la próxima lectura produce un cache miss y reconstruye la caché desde MongoDB.

### PA6 - Registrar votos concurrentes y consultar el ranking

- **Quién actualiza:** usuarios que eligen la figura de un partido.
- **Entrada disponible:** identificador del partido e identificador del jugador.
- **Respuesta esperada:** voto acumulado correctamente y ranking ordenado de jugadores.
- **Frecuencia:** escritura alta durante el partido y lectura alta al mostrar resultados.
- **Ciclo de vida:** temporal; el ranking se conserva durante 24 horas después de la actividad demostrativa.
- **Estructura elegida:** Sorted Set, porque asocia cada jugador con un puntaje y mantiene el orden.
- **Operaciones previstas:** `ZINCRBY`, `ZREVRANGE` con puntajes y `EXPIRE`.
- **Concurrencia:** `ZINCRBY` es una operación nativa atómica; evita el antipatrón de leer, sumar en la aplicación y volver a escribir.

### PA7 - Consultar métricas e inspeccionar claves

- **Quién solicita:** equipo técnico durante las pruebas.
- **Entrada disponible:** sección de métricas o patrón de clave.
- **Respuesta esperada:** hits, misses, expiraciones, evicciones y consumo de memoria.
- **Frecuencia:** baja y controlada.
- **Estructura elegida:** métricas internas de Redis.
- **Operaciones previstas:** `INFO stats`, `INFO memory` y `SCAN`.
- **Restricción:** no se utilizará `KEYS *` como mecanismo normal de inspección, porque puede bloquear el servidor al recorrer todas las claves.

## 4. Resumen de temporalidad y autoridad

| Información | Fuente de verdad | Redis | Expiración o invalidación |
|---|---|---|---|
| Perfil completo del equipo | MongoDB | Copia de caché | TTL de 300 segundos y `DEL` ante cambios |
| Sesión del usuario | Servicio de autenticación no implementado físicamente | Estado temporal | 30 minutos de inactividad, cierre o invalidación |
| Votos y ranking de demostración | Operación temporal del módulo | Sorted Set | TTL de 24 horas |

## 5. Alcance del laboratorio

El ambiente utiliza un único nodo Redis en modo standalone. Permite demostrar claves, estructuras, TTL, caché, atomicidad y métricas, pero no demuestra alta disponibilidad, replicación, Sentinel ni Redis Cluster.

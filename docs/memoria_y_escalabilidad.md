# Memoria y escalabilidad - Fixture 2030

## 1. Configuración del laboratorio

El módulo utiliza una instancia Redis en modo `standalone`, ejecutada mediante Docker Compose con la imagen `redis:latest`.

Configuración aplicada:

```text
maxmemory 256mb
maxmemory-policy noeviction
appendonly yes
```

La persistencia local se monta en `~/docker/data/redis` y Redis utiliza AOF para registrar operaciones de escritura.

## 2. Política de memoria elegida

Se seleccionó `noeviction` porque el laboratorio comparte en una sola instancia sesiones, caché y datos temporales. Si Redis alcanza el límite de 256 MB, no eliminará silenciosamente una sesión o un ranking para aceptar una nueva escritura. Las operaciones que requieran memoria adicional devolverán un error y la aplicación deberá manejarlo.

Esta decisión prioriza que una sesión no desaparezca de forma impredecible por presión de memoria. La desventaja es que el servicio puede rechazar nuevas escrituras cuando se agota la capacidad disponible.

## 3. Diferencia entre TTL y evicción

- **TTL:** elimina una clave porque el dato dejó de ser válido según una regla funcional.
- **Evicción:** elimina claves bajo presión de memoria, según la política configurada.

Una sesión que vence por inactividad y una caché que supera su duración permitida deben desaparecer aunque exista memoria disponible. En cambio, con `noeviction`, la presión de memoria no elimina claves anticipadamente.

## 4. Métricas observadas

Fecha de observación: 30 de septiembre de 2026.

| Métrica | Resultado |
|---|---:|
| Memoria utilizada | 1,81 MB |
| Límite configurado | 256 MB |
| Política | `noeviction` |
| Claves actuales | 2 |
| Cache hits acumulados | 40 |
| Cache misses acumulados | 7 |
| Claves expiradas | 4 |
| Claves expulsadas por memoria | 0 |

Los valores de hits y misses son acumulados desde el inicio de la instancia. Las cuatro expiraciones corresponden a claves temporales vencidas durante las pruebas. `evicted_keys:0` confirma que ninguna clave fue eliminada por presión de memoria.

## 5. Comportamiento esperado al alcanzar el límite

Cuando la instancia alcanza `maxmemory`:

1. Redis conserva las claves existentes mientras no venzan por TTL ni sean eliminadas explícitamente.
2. Las nuevas escrituras que requieran memoria pueden recibir un error.
3. Las lecturas de claves existentes pueden continuar.
4. La aplicación debe registrar el error y aplicar degradación controlada.
5. Para una caché, la aplicación puede consultar directamente MongoDB sin guardar una nueva copia.
6. Para una sesión nueva, el servicio debe informar que no pudo crear el estado temporal; no debe asumir que la sesión fue creada.

## 6. Persistencia y recuperación

AOF permite recuperar datos tras un reinicio normal del contenedor. Sin embargo, persistir Redis no cambia la autoridad de los datos:

- MongoDB continúa siendo la fuente de verdad para equipos.
- La caché es una copia reconstruible.
- Una sesión ausente se considera inválida.
- Los rankings y contadores son datos temporales del módulo.

## 7. Limitaciones del nodo único

El entorno local posee un único proceso Redis y, por lo tanto:

- Es un punto único de falla.
- No demuestra replicación ni failover.
- No distribuye memoria ni claves entre nodos.
- No permite afirmar alta disponibilidad.
- Las cifras de rendimiento representan solamente la computadora local.

## 8. Evolución para producción

En un ambiente productivo convendría separar responsabilidades:

- Instancia de sesiones con una política conservadora y recuperación definida.
- Instancia dedicada a caché, donde podría evaluarse `allkeys-lfu` para conservar los perfiles más consultados.
- Primary y réplicas con Sentinel cuando el objetivo principal sea disponibilidad y failover.
- Redis Cluster cuando sea necesario distribuir capacidad y claves entre varios nodos.

Estas topologías requieren analizar replicación, consistencia eventual, slots y operaciones de varias claves. No forman parte de la implementación local del Hito 7.

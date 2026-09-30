# Modelo clave/valor - Fixture 2030

## 1. Criterio de diseño

Redis localizará cada dato a partir de una clave conocida por la aplicación. Las claves se diseñan según los patrones de acceso documentados y no para realizar búsquedas globales. Cada estructura tiene una operación concreta que justifica su existencia.

## 2. Convención de nombres

Se utiliza la siguiente convención:

```text
dominio:alcance:identificador:proposito
```

Reglas:

- Separar las partes mediante `:`.
- Utilizar identificadores estables y no nombres que puedan cambiar.
- Expresar claramente el dominio y el alcance de la información.
- No incluir tokens, contraseñas ni datos sensibles en las claves.
- Inspeccionar familias de claves mediante `SCAN` y no mediante `KEYS *`.

## 3. Familias de claves

### 3.1. Sesiones de usuario

```text
sesion:SES-0001
```

- **Tipo:** Hash.
- **Propósito:** almacenar el estado temporal de una sesión.
- **TTL:** 1800 segundos desde la última actividad válida.
- **Patrones relacionados:** crear, recuperar, renovar, cerrar y detectar una sesión ausente.

Campos:

| Campo | Ejemplo | Función |
|---|---|---|
| `sesion_id` | `SES-0001` | Identificador de la sesión |
| `usuario_id` | `USR-0001` | Usuario asociado |
| `rol` | `fan` | Estado de acceso |
| `ultimo_acceso` | `2030-06-13T20:15:00Z` | Última actividad válida |
| `estado` | `activa` | Estado lógico de acceso |
| `partido_actual` | `PAR-0001` | Contexto temporal de navegación |
| `acciones` | `0` | Cantidad de acciones realizadas |

Operaciones principales:

```text
HSET sesion:SES-0001 ...
HGETALL sesion:SES-0001
HINCRBY sesion:SES-0001 acciones 1
EXPIRE sesion:SES-0001 1800
TTL sesion:SES-0001
DEL sesion:SES-0001
```

El TTL pertenece al Hash completo. `HSET` y `HINCRBY` no renuevan automáticamente la expiración; la renovación debe ejecutarse de manera explícita.

### 3.2. Caché de perfil de equipo

```text
cache:equipo:ARG
```

- **Tipo:** String con contenido serializado.
- **Propósito:** devolver rápidamente una ficha de equipo consultada con frecuencia.
- **Fuente de verdad:** colección `equipos` de MongoDB.
- **TTL:** 300 segundos.
- **Patrones relacionados:** cache hit, cache miss e invalidación.

Ejemplo conceptual del valor:

```json
{"equipo_id":"ARG","nombre":"Argentina","confederacion":"CONMEBOL"}
```

Operaciones principales:

```text
GET cache:equipo:ARG
SET cache:equipo:ARG <valor_serializado> EX 300
DEL cache:equipo:ARG
```

La información es una copia descartable. Si la clave no existe, la aplicación debe consultar MongoDB y reconstruirla. Cuando se modifica el equipo en MongoDB, se elimina la copia para impedir que se continúe entregando información obsoleta.

### 3.3. Ranking temporal de figura del partido

```text
ranking:partido:PAR-0001:figura
```

- **Tipo:** Sorted Set.
- **Miembro:** identificador estable del jugador.
- **Score:** cantidad acumulada de votos.
- **Propósito:** registrar votos simultáneos y devolver el ranking ordenado.
- **TTL:** 86400 segundos, equivalentes a 24 horas.
- **Patrones relacionados:** actualización concurrente y consulta Top N.

Operaciones principales:

```text
ZINCRBY ranking:partido:PAR-0001:figura 1 JUG-0001
ZREVRANGE ranking:partido:PAR-0001:figura 0 4 WITHSCORES
EXPIRE ranking:partido:PAR-0001:figura 86400
```

`ZINCRBY` modifica el puntaje dentro del servidor como una operación atómica. De esta manera, dos votos concurrentes no realizan una secuencia separada de lectura, suma y escritura que pueda perder actualizaciones.

### 3.4. Contador de visitas de un partido

```text
contador:partido:PAR-0001:visitas
```

- **Tipo:** String numérico.
- **Propósito:** contar accesos a la ficha de un partido y demostrar una segunda operación atómica simple.
- **Ciclo de vida:** temporal para la demostración; TTL de 86400 segundos.

Operaciones principales:

```text
INCR contador:partido:PAR-0001:visitas
GET contador:partido:PAR-0001:visitas
EXPIRE contador:partido:PAR-0001:visitas 86400
```

## 4. Relación entre patrones y estructuras

| Patrón de acceso | Familia de clave | Estructura | Justificación |
|---|---|---|---|
| Crear, consultar y renovar sesión | `sesion:*` | Hash | Modificación independiente de atributos y TTL sobre la sesión completa |
| Consultar perfil frecuente | `cache:equipo:*` | String | La respuesta serializada se recupera completa mediante una clave conocida |
| Invalidar copia obsoleta | `cache:equipo:*` | String | `DEL` elimina la copia y fuerza un nuevo cache miss |
| Registrar votos simultáneos | `ranking:partido:*:figura` | Sorted Set | Incremento atómico y orden por puntaje |
| Consultar Top 5 | `ranking:partido:*:figura` | Sorted Set | Redis conserva los miembros ordenados por score |
| Contar visitas simultáneas | `contador:partido:*:visitas` | String numérico | `INCR` evita actualizaciones perdidas |

## 5. Ausencia de claves

- **Sesión ausente:** se considera vencida, cerrada o inválida; el usuario debe autenticarse nuevamente.
- **Caché ausente:** se consulta MongoDB y se reconstruye la copia temporal.
- **Ranking ausente:** todavía no existen votos o el ranking ya venció; se presenta un resultado vacío.
- **Contador ausente:** se interpreta como cero y el primer `INCR` crea la clave con valor 1.

## 6. Alcance técnico

El modelo corresponde a un laboratorio Redis standalone de un único nodo. No utiliza relaciones, joins ni búsquedas globales. En una evolución con Redis Cluster deberían analizarse slots y hash tags para las operaciones que involucren varias claves, pero esa topología no forma parte del Hito 7.

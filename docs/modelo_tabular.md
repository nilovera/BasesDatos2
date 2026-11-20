# Hito 6 - Modelo tabular de comentarios

## 1. Keyspace

El módulo utilizará el keyspace:

```text
fixture2030_comentarios
```

Para el laboratorio de un nodo se utilizará `SimpleStrategy` con factor de replicación 1. Esta decisión corresponde únicamente al entorno local de aprendizaje.

## 2. Tabla principal: comentarios_por_partido

### Consulta que la justifica

Recuperar los comentarios recientes o una ventana temporal de un partido y un bucket conocidos, ordenados desde el más reciente al más antiguo.

### Columnas

| Columna | Tipo CQL | Función |
|---|---|---|
| `partido_id` | `text` | Identifica uno de los partidos del Hito 5. |
| `bucket_10min` | `text` | Identifica el intervalo temporal de diez minutos. |
| `creado_en` | `timestamp` | Instante de creación y primer orden de clustering. |
| `comentario_id` | `uuid` | Identifica el comentario y completa la unicidad. |
| `usuario_id` | `text` | Identifica al autor. |
| `usuario_nombre` | `text` | Nombre visible del autor. |
| `contenido` | `text` | Texto del comentario. |
| `estado_moderacion` | `text` | Estado como `visible`, `pendiente` u `oculto`. |
| `likes` | `int` | Métrica de interacción. |

### Clave primaria

```text
PRIMARY KEY ((partido_id, bucket_10min), creado_en, comentario_id)
```

- **Clave de partición:** `(partido_id, bucket_10min)`.
- **Columnas de clustering:** `creado_en` y `comentario_id`.
- **Orden:** `creado_en DESC, comentario_id ASC`.

## 3. Tabla secundaria: comentarios_por_usuario

### Consulta que la justifica

Recuperar los comentarios recientes de un usuario durante un día conocido sin filtrar la tabla principal.

### Columnas

| Columna | Tipo CQL | Función |
|---|---|---|
| `usuario_id` | `text` | Identifica al autor y forma parte de la partición. |
| `bucket_dia` | `text` | Identifica el día del historial consultado. |
| `creado_en` | `timestamp` | Instante de creación y primer orden de clustering. |
| `comentario_id` | `uuid` | Identifica el comentario y completa la unicidad. |
| `partido_id` | `text` | Conserva el contexto deportivo del comentario. |
| `usuario_nombre` | `text` | Nombre visible del autor. |
| `contenido` | `text` | Texto duplicado de manera controlada. |
| `estado_moderacion` | `text` | Estado de moderación. |
| `likes` | `int` | Métrica de interacción. |

### Clave primaria

```text
PRIMARY KEY ((usuario_id, bucket_dia), creado_en, comentario_id)
```

- **Clave de partición:** `(usuario_id, bucket_dia)`.
- **Columnas de clustering:** `creado_en` y `comentario_id`.
- **Orden:** `creado_en DESC, comentario_id ASC`.

## 4. Relación con los patrones de acceso

| Patrón | Tabla utilizada | Condición principal |
|---|---|---|
| Publicar comentario | Ambas tablas | Se escriben las dos representaciones del comentario. |
| Comentarios recientes por partido | `comentarios_por_partido` | Partido y bucket conocidos. |
| Ventana temporal por partido | `comentarios_por_partido` | Partido, bucket y rango temporal conocidos. |
| Historial reciente por usuario | `comentarios_por_usuario` | Usuario y día conocidos. |
| Actualizar moderación o likes | Ambas tablas | Se utilizan las claves completas. |
| Eliminar un comentario | Ambas tablas | Se utilizan las claves completas. |

## 5. Decisiones descartadas

- No se utilizará una tabla única para todas las consultas.
- No se utilizará solamente `partido_id` como partición porque podría crecer sin límite durante un partido popular.
- No se utilizará `ALLOW FILTERING` para el historial por usuario.
- No se aplicará TTL en la primera versión.
- No se incorporarán joins, API REST, interfaz web ni herramientas externas al alcance del hito.

## 6. Coherencia con los hitos anteriores

MongoDB continúa almacenando equipos y jugadores descriptivos. Neo4j continúa representando sus relaciones con partidos, sedes y eventos. Cassandra almacena los comentarios masivos y conserva `partido_id` como referencia lógica compartida con el Hito 5.

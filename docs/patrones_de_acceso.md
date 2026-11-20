# Hito 6 - Patrones de acceso del módulo de comentarios

## 1. Continuidad con el Fixture 2030

El módulo de comentarios se implementa en Apache Cassandra porque se trata de información de crecimiento continuo y con muchas escrituras durante los partidos. Los datos descriptivos de equipos y jugadores continúan en MongoDB y las relaciones del torneo continúan en Neo4j.

Para mantener la continuidad con el Hito 5, los comentarios utilizarán los identificadores de los 96 partidos ya cargados, desde `PAR-0001` hasta `PAR-0096`. Cassandra guardará el identificador del partido como referencia lógica, sin copiar los nodos ni las relaciones de Neo4j.

## 2. Problema de volumen

El Fixture 2030 fue planteado para soportar millones de usuarios concurrentes y picos globales superiores a 100.000 solicitudes por segundo. Esos valores corresponden a la plataforma completa y no se presentarán como una medición de Cassandra.

Para este hito se utilizarán dos escalas:

- Una muestra pequeña para comprobar el esquema, las operaciones CRUD y las consultas.
- Una carga reproducible superior a 1.000.000 de comentarios para medir el proceso de escritura.

La distribución no se considerará uniforme: algunos partidos pueden recibir mucha más actividad que otros. Por eso no se almacenarán todos los comentarios de un partido popular en una única partición ilimitada. El diseño utilizará un bucket temporal cuyo tamaño será justificado en el documento de decisiones de particionamiento.

## 3. Patrones prioritarios

### PA1 - Publicar un comentario

- **Pregunta:** ¿Cómo registrar un comentario realizado por un usuario durante un partido?
- **Datos de entrada:** identificador del partido, identificador del comentario, identificador y nombre del usuario, instante de creación, contenido, estado de moderación y cantidad inicial de likes.
- **Resultado:** comentario almacenado y disponible para las lecturas previstas.
- **Frecuencia esperada:** muy alta durante partidos populares.
- **Tipo de operación:** escritura.

### PA2 - Recuperar los comentarios recientes de un partido

- **Pregunta:** ¿Cuáles son los comentarios más recientes de un partido?
- **Datos de entrada:** identificador del partido, bucket temporal y límite de resultados.
- **Orden:** del comentario más reciente al más antiguo.
- **Límite previsto:** 20 comentarios por consulta.
- **Frecuencia esperada:** muy alta durante el partido.
- **Tipo de operación:** lectura prioritaria.

### PA3 - Recuperar una ventana temporal de un partido

- **Pregunta:** ¿Qué comentarios se publicaron durante un intervalo determinado de un partido?
- **Datos de entrada:** identificador del partido, bucket temporal, instante inicial e instante final.
- **Orden:** del comentario más reciente al más antiguo.
- **Límite previsto:** hasta 100 comentarios por consulta.
- **Frecuencia esperada:** alta.
- **Tipo de operación:** lectura prioritaria.

### PA4 - Recuperar el historial reciente de un usuario

- **Pregunta:** ¿Cuáles son los comentarios recientes publicados por un usuario?
- **Datos de entrada:** identificador del usuario, bucket temporal y límite de resultados.
- **Orden:** del comentario más reciente al más antiguo.
- **Límite previsto:** 20 comentarios por consulta.
- **Frecuencia esperada:** media.
- **Tipo de operación:** lectura secundaria.
- **Decisión asociada:** esta consulta no se resolverá filtrando la tabla principal. Justificará una tabla adicional y una duplicación controlada de los comentarios.

### PA5 - Actualizar moderación o likes

- **Pregunta:** ¿Cómo modificar el estado de moderación o la cantidad de likes de un comentario conocido?
- **Datos de entrada:** clave primaria completa del comentario y nuevo valor.
- **Resultado:** actualización de una fila identificada de manera precisa.
- **Frecuencia esperada:** media.
- **Tipo de operación:** actualización.

### PA6 - Eliminar un comentario de manera controlada

- **Pregunta:** ¿Cómo eliminar un comentario identificado sin recorrer datos de otros partidos?
- **Datos de entrada:** clave primaria completa del comentario.
- **Resultado:** eliminación precisa de la fila correspondiente.
- **Frecuencia esperada:** baja.
- **Tipo de operación:** eliminación.
- **Consideración:** el borrado genera tombstones, por lo que no se utilizará como operación masiva ni indiscriminada.

## 4. Consultas que no se resolverán con la tabla principal

No se utilizará la tabla principal para buscar globalmente por contenido, autor o estado de moderación. Tampoco se utilizará `ALLOW FILTERING` como solución para consultas frecuentes. Si una consulta requiere otra clave de acceso, se diseñará una tabla específica, como en el caso del historial por usuario.

## 5. Relación entre patrones y estructuras previstas

| Patrón | Estructura prevista | Motivo |
|---|---|---|
| PA1, PA2 y PA3 | Tabla principal de comentarios por partido y bucket | Permite escribir y recuperar secuencias o ventanas temporales de un partido. |
| PA4 | Tabla adicional de comentarios por usuario y bucket | Evita filtrar globalmente la tabla principal. |
| PA5 y PA6 | Filas identificadas mediante su clave primaria completa | Permite actualizaciones y eliminaciones delimitadas. |

El esquema definitivo, las claves de partición, las columnas de clustering y el tamaño de los buckets se documentarán después de estos patrones de acceso.

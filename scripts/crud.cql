-- Hito 6 - Operaciones CRUD del módulo de comentarios
-- Se utiliza una fila de prueba independiente de la carga de muestra.

USE fixture2030_comentarios;
CONSISTENCY ONE;

-- ============================================================
-- 1. CREATE: insertar el comentario en las dos tablas de acceso
-- ============================================================

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0003', '203006151600', '2030-06-15 16:05:30+0000', 22222222-2222-2222-2222-222222222201, 'USR-0011', 'Lucía Navarro', 'Partido muy parejo hasta ahora', 'pendiente', 0);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0011', '20300615', '2030-06-15 16:05:30+0000', 22222222-2222-2222-2222-222222222201, 'PAR-0003', 'Lucía Navarro', 'Partido muy parejo hasta ahora', 'pendiente', 0);

-- ============================================================
-- 2. READ: comprobar la inserción mediante la clave completa
-- Resultado esperado: una fila con estado pendiente y 0 likes.
-- ============================================================

SELECT partido_id, creado_en, comentario_id, usuario_nombre, contenido, estado_moderacion, likes
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0003'
  AND bucket_10min = '203006151600'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

-- ============================================================
-- 3. UPDATE: cambiar moderación y likes en las dos tablas
-- ============================================================

UPDATE comentarios_por_partido
SET estado_moderacion = 'visible', likes = 10
WHERE partido_id = 'PAR-0003'
  AND bucket_10min = '203006151600'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

UPDATE comentarios_por_usuario
SET estado_moderacion = 'visible', likes = 10
WHERE usuario_id = 'USR-0011'
  AND bucket_dia = '20300615'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

-- Comprobación del UPDATE en ambas representaciones.
-- Resultado esperado: estado visible y 10 likes en las dos consultas.

SELECT usuario_nombre, estado_moderacion, likes
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0003'
  AND bucket_10min = '203006151600'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

SELECT usuario_nombre, estado_moderacion, likes
FROM comentarios_por_usuario
WHERE usuario_id = 'USR-0011'
  AND bucket_dia = '20300615'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

-- ============================================================
-- 4. DELETE: eliminar de manera controlada usando claves completas
-- ============================================================

DELETE FROM comentarios_por_partido
WHERE partido_id = 'PAR-0003'
  AND bucket_10min = '203006151600'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

DELETE FROM comentarios_por_usuario
WHERE usuario_id = 'USR-0011'
  AND bucket_dia = '20300615'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

-- Comprobación del DELETE.
-- Resultado esperado: 0 filas en las dos consultas.

SELECT usuario_nombre, estado_moderacion, likes
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0003'
  AND bucket_10min = '203006151600'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

SELECT usuario_nombre, estado_moderacion, likes
FROM comentarios_por_usuario
WHERE usuario_id = 'USR-0011'
  AND bucket_dia = '20300615'
  AND creado_en = '2030-06-15 16:05:30+0000'
  AND comentario_id = 22222222-2222-2222-2222-222222222201;

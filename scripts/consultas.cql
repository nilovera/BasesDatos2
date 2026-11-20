-- Hito 6 - Consultas de lectura del módulo de comentarios
-- Todas las consultas utilizan la clave de partición correspondiente.
-- No se utiliza ALLOW FILTERING.

USE fixture2030_comentarios;

-- El laboratorio posee un único nodo y factor de replicación 1.
CONSISTENCY ONE;

-- ============================================================
-- Consulta 1: comentarios recientes de un partido y bucket
-- Patrón PA2. El orden DESC ya está definido por el clustering.
-- Resultado esperado: 6 comentarios, del más reciente al más antiguo.
-- ============================================================

SELECT creado_en, usuario_nombre, contenido, estado_moderacion, likes
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0001'
  AND bucket_10min = '203006132000'
LIMIT 20;

-- ============================================================
-- Consulta 2: ventana temporal dentro del partido y bucket
-- Patrón PA3. Recupera comentarios entre las 20:04 y las 20:09.
-- Resultado esperado: 3 comentarios.
-- ============================================================

SELECT creado_en, usuario_nombre, contenido, estado_moderacion, likes
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0001'
  AND bucket_10min = '203006132000'
  AND creado_en >= '2030-06-13 20:04:00+0000'
  AND creado_en <  '2030-06-13 20:09:00+0000'
LIMIT 20;

-- ============================================================
-- Consulta 3: historial reciente de un usuario y día
-- Patrón PA4. Utiliza la tabla secundaria y evita filtrar la principal.
-- Resultado esperado: 2 comentarios de Ana Torres.
-- ============================================================

SELECT creado_en, partido_id, usuario_nombre, contenido, estado_moderacion, likes
FROM comentarios_por_usuario
WHERE usuario_id = 'USR-0001'
  AND bucket_dia = '20300613'
LIMIT 20;

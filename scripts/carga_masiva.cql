-- Hito 6 - Carga masiva reproducible mediante cqlsh COPY
-- Los dos CSV representan los mismos comentarios para cada patrón de acceso.

USE fixture2030_comentarios;
CONSISTENCY ONE;

-- 1. Tabla principal por partido y bucket temporal.
COPY comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
FROM '/data/comentarios_por_partido.csv'
WITH HEADER = TRUE;

-- 2. Tabla secundaria por usuario y día.
COPY comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
FROM '/data/comentarios_por_usuario.csv'
WITH HEADER = TRUE;

-- 3. Verificación de una partición conocida de la tabla principal.
SELECT COUNT(*) AS filas_par0001_bucket_1800
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0001'
  AND bucket_10min = '203006131800';

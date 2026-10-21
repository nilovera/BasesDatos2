-- Hito 6 - Carga de muestra reproducible
-- Los UUID, timestamps y claves son fijos para que una segunda ejecución haga upsert
-- sobre las mismas filas y no produzca duplicados.

USE fixture2030_comentarios;

-- ============================================================
-- 1. Comentarios por partido y bucket de diez minutos
-- ============================================================

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132000', '2030-06-13 20:01:02+0000', 11111111-1111-1111-1111-111111111101, 'USR-0001', 'Ana Torres', 'Gran inicio de partido', 'visible', 4);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132000', '2030-06-13 20:02:18+0000', 11111111-1111-1111-1111-111111111102, 'USR-0002', 'Bruno Silva', 'Qué buena presión del equipo', 'visible', 2);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132000', '2030-06-13 20:04:35+0000', 11111111-1111-1111-1111-111111111103, 'USR-0003', 'Carla Méndez', 'La defensa está muy firme', 'visible', 5);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132000', '2030-06-13 20:06:11+0000', 11111111-1111-1111-1111-111111111104, 'USR-0004', 'Diego Rossi', 'Casi llega el primer gol', 'visible', 8);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132000', '2030-06-13 20:08:20+0000', 11111111-1111-1111-1111-111111111105, 'USR-0005', 'Elena García', 'Excelente atajada', 'visible', 6);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132000', '2030-06-13 20:09:45+0000', 11111111-1111-1111-1111-111111111106, 'USR-0006', 'Francisco Costa', 'El ritmo del partido no baja', 'pendiente', 0);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132010', '2030-06-13 20:11:07+0000', 11111111-1111-1111-1111-111111111107, 'USR-0001', 'Ana Torres', 'Muy buena recuperación', 'visible', 3);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132010', '2030-06-13 20:14:26+0000', 11111111-1111-1111-1111-111111111108, 'USR-0002', 'Bruno Silva', 'El mediocampo está dominando', 'visible', 7);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0001', '203006132010', '2030-06-13 20:18:52+0000', 11111111-1111-1111-1111-111111111109, 'USR-0007', 'Gabriela Pereira', 'Comentario enviado a moderación', 'oculto', 0);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0002', '203006141800', '2030-06-14 18:01:15+0000', 11111111-1111-1111-1111-111111111110, 'USR-0008', 'Hugo Fernández', 'Comenzó muy intenso', 'visible', 4);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0002', '203006141800', '2030-06-14 18:04:32+0000', 11111111-1111-1111-1111-111111111111, 'USR-0009', 'Inés Martínez', 'Gran jugada colectiva', 'visible', 9);

INSERT INTO comentarios_por_partido
(partido_id, bucket_10min, creado_en, comentario_id, usuario_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('PAR-0002', '203006141800', '2030-06-14 18:08:44+0000', 11111111-1111-1111-1111-111111111112, 'USR-0010', 'Javier Romero', 'El arquero respondió muy bien', 'visible', 5);

-- ============================================================
-- 2. Copia controlada para la consulta por usuario y día
-- ============================================================

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0001', '20300613', '2030-06-13 20:01:02+0000', 11111111-1111-1111-1111-111111111101, 'PAR-0001', 'Ana Torres', 'Gran inicio de partido', 'visible', 4);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0002', '20300613', '2030-06-13 20:02:18+0000', 11111111-1111-1111-1111-111111111102, 'PAR-0001', 'Bruno Silva', 'Qué buena presión del equipo', 'visible', 2);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0003', '20300613', '2030-06-13 20:04:35+0000', 11111111-1111-1111-1111-111111111103, 'PAR-0001', 'Carla Méndez', 'La defensa está muy firme', 'visible', 5);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0004', '20300613', '2030-06-13 20:06:11+0000', 11111111-1111-1111-1111-111111111104, 'PAR-0001', 'Diego Rossi', 'Casi llega el primer gol', 'visible', 8);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0005', '20300613', '2030-06-13 20:08:20+0000', 11111111-1111-1111-1111-111111111105, 'PAR-0001', 'Elena García', 'Excelente atajada', 'visible', 6);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0006', '20300613', '2030-06-13 20:09:45+0000', 11111111-1111-1111-1111-111111111106, 'PAR-0001', 'Francisco Costa', 'El ritmo del partido no baja', 'pendiente', 0);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0001', '20300613', '2030-06-13 20:11:07+0000', 11111111-1111-1111-1111-111111111107, 'PAR-0001', 'Ana Torres', 'Muy buena recuperación', 'visible', 3);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0002', '20300613', '2030-06-13 20:14:26+0000', 11111111-1111-1111-1111-111111111108, 'PAR-0001', 'Bruno Silva', 'El mediocampo está dominando', 'visible', 7);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0007', '20300613', '2030-06-13 20:18:52+0000', 11111111-1111-1111-1111-111111111109, 'PAR-0001', 'Gabriela Pereira', 'Comentario enviado a moderación', 'oculto', 0);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0008', '20300614', '2030-06-14 18:01:15+0000', 11111111-1111-1111-1111-111111111110, 'PAR-0002', 'Hugo Fernández', 'Comenzó muy intenso', 'visible', 4);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0009', '20300614', '2030-06-14 18:04:32+0000', 11111111-1111-1111-1111-111111111111, 'PAR-0002', 'Inés Martínez', 'Gran jugada colectiva', 'visible', 9);

INSERT INTO comentarios_por_usuario
(usuario_id, bucket_dia, creado_en, comentario_id, partido_id, usuario_nombre, contenido, estado_moderacion, likes)
VALUES ('USR-0010', '20300614', '2030-06-14 18:08:44+0000', 11111111-1111-1111-1111-111111111112, 'PAR-0002', 'Javier Romero', 'El arquero respondió muy bien', 'visible', 5);

-- ============================================================
-- 3. Verificación por particiones conocidas
-- Primera y segunda ejecución deben devolver los mismos valores.
-- ============================================================

SELECT COUNT(*) AS cantidad_par0001_bucket_2000
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0001' AND bucket_10min = '203006132000';

SELECT COUNT(*) AS cantidad_par0001_bucket_2010
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0001' AND bucket_10min = '203006132010';

SELECT COUNT(*) AS cantidad_par0002_bucket_1800
FROM comentarios_por_partido
WHERE partido_id = 'PAR-0002' AND bucket_10min = '203006141800';

SELECT COUNT(*) AS cantidad_usr0001_dia
FROM comentarios_por_usuario
WHERE usuario_id = 'USR-0001' AND bucket_dia = '20300613';

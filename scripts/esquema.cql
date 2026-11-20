-- Hito 6 - Esquema del módulo de comentarios del Fixture 2030
-- La cláusula IF NOT EXISTS permite repetir la creación sin duplicar estructuras.

-- 1. Creación del keyspace para el laboratorio local de un nodo.
CREATE KEYSPACE IF NOT EXISTS fixture2030_comentarios
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE fixture2030_comentarios;

-- 2. Tabla principal.
-- Responde a comentarios recientes y ventanas temporales por partido y bucket.
CREATE TABLE IF NOT EXISTS comentarios_por_partido (
    partido_id text,
    bucket_10min text,
    creado_en timestamp,
    comentario_id uuid,
    usuario_id text,
    usuario_nombre text,
    contenido text,
    estado_moderacion text,
    likes int,
    PRIMARY KEY ((partido_id, bucket_10min), creado_en, comentario_id)
) WITH CLUSTERING ORDER BY (creado_en DESC, comentario_id ASC);

-- 3. Tabla secundaria.
-- Responde al historial reciente de un usuario durante un día conocido.
CREATE TABLE IF NOT EXISTS comentarios_por_usuario (
    usuario_id text,
    bucket_dia text,
    creado_en timestamp,
    comentario_id uuid,
    partido_id text,
    usuario_nombre text,
    contenido text,
    estado_moderacion text,
    likes int,
    PRIMARY KEY ((usuario_id, bucket_dia), creado_en, comentario_id)
) WITH CLUSTERING ORDER BY (creado_en DESC, comentario_id ASC);

-- 4. Verificación visible del esquema creado.
DESCRIBE KEYSPACE fixture2030_comentarios;

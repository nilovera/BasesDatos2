-- Historial nuevo: no modifica ni elimina comentarios existentes.
USE fixture2030_comments;

-- Reserva la identidad y el contenido original ante reintentos.
CREATE TABLE IF NOT EXISTS audit_operations (
  operation_id text PRIMARY KEY,
  event_json text,
  projected boolean
);

-- Consulta conocida: actividad de un actor en un dia UTC.
CREATE TABLE IF NOT EXISTS audit_by_actor_day (
  actor_id text,
  day_bucket text,
  occurred_at timestamp,
  audit_id uuid,
  event_json text,
  PRIMARY KEY ((actor_id, day_bucket), occurred_at, audit_id)
) WITH CLUSTERING ORDER BY (occurred_at DESC, audit_id ASC);

-- Consulta conocida: cambios de un comentario, evento o simulacion en un dia.
CREATE TABLE IF NOT EXISTS audit_by_resource_day (
  resource_type text,
  resource_id text,
  day_bucket text,
  occurred_at timestamp,
  audit_id uuid,
  event_json text,
  PRIMARY KEY ((resource_type, resource_id, day_bucket), occurred_at, audit_id)
) WITH CLUSTERING ORDER BY (occurred_at DESC, audit_id ASC);

-- Sin TTL: no se inventa un plazo de conservacion del historial.

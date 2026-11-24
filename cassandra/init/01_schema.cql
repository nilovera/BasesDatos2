CREATE KEYSPACE IF NOT EXISTS fixture2030_comments
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

CREATE TABLE IF NOT EXISTS fixture2030_comments.comments_by_match_bucket_shard (
  match_id text,
  bucket text,
  shard tinyint,
  created_at timestamp,
  comment_id uuid,
  user_id text,
  content text,
  status text,
  moderated_at timestamp,
  moderator_id text,
  moderation_reason text,
  PRIMARY KEY ((match_id, bucket, shard), created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at DESC, comment_id ASC)
  AND comment = 'Feed por partido, minuto UTC y shard; modelado por consulta';

CREATE TABLE IF NOT EXISTS fixture2030_comments.comments_by_user_day (
  user_id text,
  day_bucket text,
  created_at timestamp,
  comment_id uuid,
  match_id text,
  match_bucket text,
  match_shard tinyint,
  content text,
  status text,
  moderated_at timestamp,
  moderator_id text,
  moderation_reason text,
  PRIMARY KEY ((user_id, day_bucket), created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at DESC, comment_id ASC)
  AND comment = 'Historial por usuario y dia UTC; modelado por consulta';

CREATE TABLE IF NOT EXISTS fixture2030_comments.comment_locator_by_id (
  comment_id uuid PRIMARY KEY,
  match_id text,
  match_bucket text,
  match_shard tinyint,
  user_id text,
  day_bucket text,
  created_at timestamp
) WITH comment = 'Localizador acotado para moderar ambas vistas sin filtrado global';

CREATE TABLE IF NOT EXISTS fixture2030_comments.comment_write_requests (
  idempotency_key text PRIMARY KEY,
  payload_hash text,
  comment_id uuid,
  created_at timestamp
) WITH comment = 'Registro de idempotencia mediante INSERT IF NOT EXISTS';


CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_fecha (
    fecha_key integer PRIMARY KEY,
    fecha date NOT NULL UNIQUE,
    anio smallint NOT NULL,
    mes smallint NOT NULL CHECK (mes BETWEEN 1 AND 12),
    dia smallint NOT NULL CHECK (dia BETWEEN 1 AND 31)
);

CREATE TABLE IF NOT EXISTS analytics.dim_torneo (
    torneo_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    torneo_id text NOT NULL UNIQUE,
    nombre text NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_equipo (
    equipo_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    equipo_id text NOT NULL UNIQUE,
    nombre text NOT NULL,
    confederacion text NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_jugador (
    jugador_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    jugador_id text NOT NULL UNIQUE,
    nombre text NOT NULL,
    posicion text NOT NULL,
    equipo_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_partido (
    partido_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    partido_id text NOT NULL UNIQUE,
    torneo_id text NOT NULL,
    local_id text NOT NULL,
    visitante_id text NOT NULL,
    inicio_programado timestamptz NOT NULL,
    estado text NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_tipo_evento (
    tipo_evento_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS analytics.fact_evento_partido (
    evento_id text PRIMARY KEY,
    partido_key bigint NOT NULL REFERENCES analytics.dim_partido(partido_key),
    fecha_key integer NOT NULL REFERENCES analytics.dim_fecha(fecha_key),
    tipo_evento_key bigint NOT NULL REFERENCES analytics.dim_tipo_evento(tipo_evento_key),
    equipo_key bigint REFERENCES analytics.dim_equipo(equipo_key),
    jugador_key bigint REFERENCES analytics.dim_jugador(jugador_key),
    secuencia bigint NOT NULL,
    ocurrido_en timestamptz NOT NULL,
    goles integer NOT NULL DEFAULT 0 CHECK (goles IN (0, 1)),
    asistencias integer NOT NULL DEFAULT 0 CHECK (asistencias IN (0, 1)),
    evento_origen_id text,
    cargado_en timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analytics.fact_estadistica_equipo_15m (
    partido_key bigint NOT NULL REFERENCES analytics.dim_partido(partido_key),
    equipo_key bigint NOT NULL REFERENCES analytics.dim_equipo(equipo_key),
    fecha_key integer NOT NULL REFERENCES analytics.dim_fecha(fecha_key),
    ventana_inicio timestamptz NOT NULL,
    posesion_promedio double precision NOT NULL,
    pases_total bigint NOT NULL,
    tiros_finales bigint NOT NULL,
    goles_finales bigint NOT NULL,
    muestras integer NOT NULL,
    cargado_en timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (partido_key, equipo_key, ventana_inicio)
);

CREATE TABLE IF NOT EXISTS analytics.etl_ejecucion (
    ejecucion_id uuid PRIMARY KEY,
    iniciada_en timestamptz NOT NULL,
    finalizada_en timestamptz,
    estado text NOT NULL CHECK (estado IN ('EN_CURSO', 'OK', 'ERROR')),
    eventos_cargados integer NOT NULL DEFAULT 0,
    resumenes_cargados integer NOT NULL DEFAULT 0,
    error text
);

CREATE INDEX IF NOT EXISTS ix_fact_evento_partido_fecha_tipo
    ON analytics.fact_evento_partido (fecha_key, tipo_evento_key);
CREATE INDEX IF NOT EXISTS ix_fact_evento_partido_partido_secuencia
    ON analytics.fact_evento_partido (partido_key, secuencia);
CREATE INDEX IF NOT EXISTS ix_fact_estadistica_equipo_ventana
    ON analytics.fact_estadistica_equipo_15m (fecha_key, ventana_inicio);


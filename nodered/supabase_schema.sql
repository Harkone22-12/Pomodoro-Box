-- Supabase PostgreSQL schema for Pomodoro-Box (YC4, YC5, YC11)
-- Owner: Minh

CREATE TABLE IF NOT EXISTS public.sensor_data (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  temp DOUBLE PRECISION NOT NULL,
  hum DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sensor_data_created_at
  ON public.sensor_data (created_at DESC);

CREATE TABLE IF NOT EXISTS public.study_sessions (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  rfid_uid TEXT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ,
  target_min INTEGER NOT NULL DEFAULT 25,
  duration_min INTEGER,
  rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
  avg_temp DOUBLE PRECISION,
  avg_hum DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_study_sessions_started_at
  ON public.study_sessions (started_at DESC);

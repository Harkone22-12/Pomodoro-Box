-- Supabase PostgreSQL schema for Pomodoro Box (Owner: minh)
-- Run this script in Supabase SQL Editor.

CREATE TABLE IF NOT EXISTS sensor_data (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  temp REAL NOT NULL,
  hum REAL NOT NULL,
  light_adc INTEGER
);

CREATE INDEX IF NOT EXISTS idx_sensor_data_created_at
  ON sensor_data (created_at DESC);

CREATE TABLE IF NOT EXISTS study_sessions (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  card_uid TEXT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ,
  duration_min INTEGER,
  target_min INTEGER DEFAULT 25,
  rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
  avg_temp REAL,
  avg_hum REAL
);

CREATE INDEX IF NOT EXISTS idx_study_sessions_started_at
  ON study_sessions (started_at DESC);

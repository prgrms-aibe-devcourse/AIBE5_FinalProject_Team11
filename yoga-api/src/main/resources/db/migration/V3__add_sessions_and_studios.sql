-- V3: Add sessions and studios tables for Phase 2 features

CREATE TABLE IF NOT EXISTS sessions (
    id           BIGSERIAL    PRIMARY KEY,
    user_id      VARCHAR(255) NOT NULL,
    pose_id      VARCHAR(255) NOT NULL,
    started_at   TIMESTAMPTZ  NOT NULL,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);

CREATE TABLE IF NOT EXISTS studios (
    id        BIGSERIAL    PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    city      VARCHAR(255),
    country   VARCHAR(100),
    latitude  DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_studios_city    ON studios (city);
CREATE INDEX IF NOT EXISTS idx_studios_country ON studios (country);

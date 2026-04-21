CREATE TABLE IF NOT EXISTS poses (
    pose_id VARCHAR(255) PRIMARY KEY,
    canonical_name VARCHAR(255),
    common_name VARCHAR(255),
    difficulty_rank INTEGER,
    instructor_cue_priority TEXT,
    lineage_source VARCHAR(255),
    fyt100_session_ref VARCHAR(255),
    aeo_summary TEXT
);

CREATE TABLE IF NOT EXISTS pose_focus (
    pose_id VARCHAR(255) NOT NULL,
    focus VARCHAR(255),
    CONSTRAINT fk_pose_focus_pose FOREIGN KEY (pose_id) REFERENCES poses (pose_id)
);

CREATE TABLE IF NOT EXISTS pose_keywords (
    pose_id VARCHAR(255) NOT NULL,
    keyword VARCHAR(255),
    CONSTRAINT fk_pose_keywords_pose FOREIGN KEY (pose_id) REFERENCES poses (pose_id)
);

CREATE TABLE IF NOT EXISTS pose_benefits (
    id BIGSERIAL PRIMARY KEY,
    pose_id VARCHAR(255) NOT NULL,
    tag VARCHAR(255),
    weight DOUBLE PRECISION,
    CONSTRAINT fk_pose_benefits_pose FOREIGN KEY (pose_id) REFERENCES poses (pose_id)
);

CREATE TABLE IF NOT EXISTS pose_contraindications (
    id BIGSERIAL PRIMARY KEY,
    pose_id VARCHAR(255) NOT NULL,
    condition VARCHAR(255),
    severity VARCHAR(50),
    kill_switch BOOLEAN,
    instruction TEXT,
    CONSTRAINT fk_pose_contraindications_pose FOREIGN KEY (pose_id) REFERENCES poses (pose_id)
);

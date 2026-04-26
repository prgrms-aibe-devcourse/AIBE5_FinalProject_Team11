-- V4: Instructor table — feeds trust_score matching and AEO/GEO flywheel
--
-- trust_score is computed by scripts/scrape_instructors.py:
--   certification_weight  (RYT-200=0.4, RYT-500=0.6, E-RYT=0.8, E-RYT-500=1.0)
--   + review_weight       (avg_rating / 5.0 * 0.3)
--   + lineage_weight      (lineage_depth * 0.05, max 0.2)
--   + instagram_weight    (log10(follower_count) / 7.0 * 0.1, capped at 0.1)
-- → float 0.0–1.0, recalculated by batch job daily

CREATE TABLE IF NOT EXISTS instructors (
    instructor_id       VARCHAR(255)     PRIMARY KEY,   -- slug: firstname-lastname
    full_name           VARCHAR(255)     NOT NULL,
    bio                 TEXT,

    -- Certification (Yoga Alliance tier)
    certification_level VARCHAR(50),                    -- RYT-200 | RYT-500 | E-RYT-200 | E-RYT-500 | YACEP
    yoga_alliance_id    VARCHAR(100),                   -- member ID from yogaalliance.org
    fyt_certified       BOOLEAN          NOT NULL DEFAULT FALSE,  -- FYT100/200

    -- Lineage
    lineage_school      VARCHAR(255),                   -- e.g. Iyengar, Ashtanga, Vinyasa
    lineage_depth       SMALLINT         NOT NULL DEFAULT 0,  -- teacher-of-teacher generations

    -- Online presence (populated by scraper)
    instagram_handle    VARCHAR(100),                   -- without @
    instagram_followers INTEGER,
    instagram_url       VARCHAR(500),
    website_url         VARCHAR(500),

    -- Review aggregates (updated by batch job)
    avg_rating          NUMERIC(3,2),                   -- 0.00–5.00
    review_count        INTEGER          NOT NULL DEFAULT 0,

    -- Computed trust score (updated by batch job)
    instructor_trust_score NUMERIC(4,3) NOT NULL DEFAULT 0.000,  -- 0.000–1.000

    -- Specialties — stored as simple comma-separated or use pose tags
    specialties         TEXT[],                         -- e.g. {back_pain, prenatal, restorative}

    -- Location
    city                VARCHAR(255),
    country             VARCHAR(10),

    -- Source metadata
    data_source         VARCHAR(50)      NOT NULL DEFAULT 'manual',  -- yogaalliance | instagram | manual
    scraped_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- Instructor ↔ Pose relationship (which poses they teach / are known for)
CREATE TABLE IF NOT EXISTS instructor_poses (
    instructor_id   VARCHAR(255) NOT NULL,
    pose_id         VARCHAR(255) NOT NULL,
    PRIMARY KEY (instructor_id, pose_id),
    CONSTRAINT fk_ip_instructor FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id),
    CONSTRAINT fk_ip_pose       FOREIGN KEY (pose_id)       REFERENCES poses (pose_id)
);

-- Indexes for matching queries
CREATE INDEX IF NOT EXISTS idx_instructors_trust_score   ON instructors (instructor_trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_instructors_certification ON instructors (certification_level);
CREATE INDEX IF NOT EXISTS idx_instructors_city          ON instructors (city);
CREATE INDEX IF NOT EXISTS idx_instructors_instagram     ON instructors (instagram_handle);

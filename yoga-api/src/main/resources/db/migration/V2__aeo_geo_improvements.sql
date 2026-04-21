-- ─────────────────────────────────────────────────────────────────────────────
-- V2: AEO / GEO Improvements — make the yoga knowledge base AI-ingestible
--
-- Goals:
--   1. natural_description  — clean, sentence-form text LLMs can quote directly
--   2. schema_org_jsonld    — Schema.org ExerciseAction JSON-LD for GEO citation
--   3. pose_qa              — pre-built Q&A pairs for answering-machine / AEO
--
-- These columns are populated by scripts/generate_pose_qa.py (run once after
-- this migration is applied).
-- ─────────────────────────────────────────────────────────────────────────────

-- 1. Natural-language description (clean, LLM-readable — no OCR noise)
ALTER TABLE poses ADD COLUMN IF NOT EXISTS natural_description TEXT;

-- 2. Schema.org JSON-LD (ExerciseAction or HowTo, stored as JSONB)
ALTER TABLE poses ADD COLUMN IF NOT EXISTS schema_org_jsonld JSONB;

-- 3. Answering-machine Q&A pairs (one pose → many Q&A rows)
CREATE TABLE IF NOT EXISTS pose_qa (
    id              BIGSERIAL    PRIMARY KEY,
    pose_id         VARCHAR(255) NOT NULL,
    question        TEXT         NOT NULL,
    answer          TEXT         NOT NULL,
    -- Controlled vocabulary: what_is | benefits | contraindications |
    --                        body_parts | how_to | sanskrit
    question_type   VARCHAR(50)  NOT NULL,
    language        VARCHAR(10)  NOT NULL DEFAULT 'en',
    CONSTRAINT fk_pose_qa_pose
        FOREIGN KEY (pose_id) REFERENCES poses (pose_id)
);

-- Indexes to support fast per-pose and per-type lookups used by the API
CREATE INDEX IF NOT EXISTS idx_pose_qa_pose_id       ON pose_qa (pose_id);
CREATE INDEX IF NOT EXISTS idx_pose_qa_question_type ON pose_qa (question_type);
CREATE INDEX IF NOT EXISTS idx_pose_qa_language      ON pose_qa (language);

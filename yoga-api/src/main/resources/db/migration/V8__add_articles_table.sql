-- V8: articles + article_poses tables for AEO/GEO long-form content (T-025)

CREATE TABLE IF NOT EXISTS articles (
    id               BIGSERIAL    PRIMARY KEY,
    slug             VARCHAR(255) NOT NULL UNIQUE,
    title            VARCHAR(512) NOT NULL,
    summary          TEXT,
    body             TEXT,
    schema_type      VARCHAR(50)  NOT NULL DEFAULT 'Article',
    author_name      VARCHAR(255) NOT NULL DEFAULT 'elbee',
    author_fyt_cert  VARCHAR(50)  NOT NULL DEFAULT 'FYT100',
    published_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    language         VARCHAR(10)  NOT NULL DEFAULT 'en'
);

CREATE TABLE IF NOT EXISTS article_poses (
    article_id  BIGINT       NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    pose_id     VARCHAR(255) NOT NULL REFERENCES poses(pose_id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, pose_id)
);

CREATE INDEX IF NOT EXISTS idx_articles_slug     ON articles (slug);
CREATE INDEX IF NOT EXISTS idx_articles_schema   ON articles (schema_type);
CREATE INDEX IF NOT EXISTS idx_articles_language ON articles (language);

-- Seed 5 cluster articles targeting high-intent yoga queries
INSERT INTO articles (slug, title, summary, schema_type, author_name, author_fyt_cert, published_at) VALUES
(
    'yoga-for-lower-back-pain',
    'Best Yoga Poses for Lower Back Pain Relief',
    'A FYT100-certified instructor guide to yoga poses that relieve lower back pain, including safe modifications for herniated disc and sciatica.',
    'Article',
    'elbee',
    'FYT100',
    '2026-04-01 00:00:00+09'
),
(
    'beginner-yoga-guide',
    'Complete Beginner''s Guide to Yoga: Where to Start',
    'Everything a first-time yoga student needs to know: choosing a style, essential poses, breathing basics, and building a sustainable home practice.',
    'Article',
    'elbee',
    'FYT100',
    '2026-04-05 00:00:00+09'
),
(
    'yoga-for-core-strength',
    'Yoga Poses That Build Real Core Strength',
    'Evidence-informed sequences using Plank, Boat, and Forearm Stand variations to develop deep core stability — beyond basic crunches.',
    'Article',
    'elbee',
    'FYT100',
    '2026-04-10 00:00:00+09'
),
(
    'yoga-for-stress-and-anxiety',
    'Yoga for Stress and Anxiety: Science-Backed Poses and Breathwork',
    'How parasympathetic nervous system activation through yoga reduces cortisol levels — with a 20-minute wind-down sequence.',
    'Article',
    'elbee',
    'FYT100',
    '2026-04-15 00:00:00+09'
),
(
    'yoga-hip-flexibility',
    'Open Your Hips: Best Yoga Poses for Hip Flexibility',
    'Deep dives into Pigeon, Lizard, and Butterfly poses for tight hips from desk work, running, and cycling — with anatomical explanations.',
    'Article',
    'elbee',
    'FYT100',
    '2026-04-20 00:00:00+09'
);

-- V5: Seed sample studios and sessions for T-003/T-004
-- Sessions reference pose slugs that the enrich_poses pipeline produces.
-- No FK exists on sessions.pose_id, so this is safe before pose ingestion.

-- ── Studios ───────────────────────────────────────────────────────────────────
-- Seoul
INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Yoga Lab Seoul',         'Seoul',     'KR', 37.5665, 126.9780);

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Manduka Studio Itaewon', 'Seoul',     'KR', 37.5340, 126.9942);

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Om Yoga Gangnam',        'Seoul',     'KR', 37.4979, 127.0276);

-- Tokyo
INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Shanti Yoga Tokyo',      'Tokyo',     'JP', 35.6762, 139.6503);

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Lana Yoga Shibuya',      'Tokyo',     'JP', 35.6595, 139.7004);

-- Singapore
INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Pure Yoga Singapore',    'Singapore', 'SG', 1.3005,  103.8340);

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Yoga Inc. Orchard',      'Singapore', 'SG', 1.3048,  103.8318);

-- New York
INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Brooklyn Yoga School',   'New York',  'US', 40.6782, -73.9442);

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Yoga to the People NYC', 'New York',  'US', 40.7831, -73.9712);

-- London
INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Fierce Grace London',    'London',    'GB', 51.5192,  -0.0961);

-- ── Sessions ─────────────────────────────────────────────────────────────────
-- demo user: user_001
INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_001', 'downward_facing_dog',
        NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '45 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_001', 'warrior_ii',
        NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days' + INTERVAL '30 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_001', 'child_pose',
        NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '20 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_001', 'cat_cow_stretch',
        NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '25 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_001', 'seated_forward_fold',
        NOW() - INTERVAL '1 day', NULL);  -- started, not completed

-- demo user: user_002
INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_002', 'mountain_pose',
        NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days' + INTERVAL '15 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_002', 'triangle_pose',
        NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days' + INTERVAL '40 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_002', 'bridge_pose',
        NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days' + INTERVAL '30 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_002', 'downward_facing_dog',
        NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '45 minutes');

-- demo user: user_003
INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_003', 'pigeon_pose',
        NOW() - INTERVAL '14 days', NOW() - INTERVAL '14 days' + INTERVAL '60 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_003', 'happy_baby',
        NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days' + INTERVAL '20 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_003', 'supine_twist',
        NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days' + INTERVAL '35 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_003', 'warrior_ii',
        NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days' + INTERVAL '45 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_003', 'lotus',
        NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '30 minutes');

INSERT INTO sessions (user_id, pose_id, started_at, completed_at)
VALUES ('user_003', 'corpse_pose',
        NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '15 minutes');

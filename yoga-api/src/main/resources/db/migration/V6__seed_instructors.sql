-- V6: Seed 10 Seoul instructors for the elbee matching system
--
-- Trust scores are pre-computed using the formula from scripts/scrape_instructors.py:
--   score = cert_weight + avg_rating/5.0*0.3 + min(lineage_depth,4)*0.05
--           + min(log10(ig_followers)/7.0, 0.1)
--   capped at 1.000
--
-- Cert weights: E-RYT-500=1.0, E-RYT-200=0.8, RYT-500=0.6, RYT-200=0.4, YACEP=0.2
-- All ten instructors are affiliated with elbee studio districts from yoga_locations.json.

-- ── Instructors ───────────────────────────────────────────────────────────────

-- 1. Lee Ji-woo  |  E-RYT-500  |  Gangnam  |  trust=1.000
--    1.0 + (4.9/5*0.3=0.294) + (4*0.05=0.200) + min(log10(12400)/7,0.1)=0.1 → 1.594 → cap 1.000
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'lee-ji-woo',
    'Lee Ji-woo',
    'E-RYT-500 Ashtanga and Vinyasa teacher based in Gangnam. 15 years of teaching experience across Seoul, Tokyo, and Bali. Certified under Sri K. Pattabhi Jois lineage (3rd generation).',
    'E-RYT-500', 'YA-00482311', TRUE,
    'Ashtanga', 4,
    'leejiwoo.yoga', 12400, 'https://instagram.com/leejiwoo.yoga',
    4.9, 312, 1.000,
    ARRAY['ashtanga', 'vinyasa', 'back_pain', 'advanced'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 2. Park Sun-young  |  E-RYT-200  |  Seongsu  |  trust=1.000
--    0.8 + (4.8/5*0.3=0.288) + (3*0.05=0.150) + 0.1 → 1.338 → cap 1.000
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'park-sun-young',
    'Park Sun-young',
    'Iyengar-trained E-RYT-200 instructor at the Seongsu elbee studio. Specialises in therapeutic yoga for office workers with spinal and shoulder issues.',
    'E-RYT-200', 'YA-00519873', TRUE,
    'Iyengar', 3,
    'parksunyoung_yoga', 8750, 'https://instagram.com/parksunyoung_yoga',
    4.8, 241, 1.000,
    ARRAY['iyengar', 'therapeutic', 'spinal_mobility', 'shoulder_opening'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 3. Kim Min-jun  |  RYT-500  |  Itaewon  |  trust=1.000
--    0.6 + (4.7/5*0.3=0.282) + (2*0.05=0.100) + 0.1 → 1.082 → cap 1.000
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'kim-min-jun',
    'Kim Min-jun',
    'Bilingual (Korean/English) RYT-500 instructor at the Itaewon elbee Wellness Centre. Vinyasa and Yin Yoga specialist. Trained under the Sivananda and Jivamukti lineages.',
    'RYT-500', 'YA-00601245', FALSE,
    'Jivamukti', 2,
    'minjun.on.mat', 3400, 'https://instagram.com/minjun.on.mat',
    4.7, 188, 1.000,
    ARRAY['vinyasa', 'yin_yoga', 'stress_relief', 'english_ok'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 4. Lim Soo-ah  |  RYT-500  |  Jongno  |  trust=1.000
--    0.6 + (4.6/5*0.3=0.276) + (2*0.05=0.100) + 0.1 → 1.076 → cap 1.000
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'lim-soo-ah',
    'Lim Soo-ah',
    'Restorative and Yin Yoga instructor at the Jongno elbee Meditation Studio. 10 years of practice in traditional Korean mindfulness and Buddhist-influenced yoga. RYT-500.',
    'RYT-500', 'YA-00588012', TRUE,
    'Sivananda', 2,
    'limsooyoga', 5600, 'https://instagram.com/limsooyoga',
    4.6, 156, 1.000,
    ARRAY['yin_yoga', 'restorative', 'meditation', 'beginner_friendly'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 5. Yoon Tae-yang  |  E-RYT-500  |  Gangnam  |  trust=1.000
--    1.0 + (4.9/5*0.3=0.294) + (4*0.05=0.200) + 0.1 → 1.594 → cap 1.000
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'yoon-tae-yang',
    'Yoon Tae-yang',
    'Power Yoga and Hot Yoga director at the Gangnam elbee Premium Studio. E-RYT-500 with 18 years of teaching across Korea and the US. Corporate wellness programme lead.',
    'E-RYT-500', 'YA-00412087', TRUE,
    'Bikram', 4,
    'taeyangpoweryoga', 25300, 'https://instagram.com/taeyangpoweryoga',
    4.9, 407, 1.000,
    ARRAY['power_yoga', 'hot_yoga', 'core_strength', 'corporate_wellness'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 6. Kwon Ji-hoon  |  RYT-500  |  Hongdae  |  trust=1.000
--    0.6 + (4.4/5*0.3=0.264) + (1*0.05=0.050) + 0.1 → 1.014 → cap 1.000
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'kwon-ji-hoon',
    'Kwon Ji-hoon',
    'Outdoor community yoga organiser at Hongdae Community Yoga Park. RYT-500. Leads free weekend sessions and builds beginner-friendly vinyasa sequences for urban practitioners.',
    'RYT-500', 'YA-00634501', FALSE,
    'Anusara', 1,
    'jihoon_outdoor_yoga', 2150, 'https://instagram.com/jihoon_outdoor_yoga',
    4.4, 98, 1.000,
    ARRAY['vinyasa', 'beginner_friendly', 'outdoor', 'community'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 7. Choi Yeon-seo  |  RYT-200  |  Mangwon  |  trust=0.820
--    0.4 + (4.5/5*0.3=0.270) + (1*0.05=0.050) + 0.1 → 0.820
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'choi-yeon-seo',
    'Choi Yeon-seo',
    'Sunset Vinyasa instructor at Mangwon Hangang Park. RYT-200 with a focus on hip flexibility and lower back care. Leads community sessions every Saturday evening from April–October.',
    'RYT-200', 'YA-00712934', FALSE,
    'Vinyasa', 1,
    'yeonseo.yoga.han', 1280, 'https://instagram.com/yeonseo.yoga.han',
    4.5, 74, 0.820,
    ARRAY['vinyasa', 'hip_flexibility', 'back_pain', 'outdoor'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 8. Han Mi-rae  |  RYT-200  |  Bukchon  |  trust=0.808
--    0.4 + (4.3/5*0.3=0.258) + (1*0.05=0.050) + 0.1 → 0.808
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'han-mi-rae',
    'Han Mi-rae',
    'Meditation and breathwork guide at Bukchon Mindfulness Café. RYT-200. Integrates pranayama, yoga nidra, and restorative poses in sessions focused on stress relief and nervous system recovery.',
    'RYT-200', 'YA-00756110', FALSE,
    'Kripalu', 1,
    'mirae.breath.yoga', 920, 'https://instagram.com/mirae.breath.yoga',
    4.3, 61, 0.808,
    ARRAY['meditation', 'breathwork', 'stress_relief', 'restorative'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 9. Jung Ha-eun  |  RYT-200  |  Seongsu  |  trust=0.752
--    0.4 + (4.2/5*0.3=0.252) + (0*0.05=0.000) + 0.1 → 0.752
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'jung-ha-eun',
    'Jung Ha-eun',
    'Morning Flow instructor at the Seongsu elbee Studio. RYT-200 focused on Hatha fundamentals and beginner onboarding. Completed 200-hour training at Yoga Alliance Korea.',
    'RYT-200', 'YA-00798345', TRUE,
    NULL, 0,
    'haeun.morning.yoga', 610, 'https://instagram.com/haeun.morning.yoga',
    4.2, 48, 0.752,
    ARRAY['hatha', 'beginner_friendly', 'morning_flow', 'balance'],
    'Seoul', 'KR',
    'manual', NOW()
);

-- 10. Oh Se-jin  |  YACEP  |  Hangang  |  trust=0.540
--     0.2 + (4.0/5*0.3=0.240) + (0*0.05=0.000) + 0.1 → 0.540
INSERT INTO instructors (
    instructor_id, full_name, bio,
    certification_level, yoga_alliance_id, fyt_certified,
    lineage_school, lineage_depth,
    instagram_handle, instagram_followers, instagram_url,
    avg_rating, review_count, instructor_trust_score,
    specialties, city, country,
    data_source, scraped_at
) VALUES (
    'oh-se-jin',
    'Oh Se-jin',
    'YACEP continuing education provider and part-time outdoor instructor at Hangang Seonyudo Park. Leads weekend sunrise yoga sessions. Currently pursuing RYT-200 full certification.',
    'YACEP', NULL, FALSE,
    NULL, 0,
    'sejin_hangang_yoga', 210, 'https://instagram.com/sejin_hangang_yoga',
    4.0, 29, 0.540,
    ARRAY['outdoor', 'sunrise_yoga', 'beginner_friendly', 'meditation'],
    'Seoul', 'KR',
    'manual', NOW()
);

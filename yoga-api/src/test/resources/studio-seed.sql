-- Seed for StudioControllerIT
-- Three studios: two within 5 km of central Seoul (37.5665, 126.9780), one far away

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Close Studio Alpha', 'Seoul', 'KR', 37.5700, 126.9800);   -- ~0.5 km

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Close Studio Beta',  'Seoul', 'KR', 37.5600, 126.9750);   -- ~1.0 km

INSERT INTO studios (name, city, country, latitude, longitude)
VALUES ('Far Studio Gamma',   'Busan', 'KR', 35.1796, 129.0756);   -- ~326 km

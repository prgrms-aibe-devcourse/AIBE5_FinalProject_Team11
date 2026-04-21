-- Remove OCR artefacts from the poses tables.
-- Artefact patterns:
--   1. canonical_name starts with a digit (numbered book steps)
--   2. pose_id contains 'chakra' (chakra theory text)
--   3. pose_id starts with 'by_' (methodology / sentence fragments)
--   4. canonical_name has more than 8 words (full sentence, not a pose name)
BEGIN;

CREATE TEMP TABLE artefact_ids AS
  SELECT pose_id FROM poses
  WHERE canonical_name ~ '^\d'
     OR pose_id ILIKE '%chakra%'
     OR pose_id LIKE 'by\_%' ESCAPE '\'
     OR (length(canonical_name) - length(replace(canonical_name, ' ', ''))) >= 8;

SELECT COUNT(*) AS artefacts_to_delete FROM artefact_ids;

DELETE FROM pose_focus             WHERE pose_id IN (SELECT pose_id FROM artefact_ids);
DELETE FROM pose_keywords          WHERE pose_id IN (SELECT pose_id FROM artefact_ids);
DELETE FROM pose_benefits          WHERE pose_id IN (SELECT pose_id FROM artefact_ids);
DELETE FROM pose_contraindications WHERE pose_id IN (SELECT pose_id FROM artefact_ids);
DELETE FROM poses                  WHERE pose_id IN (SELECT pose_id FROM artefact_ids);

SELECT COUNT(*) AS poses_remaining FROM poses;

COMMIT;

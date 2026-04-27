-- V7: Add instructor_specialties join table for JPA @ElementCollection mapping
-- This migration creates the table expected by the Instructor entity and migrates
-- any existing specialties array values into the join table.

CREATE TABLE IF NOT EXISTS instructor_specialties (
    instructor_id VARCHAR(255) NOT NULL,
    specialty TEXT NOT NULL,
    PRIMARY KEY (instructor_id, specialty),
    CONSTRAINT fk_instructor_specialties_instructor FOREIGN KEY (instructor_id)
        REFERENCES instructors (instructor_id)
        ON DELETE CASCADE
);

INSERT INTO instructor_specialties (instructor_id, specialty)
SELECT instructor_id, unnest(specialties)
FROM instructors
WHERE specialties IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_instructor_specialties_specialty
    ON instructor_specialties (specialty);

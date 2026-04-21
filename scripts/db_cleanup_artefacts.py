#!/usr/bin/env python3
"""Direct PostgreSQL connection to check and clean artefacts."""
import sys

try:
    import psycopg2
except ImportError:
    print("psycopg2 not available, trying psycopg2-binary...")
    sys.exit(1)

conn = psycopg2.connect(
    host="localhost", port=8879,
    dbname="yogadb", user="postgres", password="postgres"
)
conn.autocommit = False
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM poses;")
before = cur.fetchone()[0]
print(f"Poses before cleanup: {before}")

if before > 1000:
    print("Running artefact cleanup...")
    cur.execute("""
        CREATE TEMP TABLE artefact_ids AS
          SELECT pose_id FROM poses
          WHERE canonical_name ~ '^\\d'
             OR pose_id ILIKE '%chakra%'
             OR pose_id LIKE 'by\\_%' ESCAPE '\\'
             OR (length(canonical_name) - length(replace(canonical_name, ' ', ''))) >= 8;
    """)
    cur.execute("SELECT COUNT(*) FROM artefact_ids;")
    artefact_count = cur.fetchone()[0]
    print(f"Artefacts identified: {artefact_count}")

    cur.execute("DELETE FROM pose_focus             WHERE pose_id IN (SELECT pose_id FROM artefact_ids);")
    cur.execute("DELETE FROM pose_keywords          WHERE pose_id IN (SELECT pose_id FROM artefact_ids);")
    cur.execute("DELETE FROM pose_benefits          WHERE pose_id IN (SELECT pose_id FROM artefact_ids);")
    cur.execute("DELETE FROM pose_contraindications WHERE pose_id IN (SELECT pose_id FROM artefact_ids);")
    cur.execute("DELETE FROM poses                  WHERE pose_id IN (SELECT pose_id FROM artefact_ids);")

    cur.execute("SELECT COUNT(*) FROM poses;")
    after = cur.fetchone()[0]
    print(f"Poses after cleanup: {after}")

    conn.commit()
    print("COMMIT successful.")
else:
    print(f"Cleanup already done or count unexpected: {before}")
    conn.rollback()

cur.close()
conn.close()

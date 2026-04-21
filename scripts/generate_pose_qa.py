#!/usr/bin/env python3
"""
generate_pose_qa.py — AEO/GEO knowledge-base enrichment

What this does
──────────────
1. Applies the V2 DDL (idempotent ALTER / CREATE IF NOT EXISTS) so the script
   can run standalone without waiting for Flyway / Java restart.
2. Reads every *valid* pose from the live yogadb together with its benefits,
   contraindications, and keywords.
3. Generates per-pose:
   • natural_description  — a clean, sentence-form English paragraph.
   • schema_org_jsonld    — Schema.org ExerciseAction JSON-LD.
   • pose_qa rows         — pre-built Q&A for AEO (what_is / benefits /
                            contraindications / body_parts / how_to).
4. Fills pose_focus from benefit tags that map to anatomical regions (the
   pose_focus table has 0 rows in the live DB).

Usage
─────
  cd /home/aiegoo/repos/aiegoo/aeogeo
  python scripts/generate_pose_qa.py [--dry-run] [--limit N]

Options
  --dry-run    Print the first 5 poses worth of data; do not write to DB.
  --limit N    Process only the first N valid poses (for quick tests).

Dependencies: psycopg2  (already used by db_table.py)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras

# ── DB connection ─────────────────────────────────────────────────────────────
DEFAULT_DSN: dict[str, Any] = {
    "host":     "localhost",
    "port":     8879,
    "dbname":   "yogadb",
    "user":     "postgres",
    "password": "postgres",
}

# ── Anatomical-focus tags (benefit tags that are also body-region labels) ─────
ANATOMICAL_TAGS = {
    "Back", "Shoulder", "Hip", "Core", "Knee", "Neck",
    "Wrist", "Hamstring", "Glute", "Chest", "Spine", "Ankle",
    "Abs", "Arms", "Hips", "Legs", "Thighs", "Calves",
}

# Body-part words we can infer from pose canonical_name text
_BODY_PART_WORDS = {
    "back": "Back", "shoulder": "Shoulder", "hip": "Hip", "core": "Core",
    "knee": "Knee", "neck": "Neck", "wrist": "Wrist", "hamstring": "Hamstring",
    "glute": "Glute", "chest": "Chest", "spine": "Spine", "ankle": "Ankle",
    "ab": "Abs", "abs": "Abs", "arm": "Arms", "leg": "Legs",
    "thigh": "Thighs", "calf": "Calves", "calves": "Calves",
    "quad": "Legs", "quad": "Legs",
}

# ── Pose-ID garbage detector ──────────────────────────────────────────────────

def _is_valid_pose(pose_id: str, canonical_name: str) -> bool:
    """Return False for OCR-artifact rows that have no real pose data."""
    # Single or very short OCR artifacts: 'a', 'j', 'bhs,'
    if len(pose_id) <= 3:
        return False
    # Numbered instruction steps: "1. Begin by standing..."
    if re.match(r"^\d+[._\s]", canonical_name or ""):
        return False
    return True


# ── Natural description builder ───────────────────────────────────────────────

def _build_natural_description(
    canonical_name: str,
    benefits: list[dict],
    contraindications: list[dict],
) -> str:
    """Return a clean English sentence usable as an AI-ingestible description."""
    name = canonical_name.strip()

    # Prioritise specific benefit tags over generics
    specific_benefits = [
        b["tag"] for b in benefits if b["tag"] not in ("GeneralWellness",)
    ]
    all_benefits = [b["tag"] for b in benefits]
    focus_tags = specific_benefits or all_benefits

    if focus_tags:
        if len(focus_tags) == 1:
            benefit_phrase = f" known for its positive effects on {focus_tags[0].lower()}"
        elif len(focus_tags) == 2:
            benefit_phrase = (
                f" known for its positive effects on {focus_tags[0].lower()} "
                f"and {focus_tags[1].lower()}"
            )
        else:
            joined = ", ".join(t.lower() for t in focus_tags[:-1])
            benefit_phrase = f" known for its positive effects on {joined}, and {focus_tags[-1].lower()}"
    else:
        benefit_phrase = ""

    desc = f"{name} is a yoga pose{benefit_phrase}."

    if contraindications:
        kill_conds = [c["condition"] for c in contraindications if c.get("kill_switch")]
        caution_conds = [
            c["condition"] for c in contraindications if not c.get("kill_switch")
        ]
        if kill_conds:
            desc += (
                f" Practitioners with {_join_list(kill_conds, lower=True)} "
                "should avoid this pose entirely."
            )
        if caution_conds:
            desc += (
                f" Those with {_join_list(caution_conds, lower=True)} "
                "should practise with caution or consult an instructor."
            )

    return desc


def _join_list(items: list[str], *, lower: bool = False) -> str:
    parts = [x.lower() if lower else x for x in items]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return f"{', '.join(parts[:-1])}, and {parts[-1]}"


# ── Schema.org JSON-LD builder ────────────────────────────────────────────────

def _build_schema_org(
    canonical_name: str,
    natural_description: str,
    benefits: list[dict],
    difficulty_rank: int,
) -> dict:
    level_map = {1: "Beginner", 2: "Beginner", 3: "Intermediate", 4: "Advanced", 5: "Expert"}
    level = level_map.get(difficulty_rank, "Intermediate")

    anatomical = [b["tag"] for b in benefits if b["tag"] in ANATOMICAL_TAGS]

    return {
        "@context": "https://schema.org",
        "@type": "ExerciseAction",
        "name": canonical_name,
        "description": natural_description,
        "exerciseType": "Yoga",
        "educationalLevel": level,
        "actionStatus": "ActiveActionStatus",
        "bodyLocation": anatomical or None,
    }


# ── Q&A pair builder ──────────────────────────────────────────────────────────

def _build_qa_pairs(
    pose_id: str,
    canonical_name: str,
    natural_description: str,
    benefits: list[dict],
    contraindications: list[dict],
) -> list[dict]:
    name = canonical_name.strip()
    pairs: list[dict] = []

    # 1. what_is
    pairs.append({
        "pose_id": pose_id,
        "question": f"What is {name}?",
        "answer": natural_description,
        "question_type": "what_is",
        "language": "en",
    })

    # 2. benefits
    if benefits:
        tags = [b["tag"] for b in benefits]
        tag_list = _join_list(tags)
        pairs.append({
            "pose_id": pose_id,
            "question": f"What are the benefits of {name}?",
            "answer": (
                f"Regular practice of {name} can benefit: {tag_list}. "
                "It is suitable for students looking to improve overall wellness."
            ),
            "question_type": "benefits",
            "language": "en",
        })

    # 3. contraindications
    if contraindications:
        kill = [c["condition"] for c in contraindications if c.get("kill_switch")]
        caution = [c["condition"] for c in contraindications if not c.get("kill_switch")]

        parts: list[str] = []
        if kill:
            parts.append(
                f"Do not practise {name} if you have {_join_list(kill, lower=True)}."
            )
        if caution:
            parts.append(
                f"Use caution or seek guidance if you have "
                f"{_join_list(caution, lower=True)}."
            )
        parts.append("Always consult a qualified yoga instructor when in doubt.")

        pairs.append({
            "pose_id": pose_id,
            "question": f"Who should avoid {name}?",
            "answer": " ".join(parts),
            "question_type": "contraindications",
            "language": "en",
        })

    # 4. body_parts
    anatomical = [b["tag"] for b in benefits if b["tag"] in ANATOMICAL_TAGS]
    if anatomical:
        pairs.append({
            "pose_id": pose_id,
            "question": f"What body parts does {name} target?",
            "answer": (
                f"{name} primarily works the following body regions: "
                f"{_join_list(anatomical)}."
            ),
            "question_type": "body_parts",
            "language": "en",
        })

    # 5. how_to (generic if no clean aeo_summary; the instruction step poses are
    #    filtered out already by _is_valid_pose, so remaining poses get this)
    pairs.append({
        "pose_id": pose_id,
        "question": f"How do you do {name}?",
        "answer": (
            f"To practise {name}, begin in a comfortable starting position. "
            "Move mindfully into the pose, keeping the breath steady and even. "
            "Hold for 5–10 breaths, then release with control. "
            "Consult a certified yoga instructor for detailed alignment cues."
        ),
        "question_type": "how_to",
        "language": "en",
    })

    return pairs


# ── Anatomical focus inference ────────────────────────────────────────────────

def _infer_focus(
    canonical_name: str,
    benefits: list[dict],
) -> list[str]:
    focus: set[str] = set()

    # Primary: benefit tags that map to anatomical regions
    for b in benefits:
        if b["tag"] in ANATOMICAL_TAGS:
            focus.add(b["tag"])

    # Secondary: word-match in canonical name
    name_lower = canonical_name.lower()
    for word, region in _BODY_PART_WORDS.items():
        if word in name_lower:
            focus.add(region)

    return sorted(focus)


# ── DDL (V2 migration, idempotent) ────────────────────────────────────────────

V2_DDL = """
ALTER TABLE poses ADD COLUMN IF NOT EXISTS natural_description TEXT;
ALTER TABLE poses ADD COLUMN IF NOT EXISTS schema_org_jsonld JSONB;

CREATE TABLE IF NOT EXISTS pose_qa (
    id              BIGSERIAL    PRIMARY KEY,
    pose_id         VARCHAR(255) NOT NULL,
    question        TEXT         NOT NULL,
    answer          TEXT         NOT NULL,
    question_type   VARCHAR(50)  NOT NULL,
    language        VARCHAR(10)  NOT NULL DEFAULT 'en',
    CONSTRAINT fk_pose_qa_pose
        FOREIGN KEY (pose_id) REFERENCES poses (pose_id)
);

CREATE INDEX IF NOT EXISTS idx_pose_qa_pose_id       ON pose_qa (pose_id);
CREATE INDEX IF NOT EXISTS idx_pose_qa_question_type ON pose_qa (question_type);
CREATE INDEX IF NOT EXISTS idx_pose_qa_language      ON pose_qa (language);
"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate AEO/GEO Q&A enrichment for yogadb."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print data for the first 5 valid poses; do not write to DB.",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Process only the first N valid poses (0 = all).",
    )
    args = parser.parse_args()

    conn = psycopg2.connect(**DEFAULT_DSN)
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # ── Apply V2 DDL ────────────────────────────────────────────────────────
    if not args.dry_run:
        print("Applying V2 DDL (idempotent)…")
        cur.execute(V2_DDL)
        conn.commit()
        print("  ✓ Schema updated.")

    # ── Load poses ──────────────────────────────────────────────────────────
    print("Loading poses from yogadb…")
    cur.execute(
        """
        SELECT pose_id, canonical_name, common_name, difficulty_rank
        FROM   poses
        ORDER  BY pose_id
        """
    )
    all_poses = cur.fetchall()
    print(f"  Total rows in poses: {len(all_poses)}")

    valid_poses = [
        p for p in all_poses
        if _is_valid_pose(p["pose_id"], p["canonical_name"] or "")
    ]
    print(f"  Valid (non-OCR-artifact) poses: {len(valid_poses)}")

    if args.limit:
        valid_poses = valid_poses[: args.limit]
        print(f"  (Limited to first {args.limit} for this run)")

    # ── Pre-load related tables into dicts for fast lookup ──────────────────
    print("Loading benefits, contraindications…")

    cur.execute("SELECT pose_id, tag, weight FROM pose_benefits")
    benefits_map: dict[str, list[dict]] = {}
    for row in cur.fetchall():
        benefits_map.setdefault(row["pose_id"], []).append(
            {"tag": row["tag"], "weight": float(row["weight"] or 0)}
        )

    cur.execute(
        "SELECT pose_id, condition, severity, kill_switch, instruction "
        "FROM   pose_contraindications"
    )
    contra_map: dict[str, list[dict]] = {}
    for row in cur.fetchall():
        contra_map.setdefault(row["pose_id"], []).append({
            "condition":   row["condition"],
            "severity":    row["severity"],
            "kill_switch": bool(row["kill_switch"]),
            "instruction": row["instruction"],
        })

    # Check which pose_ids already have focus rows so we don't double-insert
    cur.execute("SELECT DISTINCT pose_id FROM pose_focus")
    has_focus: set[str] = {r["pose_id"] for r in cur.fetchall()}

    # Check which pose_ids already have qa rows
    cur.execute("SELECT DISTINCT pose_id FROM pose_qa") if not args.dry_run else None
    has_qa: set[str] = set()
    if not args.dry_run:
        cur.execute("SELECT DISTINCT pose_id FROM pose_qa")
        has_qa = {r["pose_id"] for r in cur.fetchall()}

    # ── Process ─────────────────────────────────────────────────────────────
    total_qa = 0
    total_focus = 0
    total_desc = 0

    print(f"\nGenerating enrichments for {len(valid_poses)} poses…")

    for i, pose in enumerate(valid_poses, 1):
        pid        = pose["pose_id"]
        cname      = pose["canonical_name"] or ""
        difficulty = int(pose["difficulty_rank"] or 3)

        benefits       = benefits_map.get(pid, [])
        contraindications = contra_map.get(pid, [])

        natural_desc = _build_natural_description(cname, benefits, contraindications)
        schema_org   = _build_schema_org(cname, natural_desc, benefits, difficulty)
        qa_pairs     = _build_qa_pairs(pid, cname, natural_desc, benefits, contraindications)
        focus_areas  = _infer_focus(cname, benefits)

        if args.dry_run:
            if i <= 5:
                print(f"\n{'─'*70}")
                print(f"pose_id: {pid}")
                print(f"canonical_name: {cname}")
                print(f"natural_description:\n  {natural_desc}")
                print(f"schema_org: {json.dumps(schema_org, indent=2)}")
                print(f"focus_areas: {focus_areas}")
                print(f"Q&A pairs ({len(qa_pairs)}):")
                for qa in qa_pairs:
                    print(f"  [{qa['question_type']}] Q: {qa['question']}")
                    print(f"        A: {qa['answer'][:120]}…")
            elif i == 6:
                print("\n(dry-run: showing only first 5 poses)")
            continue

        # ── UPDATE poses ────────────────────────────────────────────────────
        cur.execute(
            """
            UPDATE poses
            SET    natural_description = %s,
                   schema_org_jsonld   = %s::jsonb
            WHERE  pose_id = %s
              AND  (natural_description IS NULL OR natural_description = '')
            """,
            (natural_desc, json.dumps(schema_org, ensure_ascii=False), pid),
        )
        if cur.rowcount:
            total_desc += 1

        # ── INSERT pose_focus (skip if already present for this pose) ────────
        if pid not in has_focus and focus_areas:
            psycopg2.extras.execute_values(
                cur,
                "INSERT INTO pose_focus (pose_id, focus) VALUES %s",
                [(pid, f) for f in focus_areas],
            )
            total_focus += len(focus_areas)
            has_focus.add(pid)

        # ── INSERT pose_qa (idempotent: skip if already exists) ─────────────
        if pid not in has_qa:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO pose_qa (pose_id, question, answer, question_type, language)
                VALUES %s
                """,
                [
                    (qa["pose_id"], qa["question"], qa["answer"],
                     qa["question_type"], qa["language"])
                    for qa in qa_pairs
                ],
            )
            total_qa += len(qa_pairs)
            has_qa.add(pid)

        # Commit every 100 poses to keep transactions small
        if i % 100 == 0:
            conn.commit()
            print(f"  …{i}/{len(valid_poses)} processed")

    if not args.dry_run:
        conn.commit()
        print(f"\n{'═'*50}")
        print(f"Done.")
        print(f"  natural_description updated : {total_desc}")
        print(f"  pose_focus rows inserted    : {total_focus}")
        print(f"  pose_qa rows inserted       : {total_qa}")

    cur.close()
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

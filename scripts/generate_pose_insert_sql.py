#!/usr/bin/env python3
"""
Generate SQL insert statements from the enriched pose JSON.

This script reads `data/poses/poses_eat_schema.json` and emits SQL for the
`yoga-api` schema in `src/main/resources/db/migration`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/poses/poses_eat_schema.json")
DEFAULT_OUTPUT = Path("data/poses/pose_enriched_ingest.sql")


def sql_escape(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def insert_row(table: str, columns: list[str], values: list[str]) -> str:
    return f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});"


def load_input(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Expected top-level JSON array")
    return data


def is_artefact(pose: dict[str, Any]) -> bool:
    """Return True for OCR artefacts that are not real yoga poses.

    Detected patterns:
    - canonical_name starts with a digit (numbered book steps)
    - pose_id contains 'chakra' (chakra theory text)
    - pose_id starts with 'by_' (methodology / sentence fragments)
    - canonical_name has more than 8 words (full sentence, not a pose name)
    """
    pose_id = normalize_text(pose.get("pose_id"))
    canonical_name = normalize_text(pose.get("canonical_name"))
    if canonical_name and canonical_name[0].isdigit():
        return True
    if "chakra" in pose_id.lower():
        return True
    if pose_id.startswith("by_"):
        return True
    if len(canonical_name.split()) > 8:
        return True
    return False


def build_inserts(poses: list[dict[str, Any]]) -> tuple[list[str], int]:
    sql_lines: list[str] = []
    skipped = 0
    seen_ids: set[str] = set()
    for pose in poses:
        if is_artefact(pose):
            skipped += 1
            continue
        pose_id = normalize_text(pose.get("pose_id"))
        if not pose_id:
            skipped += 1
            continue
        if pose_id in seen_ids:
            skipped += 1
            continue
        seen_ids.add(pose_id)
        canonical_name = normalize_text(pose.get("canonical_name"))
        common_name = normalize_text(pose.get("common_name"))
        difficulty_rank = int(pose.get("difficulty_rank") or 0)

        edu = pose.get("educational_metadata", {}) or {}
        instructor_cue_priority = normalize_text(edu.get("instructor_cue_priority"))
        lineage_source = normalize_text(edu.get("lineage_source"))
        fyt100_ref = normalize_text(edu.get("fyt100_session_ref"))
        aeo_summary = normalize_text(edu.get("aeo_summary"))

        sql_lines.append(insert_row(
            "poses",
            ["pose_id", "canonical_name", "common_name", "difficulty_rank", "instructor_cue_priority", "lineage_source", "fyt100_session_ref", "aeo_summary"],
            [sql_escape(pose_id), sql_escape(canonical_name), sql_escape(common_name), str(difficulty_rank), sql_escape(instructor_cue_priority), sql_escape(lineage_source), sql_escape(fyt100_ref), sql_escape(aeo_summary)],
        ))

        for focus in pose.get("anatomical_focus", []):
            focus_text = normalize_text(focus)
            if focus_text:
                sql_lines.append(insert_row(
                    "pose_focus",
                    ["pose_id", "focus"],
                    [sql_escape(pose_id), sql_escape(focus_text)],
                ))

        for keyword in pose.get("geo_keywords", []):
            keyword_text = normalize_text(keyword)
            if keyword_text:
                sql_lines.append(insert_row(
                    "pose_keywords",
                    ["pose_id", "keyword"],
                    [sql_escape(pose_id), sql_escape(keyword_text)],
                ))

        for benefit in pose.get("matching_logic", {}).get("benefits", []):
            tag = normalize_text(benefit.get("tag"))
            weight = float(benefit.get("weight") or 0.0)
            if tag:
                sql_lines.append(insert_row(
                    "pose_benefits",
                    ["pose_id", "tag", "weight"],
                    [sql_escape(pose_id), sql_escape(tag), str(weight)],
                ))

        for contraindication in pose.get("matching_logic", {}).get("contraindications", []):
            condition = normalize_text(contraindication.get("condition"))
            severity = normalize_text(contraindication.get("severity"))
            kill_switch = bool(contraindication.get("kill_switch"))
            instruction = normalize_text(contraindication.get("instruction"))
            if condition:
                sql_lines.append(insert_row(
                    "pose_contraindications",
                    ["pose_id", "condition", "severity", "kill_switch", "instruction"],
                    [sql_escape(pose_id), sql_escape(condition), sql_escape(severity), 'TRUE' if kill_switch else 'FALSE', sql_escape(instruction)],
                ))

    return sql_lines, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SQL insert statements from enriched pose JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Enriched pose JSON input file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="SQL output file")
    args = parser.parse_args()

    try:
        poses = load_input(args.input)
    except Exception as exc:
        print(exc)
        return 1

    sql_lines, skipped = build_inserts(poses)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(sql_lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(sql_lines)} SQL statements to {args.output}")
    print(f"Pose rows (clean): {len(poses) - skipped}  Skipped (artefacts): {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

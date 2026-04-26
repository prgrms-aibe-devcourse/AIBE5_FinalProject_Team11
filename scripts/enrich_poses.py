#!/usr/bin/env python3
"""
Enrich pose source data into an E-E-A-T oriented schema for yoga matching.

This script is intentionally generic: it can consume an existing JSON pose source
and output a normalized, enriched version suitable for the first phase of the
matching system.

Usage:
  python3 scripts/enrich_poses.py --input ../yoga/references/2700-asanas/json/poses_database.json \
      --output data/poses/poses_eat_schema.json

By default, this script reads pose source data from the sibling `yoga` repository.
The `yoga` files are treated as external read-only inputs; this script does not
attempt to modify anything in that repository.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
YOGA_REPO = REPO_ROOT.parent / "yoga"
DEFAULT_INPUT = YOGA_REPO / "references" / "2700-asanas" / "json" / "poses_database.json"
DEFAULT_OUTPUT = Path("data/poses/poses_eat_schema.json")

# Minimal fallback keywords for geo search and pose discovery.
BENEFIT_KEYWORDS = [
    "flexibility",
    "mobility",
    "strength",
    "balance",
    "stability",
    "relief",
    "release",
    "posture",
    "core",
    "stress",
    "back",
    "hip",
    "shoulder",
    "neck",
]

CONTRAINDICATION_KEYWORDS = [
    "injury",
    "pain",
    "disc",
    "back",
    "knee",
    "wrist",
    "neck",
    "pregnancy",
    "hypertension",
    "glaucoma",
    "shoulder",
    "sciatica",
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def unique_slug(base: str, seen: set[str]) -> str:
    if not base:
        base = "pose"
    slug = slugify(base)
    if not slug:
        slug = "pose"
    candidate = slug
    suffix = 1
    while candidate in seen:
        suffix += 1
        candidate = f"{slug}_{suffix}"
    seen.add(candidate)
    return candidate


def choose_text(raw: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def infer_difficulty(raw: dict[str, Any]) -> int:
    difficulty = raw.get("difficulty_rank") or raw.get("difficulty") or raw.get("level")
    if isinstance(difficulty, str) and difficulty.isdigit():
        return max(1, min(5, int(difficulty)))
    if isinstance(difficulty, (int, float)):
        return max(1, min(5, int(difficulty)))
    if isinstance(difficulty, str):
        mapping = {
            "beginner": 1,
            "intro": 1,
            "easy": 1,
            "intermediate": 3,
            "medium": 3,
            "advanced": 5,
            "expert": 5,
        }
        return mapping.get(difficulty.lower(), 3)
    return 3


def infer_anatomical_focus(raw: dict[str, Any]) -> list[str]:
    focus = []
    for key in ("anatomy", "body_parts", "anatomical_focus", "focus", "muscles", "targets"):
        value = raw.get(key)
        if isinstance(value, str):
            focus.extend([p.strip().title() for p in re.split(r"[,;/]", value) if p.strip()])
        elif isinstance(value, list):
            focus.extend([str(p).strip().title() for p in value if str(p).strip()])
    return sorted(set(focus))


def infer_benefits(raw: dict[str, Any]) -> list[dict[str, Any]]:
    benefits = []
    description = choose_text(raw, ["benefits", "effects", "highlights", "tags", "description"])
    text = description.lower()
    for tag in BENEFIT_KEYWORDS:
        if tag in text and not any(b["tag"] == tag for b in benefits):
            benefits.append({"tag": tag.replace(" ", "_").title(), "weight": 0.6})
    if not benefits:
        benefits.append({"tag": "GeneralWellness", "weight": 0.5})
    return benefits


def infer_contraindications(raw: dict[str, Any]) -> list[dict[str, Any]]:
    contraindications = []
    notes = choose_text(raw, ["contraindications", "cautions", "warnings", "avoid", "modification", "notes"])
    text = notes.lower()
    for keyword in CONTRAINDICATION_KEYWORDS:
        if keyword in text and not any(c["condition"] == keyword.upper() for c in contraindications):
            contraindications.append({
                "condition": keyword.upper(),
                "severity": "CRITICAL" if keyword in ("injury", "disc", "pregnancy", "glaucoma") else "CAUTION",
                "kill_switch": keyword in ("injury", "disc", "pregnancy", "glaucoma"),
                "instruction": f"Careful with {keyword}. Modify or avoid this pose as needed.",
            })
    return contraindications


def infer_geo_keywords(raw: dict[str, Any], canonical: str, common: str) -> list[str]:
    keywords = set()
    keywords.add(canonical)
    if common and common != canonical:
        keywords.add(common)
    for key in ("alt_name", "alias", "sanskrit", "english_name", "also_known_as", "pose_type", "name"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip() and value.strip() not in keywords:
            keywords.add(value.strip())
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    keywords.add(item.strip())
    if raw.get("lineage"):
        keywords.add(str(raw["lineage"]).strip())
    return sorted(keywords)


def is_pose_entry(raw: dict[str, Any]) -> bool:
    marker_keys = ["pose_image", "pose_type", "drishti_point", "also_known_as", "sanskrit"]
    return any(raw.get(key) for key in marker_keys)


def build_schema_org(raw: dict[str, Any], canonical: str, common: str, summary: str) -> dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to Do {common or canonical}",
        "description": summary or f"Step-by-step guide for {common or canonical}.",
        "educationalLevel": "Beginner to Intermediate",
        "teaches": infer_anatomical_focus(raw),
    }


def build_pose_item(raw: dict[str, Any], seen_ids: set[str]) -> dict[str, Any]:
    canonical = choose_text(raw, ["canonical_name", "name", "english_name", "common_name"]) or "Unknown Pose"
    common = choose_text(raw, ["common_name", "name", "english_name", "canonical_name"]) or canonical
    pose_id = unique_slug(raw.get("pose_id") or canonical, seen_ids)
    summary = choose_text(raw, ["summary", "description", "instructions", "overview"])

    item = {
        "pose_id": pose_id,
        "canonical_name": canonical,
        "common_name": common,
        "difficulty_rank": infer_difficulty(raw),
        "anatomical_focus": infer_anatomical_focus(raw),
        "educational_metadata": {
            "instructor_cue_priority": choose_text(raw, ["cue", "que", "teaching_note", "instruction"]),
            "lineage_source": choose_text(raw, ["lineage", "source", "tradition", "style"]),
            "fyt100_session_ref": choose_text(raw, ["session_ref", "fyt100_ref", "fyt100_session"]),
            "aeo_summary": summary,
        },
        "matching_logic": {
            "benefits": infer_benefits(raw),
            "contraindications": infer_contraindications(raw),
        },
        "geo_keywords": infer_geo_keywords(raw, canonical, common),
    }
    item["schema_org"] = build_schema_org(raw, canonical, common, summary)
    return item


def load_source(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "poses" in data and isinstance(data["poses"], list):
            return data["poses"]
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("Unsupported input JSON structure: top-level must be object or array")


def write_output(items: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an E-E-A-T enriched pose schema from source JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input JSON pose source path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output enriched pose JSON path")
    parser.add_argument("--preview", action="store_true", help="Print the first enriched pose and exit")
    args = parser.parse_args()

    try:
        source = load_source(args.input)
    except FileNotFoundError as exc:
        print(exc)
        print("No input file found. Provide --input to run against a local pose JSON source.")
        return 1
    except ValueError as exc:
        print(exc)
        return 1

    pose_entries = [item for item in source if is_pose_entry(item)]
    dropped = len(source) - len(pose_entries)
    print(f"Loaded {len(source)} source entries; keeping {len(pose_entries)} pose entries, dropping {dropped} non-pose entries.")

    seen_ids: set[str] = set()
    enriched = [build_pose_item(raw, seen_ids) for raw in pose_entries]

    if args.preview:
        print(json.dumps(enriched[0] if enriched else {}, ensure_ascii=False, indent=2))
        return 0

    write_output(enriched, args.output)
    print(f"Wrote {len(enriched)} enriched poses to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

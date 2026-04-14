#!/usr/bin/env python3
"""
geo/scripts/adapt_content.py
────────────────────────────────────────────────────────
Post-process raw OCR output → clean, topic-tagged Markdown
with Jekyll frontmatter, ready for yoga-chatbot content/.

Usage
─────
  python3 scripts/adapt_content.py --book "Light on Yoga"
  python3 scripts/adapt_content.py --book "Light on Yoga" --min-words 30

Output
──────
  content/<book-slug>/page_NNNN.md   Jekyll Markdown with frontmatter
  ocr/processed/<book-slug>/         cleaned plain-text copies
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "json"
CONTENT_DIR = ROOT / "content"
PROCESSED_DIR = ROOT / "ocr" / "processed"

# ── Topic tagger ───────────────────────────────────────────────────────────────

TOPIC_KEYWORDS = {
    "asana":       ["asana", "pose", "posture", "position", "stand", "sit", "lie", "balance"],
    "pranayama":   ["breath", "breathe", "pranayama", "inhale", "exhale", "nostril", "kumbhaka"],
    "anatomy":     ["muscle", "spine", "hip", "shoulder", "knee", "joint", "ligament", "nerve",
                    "vertebra", "pelvis", "femur", "hamstring", "quadricep"],
    "philosophy":  ["dharma", "karma", "yoga sutra", "patanjali", "chakra", "prana", "nadi",
                    "samadhi", "moksha", "ahimsa", "consciousness"],
    "sequence":    ["series", "sequence", "flow", "vinyasa", "primary", "secondary", "ashtanga",
                    "surya", "sun salutation"],
    "mudra":       ["mudra", "bandha", "mula", "uddiyana", "jalandhara", "gesture", "lock"],
    "meditation":  ["meditation", "dhyana", "focus", "concentration", "mantra", "trataka"],
}


def tag_topics(text: str) -> list[str]:
    lower = text.lower()
    tags = [topic for topic, kws in TOPIC_KEYWORDS.items() if any(kw in lower for kw in kws)]
    return tags or ["general"]


def detect_heading(text: str) -> str:
    """Pull the first short line as a title candidate."""
    for line in text.splitlines():
        line = line.strip()
        if 4 <= len(line) <= 80 and not line[0].isdigit():
            return line
    return ""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ── Markdown builder ───────────────────────────────────────────────────────────

def build_markdown(page: dict, book_title: str, book_slug: str) -> str:
    text = page["text"]
    page_num = page["page_number"]
    heading = detect_heading(text) or f"Page {page_num}"
    topics = tag_topics(text)

    # Frontmatter
    fm_tags = "\n".join(f'  - "{t}"' for t in topics)
    fm = f"""---
title: "{heading.replace('"', "'")}"
layout: single
permalink: /geo/{book_slug}/page-{page_num:04d}/
book: "{book_title}"
book_slug: "{book_slug}"
page: {page_num}
tags:
{fm_tags}
category: books
source: geo-ocr
brand: elbee.yogaman.club
date: {date.today().isoformat()}
toc: false
---
"""

    # Body — promote first short line to h2, rest as paragraphs
    lines = text.splitlines()
    body_parts = []
    first = True
    for line in lines:
        line = line.rstrip()
        if not line:
            body_parts.append("")
            continue
        if first and line.strip() == heading:
            body_parts.append(f"## {line.strip()}")
            first = False
        else:
            body_parts.append(line)
            first = False

    body = "\n".join(body_parts).strip()
    return fm + "\n" + body + "\n"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Adapt OCR output to Jekyll Markdown")
    parser.add_argument("--book", required=True, help="Book title (must match ocr_pipeline run)")
    parser.add_argument("--min-words", type=int, default=20,
                        help="Skip pages with fewer words (default 20)")
    args = parser.parse_args()

    slug = slugify(args.book)
    db_path = DATA_DIR / slug / "ocr_database.json"
    if not db_path.exists():
        sys.exit(f"[ERROR] No OCR data found at {db_path}\nRun ocr_pipeline.py first.")

    db = json.loads(db_path.read_text(encoding="utf-8"))
    pages = db["pages"]
    book_title = db["metadata"]["source_file"]

    out_content = CONTENT_DIR / slug
    out_content.mkdir(parents=True, exist_ok=True)

    out_processed = PROCESSED_DIR / slug
    out_processed.mkdir(parents=True, exist_ok=True)

    skipped = 0
    written = 0
    for page in pages:
        if page.get("word_count", len(page["text"].split())) < args.min_words:
            skipped += 1
            continue

        md = build_markdown(page, book_title, slug)
        out_md = out_content / f"page_{page['page_number']:04d}.md"
        out_md.write_text(md, encoding="utf-8")

        # Plain-text copy for diff/audit
        (out_processed / f"page_{page['page_number']:04d}.txt").write_text(
            page["text"], encoding="utf-8"
        )
        written += 1

    print(f"\n✅ Content adaptation done")
    print(f"   Book    : {book_title}")
    print(f"   Written : {written} pages → content/{slug}/")
    print(f"   Skipped : {skipped} (< {args.min_words} words)")
    print(f"\n   Next: python3 scripts/integrate.py --book \"{args.book}\"")


if __name__ == "__main__":
    main()

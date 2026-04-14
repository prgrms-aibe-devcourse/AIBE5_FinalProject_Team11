#!/usr/bin/env python3
"""
geo/scripts/integrate.py
────────────────────────────────────────────────────────
Sync a processed book from geo/ into the yoga-chatbot project
so it becomes searchable via /yoga/search and /yoga/chat.

What it does
────────────
1. Copies data/json/<slug>/ocr_database.json
   → yoga-chatbot/references/<slug>/json/ocr_database.json
      (same location as existing books, e.g. asana-pranayama-mudra-and-bandha)

2. Copies content/<slug>/*.md
   → yoga-chatbot/references/<slug>/pages/*.md

3. Appends a "books" chip entry to yoga-chatbot search.md if not already there

4. Prints a reminder to rebuild the search index

Usage
─────
  python3 scripts/integrate.py --book "Light on Yoga"
  python3 scripts/integrate.py --book "Light on Yoga" --chatbot /path/to/yoga-chatbot
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_CHATBOT = Path.home() / "repos" / "aiegoo" / "yoga-chatbot"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def main():
    parser = argparse.ArgumentParser(description="Integrate geo book into yoga-chatbot")
    parser.add_argument("--book", required=True, help="Book title")
    parser.add_argument("--chatbot", default=str(DEFAULT_CHATBOT),
                        help="Path to yoga-chatbot repo root")
    args = parser.parse_args()

    slug = slugify(args.book)
    chatbot = Path(args.chatbot)

    if not chatbot.exists():
        sys.exit(f"[ERROR] yoga-chatbot not found at {chatbot}")

    # ── 1. Copy JSON data ──────────────────────────────────────────────────
    src_json_dir = ROOT / "data" / "json" / slug
    dst_json_dir = chatbot / "references" / slug / "json"
    dst_json_dir.mkdir(parents=True, exist_ok=True)

    for json_file in src_json_dir.glob("*.json"):
        shutil.copy2(json_file, dst_json_dir / json_file.name)
        print(f"  📄 Copied {json_file.name} → references/{slug}/json/")

    # ── 2. Copy adapted Markdown ───────────────────────────────────────────
    src_content = ROOT / "content" / slug
    if src_content.exists():
        dst_pages = chatbot / "references" / slug / "pages"
        dst_pages.mkdir(parents=True, exist_ok=True)
        md_files = list(src_content.glob("*.md"))
        for md in md_files:
            shutil.copy2(md, dst_pages / md.name)
        print(f"  📚 Copied {len(md_files)} Markdown pages → references/{slug}/pages/")

    # ── 3. Register in _config.yml include list ────────────────────────────
    config = chatbot / "_config.yml"
    if config.exists():
        cfg_text = config.read_text(encoding="utf-8")
        include_entry = f"  - references/{slug}/pages"
        if include_entry not in cfg_text:
            # Insert after last "  - " in include block
            cfg_text = cfg_text.replace(
                "  - assets/poses",
                f"  - assets/poses\n{include_entry}"
            )
            config.write_text(cfg_text, encoding="utf-8")
            print(f"  ⚙️  Added references/{slug}/pages to _config.yml includes")
        else:
            print(f"  ✅ _config.yml already includes references/{slug}/pages")

    # ── 4. Print next steps ────────────────────────────────────────────────
    print(f"\n✅ Integration done — '{args.book}' is now in yoga-chatbot")
    print(f"""
   Next steps:
   ① Add a search chip in yoga-chatbot/_pages/search.md:
       <span class="chip" data-category="{slug}">{args.book}</span>

   ② If the chat backend uses a books manifest, add:
       {{ "slug": "{slug}", "title": "{args.book}", "brand": "elbee.yogaman.club" }}

   ③ Rebuild the site:
       cd {chatbot} && bundle exec jekyll build

   ④ Commit and push geo/:
       cd {ROOT} && git add data/ content/ && git commit -m "add: {args.book} OCR"
       git push origin main
""")


if __name__ == "__main__":
    main()

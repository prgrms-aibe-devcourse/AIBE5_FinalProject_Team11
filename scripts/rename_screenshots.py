#!/usr/bin/env python3
"""
geo/scripts/rename_screenshots.py
────────────────────────────────────────────────────────
Rename timestamp-based screenshot files to zero-padded
sequential names so OCR processes them in correct book order.

  Before: screenshot_2026_04_15T03_41_23+0900.png
  After:  page_001.png

Usage
─────
  # Dry-run (shows what would be renamed, makes no changes)
  python3 scripts/rename_screenshots.py --dry-run

  # Execute rename
  python3 scripts/rename_screenshots.py

  # Rename into a named subfolder (recommended for multi-book projects)
  python3 scripts/rename_screenshots.py --book "Light on Yoga"
  # → screenshots/light-on-yoga/page_001.png …

Notes
─────
- Sort order is by filename (timestamps sort chronologically when zero-padded)
- Already-renamed files (page_NNN.*) are skipped
- Original files are renamed in-place (no copy)
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCREENSHOTS = ROOT / "screenshots"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif"}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def gather_images(folder: Path) -> list[Path]:
    """Return image files sorted by name, skipping already-named pages."""
    files = sorted(
        p for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTS
        and not re.match(r"^page_\d+", p.name)   # skip already renamed
    )
    return files


def main():
    parser = argparse.ArgumentParser(description="Rename screenshots to page_NNN.ext")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview renames without making changes")
    parser.add_argument("--book", default="",
                        help="If set, rename into screenshots/<book-slug>/ subfolder")
    parser.add_argument("--start", type=int, default=1,
                        help="Starting page number (useful when appending to existing set)")
    args = parser.parse_args()

    if args.book:
        slug = slugify(args.book)
        target_dir = SCREENSHOTS / slug
    else:
        target_dir = SCREENSHOTS

    target_dir.mkdir(parents=True, exist_ok=True)

    # If --book, look for unnested files in screenshots/ root to move+rename
    if args.book:
        source_dir = SCREENSHOTS
    else:
        source_dir = SCREENSHOTS

    files = gather_images(source_dir)

    if not files:
        print(f"[INFO] No unprocessed images found in {source_dir}")
        print("       (Files matching page_NNN.* are already renamed and skipped)")
        sys.exit(0)

    print(f"\n📋 Rename plan — {len(files)} files")
    if args.dry_run:
        print("   [DRY RUN — no changes made]\n")

    pad = max(3, len(str(len(files) + args.start - 1)))  # at least 3 digits

    renamed = 0
    for i, src in enumerate(files, start=args.start):
        dest_name = f"page_{i:0{pad}d}{src.suffix.lower()}"
        dest = target_dir / dest_name

        print(f"  {src.name:<60} → {dest.relative_to(ROOT)}")
        if not args.dry_run:
            src.rename(dest)
            renamed += 1

    if args.dry_run:
        print(f"\n[DRY RUN] Would rename {len(files)} files. Re-run without --dry-run to apply.")
    else:
        print(f"\n✅ Renamed {renamed} files → {target_dir.relative_to(ROOT)}/")
        if args.book:
            print(f"\n   Next: python3 ocr_pipeline.py --book \"{args.book}\"")
        else:
            print(f"\n   Next: python3 ocr_pipeline.py --book \"<title>\"")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
geo/ocr_pipeline.py
────────────────────────────────────────────────────────
Batch-OCR book screenshots → structured JSON + raw text.

Usage
─────
  # Process all new images in screenshots/
  python3 ocr_pipeline.py

  # Process a single file
  python3 ocr_pipeline.py --file screenshots/page_001.jpg

  # Set book title (persisted in metadata)
  python3 ocr_pipeline.py --book "Light on Yoga"

Output
──────
  ocr/raw/<book_slug>/page_NNNN.txt       raw tesseract output
  data/json/<book_slug>/ocr_database.json  matches yoga-chatbot schema
  data/json/<book_slug>/page_index.json    page → text quick-lookup
  data/json/<book_slug>/keyword_index.json word → [page_numbers] inverted index

Drop screenshots (jpg/png/webp/tiff) into screenshots/ and run.
Pages are sorted by filename, so name files page_001.jpg … page_NNN.jpg
or any zero-padded numeric prefix.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
except ImportError as e:
    sys.exit(f"[ERROR] Missing dependency: {e}\nRun: pip install pytesseract Pillow opencv-python")

TESSERACT_CMD = os.environ.get("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
elif sys.platform == "win32":
    default_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if Path(default_tesseract).exists():
        pytesseract.pytesseract.tesseract_cmd = default_tesseract

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
SCREENSHOTS = ROOT / "screenshots"
RAW_DIR = ROOT / "ocr" / "raw"
DATA_DIR = ROOT / "data" / "json"

# ── Tesseract config ───────────────────────────────────────────────────────────
TESS_CONFIG = "--oem 3 --psm 6"   # OEM 3 = LSTM, PSM 6 = block of text


# ── Image pre-processing ───────────────────────────────────────────────────────

def preprocess(img_path: Path) -> "Image.Image":
    """Deskew, denoise and binarise for best OCR accuracy."""
    img = cv2.imread(str(img_path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Upscale small images (< 1500px wide) to help Tesseract
    h, w = gray.shape
    if w < 1500:
        scale = 1500 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Adaptive threshold → clean binary
    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )

    # Light denoise
    denoised = cv2.fastNlMeansDenoising(binary, h=10)
    return Image.fromarray(denoised)


# ── OCR ────────────────────────────────────────────────────────────────────────

def ocr_image(img_path: Path) -> str:
    pil_img = preprocess(img_path)
    return pytesseract.image_to_string(pil_img, config=TESS_CONFIG)


def clean_text(raw: str) -> str:
    """Normalise whitespace and remove common OCR artefacts."""
    text = raw.strip()
    # Collapse multiple blank lines → single blank
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove lone special chars that are OCR noise
    text = re.sub(r'(?m)^[|\\/_\-=~`]{1,3}$', '', text)
    # Normalise smart quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    return text.strip()


# ── Slug helper ────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


# ── Checkpoint helpers ─────────────────────────────────────────────────────────

def load_checkpoint(slug: str) -> set[str]:
    """Return set of already-processed image filenames."""
    cp = DATA_DIR / slug / ".checkpoint.json"
    if cp.exists():
        return set(json.loads(cp.read_text(encoding="utf-8")))
    return set()


def save_checkpoint(slug: str, done: set[str]) -> None:
    cp = DATA_DIR / slug / ".checkpoint.json"
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps(sorted(done), indent=2), encoding="utf-8")


def load_existing_db(slug: str) -> Optional[dict]:
    db_path = DATA_DIR / slug / "ocr_database.json"
    if db_path.exists():
        return json.loads(db_path.read_text(encoding="utf-8"))
    return None


# ── Batch-aware process_book ───────────────────────────────────────────────────

def process_book(book_title: str, image_paths: list[Path],
                 batch_size: Optional[int] = None,
                 resume: bool = True,
                 verbose: bool = True) -> dict:
    slug = slugify(book_title)
    raw_book_dir = RAW_DIR / slug
    raw_book_dir.mkdir(parents=True, exist_ok=True)
    data_book_dir = DATA_DIR / slug
    data_book_dir.mkdir(parents=True, exist_ok=True)

    # Resume: skip already processed images
    done_names = load_checkpoint(slug) if resume else set()
    pending = [p for p in sorted(image_paths) if p.name not in done_names]

    if not pending:
        if verbose:
            print(f"  [RESUME] All {len(image_paths)} images already processed.")
        return load_existing_db(slug) or {}

    # Apply batch limit
    if batch_size and batch_size > 0:
        pending = pending[:batch_size]
        if verbose:
            total_rem = len([p for p in sorted(image_paths) if p.name not in done_names])
            print(f"  [BATCH] Processing {len(pending)} of {total_rem} remaining pages")

    # Load existing pages (for resume/append)
    existing_db = load_existing_db(slug)
    existing_pages: list[dict] = existing_db["pages"] if existing_db else []
    existing_nums = {p["page_number"] for p in existing_pages}

    # Determine starting page number from filename (page_NNN.ext → NNN) or sequence
    def page_num_from_path(p: Path, fallback: int) -> int:
        m = re.match(r"page_(\d+)", p.stem)
        return int(m.group(1)) if m else fallback

    new_pages = []
    total_new_words = 0

    for i, img_path in enumerate(pending):
        global_i = len(existing_pages) + len(new_pages) + 1
        pnum = page_num_from_path(img_path, global_i)

        # Skip if this page number was already stored
        if pnum in existing_nums:
            done_names.add(img_path.name)
            continue

        if verbose:
            already = len(done_names)
            total = len(image_paths)
            print(f"  [{already + i + 1:>4}/{total}] {img_path.name}", end=" … ", flush=True)

        raw_text = ocr_image(img_path)
        clean = clean_text(raw_text)
        words = len(clean.split())
        total_new_words += words

        (raw_book_dir / f"page_{pnum:04d}.txt").write_text(raw_text, encoding="utf-8")

        new_pages.append({
            "page_number": pnum,
            "image_file": img_path.name,
            "text": clean,
            "raw_text": raw_text,
            "word_count": words,
        })
        done_names.add(img_path.name)

        if verbose:
            print(f"{words} words")

    # Merge + sort
    all_pages = sorted(existing_pages + new_pages, key=lambda p: p["page_number"])
    total_words = sum(p.get("word_count", len(p["text"].split())) for p in all_pages)

    db = {
        "metadata": {
            "source_file": book_title,
            "book_slug": slug,
            "total_pages": len(all_pages),
            "processed_pages": len(all_pages),
            "pending_pages": len(image_paths) - len(done_names),
            "page_range": {"start": all_pages[0]["page_number"] if all_pages else 1,
                           "end":   all_pages[-1]["page_number"] if all_pages else 1},
            "processing_date": datetime.now().isoformat(),
            "dpi": "screenshot",
            "total_words": total_words,
            "pages_with_content": sum(1 for p in all_pages if p.get("word_count", 0) > 10),
            "brand": "elbee.yogaman.club",
            "target_site": "https://aiegoo.github.io/yoga",
        },
        "pages": all_pages,
    }

    (data_book_dir / "ocr_database.json").write_text(
        json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    page_index = {str(p["page_number"]): p["text"] for p in all_pages}
    (data_book_dir / "page_index.json").write_text(
        json.dumps(page_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    kw_index: dict[str, list[int]] = defaultdict(list)
    stop = {"the", "a", "an", "and", "or", "of", "in", "to", "is", "it",
             "at", "by", "for", "on", "with", "as", "be", "are", "was", "this"}
    for p in all_pages:
        seen: set[str] = set()
        for word in re.findall(r"[a-z]{3,}", p["text"].lower()):
            if word not in stop and word not in seen:
                kw_index[word].append(p["page_number"])
                seen.add(word)
    (data_book_dir / "keyword_index.json").write_text(
        json.dumps(dict(sorted(kw_index.items())), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    save_checkpoint(slug, done_names)
    return db


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="OCR pipeline for geo project")
    parser.add_argument("--file", help="Process a single image file")
    parser.add_argument("--book", default="", help="Book title (slug used for output folder)")
    parser.add_argument("--ext", default="jpg,jpeg,png,webp,tiff,tif",
                        help="Comma-separated image extensions to scan")
    parser.add_argument("--batch", type=int, default=0,
                        help="Process at most N images per run (0 = all). "
                             "Re-run to continue from checkpoint.")
    parser.add_argument("--no-resume", action="store_true",
                        help="Ignore checkpoint and reprocess everything")
    args = parser.parse_args()

    exts = {f".{e.strip().lower()}" for e in args.ext.split(",")}

    if args.file:
        img = Path(args.file).resolve()
        if not img.exists():
            sys.exit(f"[ERROR] File not found: {img}")
        images = [img]
        book = args.book or img.stem
    else:
        SCREENSHOTS.mkdir(exist_ok=True)
        # Also look in a per-book subfolder if --book given
        slug_dir = SCREENSHOTS / re.sub(r"[^a-z0-9]+", "-", (args.book or "").lower()).strip("-")
        search_dir = slug_dir if slug_dir.exists() and args.book else SCREENSHOTS
        images = sorted(p for p in search_dir.iterdir() if p.suffix.lower() in exts)
        if not images:
            sys.exit(f"[INFO] No images found in {search_dir}\n"
                     f"       Drop screenshots there and re-run.")
        book = args.book or "untitled-book"

    print(f"\n🔍 OCR Pipeline — geo / elbee.yogaman.club")
    print(f"   Book      : {book}")
    print(f"   Images    : {len(images)} total")
    print(f"   Batch     : {args.batch if args.batch else 'all'}")
    print(f"   Resume    : {'no' if args.no_resume else 'yes (checkpoint)'}")
    print(f"   Engine    : Tesseract {pytesseract.get_tesseract_version()}\n")

    db = process_book(book, images,
                      batch_size=args.batch or None,
                      resume=not args.no_resume)

    if not db:
        sys.exit(0)

    meta = db["metadata"]
    pending = meta.get("pending_pages", 0)
    slug = meta["book_slug"]

    print(f"\n✅ Batch done")
    print(f"   Pages in DB     : {meta['processed_pages']}")
    print(f"   Total words     : {meta['total_words']}")
    print(f"   Still pending   : {pending}")
    print(f"   Output → data/json/{slug}/")

    if pending > 0:
        batch = args.batch or 25
        print(f"\n   ▶ {pending} pages remaining — re-run to continue:")
        print(f"     python3 ocr_pipeline.py --book \"{book}\" --batch {batch}")
    else:
        print(f"\n   Next:")
        print(f"     python3 scripts/adapt_content.py --book \"{book}\"")
        print(f"     python3 scripts/batch_commit.py  --book \"{book}\"")


if __name__ == "__main__":
    main()

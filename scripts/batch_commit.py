#!/usr/bin/env python3
"""
geo/scripts/batch_commit.py
────────────────────────────────────────────────────────
Stage and commit OCR output in small, reviewable chunks
so no single push bloats the repo or risks GitHub's limits.

What it commits (never commits screenshots or ocr/raw/):
  • data/json/<slug>/          — JSON databases + checkpoint
  • content/<slug>/            — adapted Jekyll Markdown
  • ocr/processed/<slug>/      — cleaned plain-text pages

Strategy
────────
  --chunk-size N (default 25)
    Groups pages into chunks of N and makes one commit per chunk.
    Each commit message records the page range and word count delta.

  --dry-run
    Shows what would be committed without touching git.

Usage
─────
  python3 scripts/batch_commit.py --book "Light on Yoga"
  python3 scripts/batch_commit.py --book "Light on Yoga" --chunk-size 50
  python3 scripts/batch_commit.py --book "Light on Yoga" --dry-run

After all batches:
  git push origin main
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "json"
CONTENT_DIR = ROOT / "content"
PROCESSED_DIR = ROOT / "ocr" / "processed"
COMMIT_LOG = ROOT / "data" / "json" / ".commit_log.json"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def git(args: list[str], dry_run: bool = False, cwd: Path = ROOT) -> str:
    if dry_run:
        print(f"  [DRY] git {' '.join(args)}")
        return ""
    result = subprocess.run(
        ["git"] + args, cwd=str(cwd), capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  [WARN] git {' '.join(args)}\n  {result.stderr.strip()}")
    return result.stdout.strip()


def load_commit_log() -> dict:
    if COMMIT_LOG.exists():
        return json.loads(COMMIT_LOG.read_text(encoding="utf-8"))
    return {}


def save_commit_log(log: dict) -> None:
    COMMIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    COMMIT_LOG.write_text(json.dumps(log, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Batch-commit OCR output to git")
    parser.add_argument("--book", required=True, help="Book title")
    parser.add_argument("--chunk-size", type=int, default=25,
                        help="Pages per commit (default 25)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview commits without running git")
    parser.add_argument("--push", action="store_true",
                        help="Push to origin/main after all commits")
    args = parser.parse_args()

    slug = slugify(args.book)
    db_path = DATA_DIR / slug / "ocr_database.json"

    if not db_path.exists():
        sys.exit(f"[ERROR] No OCR database at {db_path}\nRun ocr_pipeline.py first.")

    db = json.loads(db_path.read_text(encoding="utf-8"))
    pages = db["pages"]

    if not pages:
        sys.exit("[INFO] No pages in database.")

    # Load commit log to skip already-committed pages
    commit_log = load_commit_log()
    committed_pages = set(commit_log.get(slug, {}).get("committed_pages", []))
    pending_pages = [p for p in pages if p["page_number"] not in committed_pages]

    if not pending_pages:
        print(f"[INFO] All {len(pages)} pages already committed for '{args.book}'.")
        if args.push:
            print("  → Pushing …")
            git(["push", "origin", "main"], dry_run=args.dry_run)
        sys.exit(0)

    # Split into chunks
    chunks = [
        pending_pages[i:i + args.chunk_size]
        for i in range(0, len(pending_pages), args.chunk_size)
    ]

    print(f"\n📦 Batch commit — '{args.book}'")
    print(f"   Pages to commit  : {len(pending_pages)}")
    print(f"   Chunk size       : {args.chunk_size}")
    print(f"   Commits to make  : {len(chunks)}")
    if args.dry_run:
        print("   [DRY RUN]\n")

    newly_committed: list[int] = []

    for ci, chunk in enumerate(chunks, 1):
        pnums = [p["page_number"] for p in chunk]
        p_start, p_end = pnums[0], pnums[-1]
        word_count = sum(p.get("word_count", 0) for p in chunk)

        # Collect files for this chunk
        files_to_stage: list[Path] = []

        # content Markdown
        for p in chunk:
            md = CONTENT_DIR / slug / f"page_{p['page_number']:04d}.md"
            if md.exists():
                files_to_stage.append(md)

        # processed txt
        for p in chunk:
            txt = PROCESSED_DIR / slug / f"page_{p['page_number']:04d}.txt"
            if txt.exists():
                files_to_stage.append(txt)

        # Always include the updated JSON databases + checkpoint (last chunk only adds them once)
        if ci == len(chunks):
            for jf in (DATA_DIR / slug).glob("*.json"):
                files_to_stage.append(jf)
            # Include commit log itself
            files_to_stage.append(COMMIT_LOG)

        if not files_to_stage:
            print(f"  [{ci}/{len(chunks)}] pages {p_start}–{p_end}: no files found, skipping")
            continue

        msg = (f"ocr({slug}): pages {p_start}–{p_end} "
               f"[{len(chunk)} pages, {word_count:,} words] "
               f"brand=elbee.yogaman.club")

        print(f"\n  [{ci}/{len(chunks)}] Committing pages {p_start}–{p_end} "
              f"({len(files_to_stage)} files) …")

        # git add
        rel_files = [str(f.relative_to(ROOT)) for f in files_to_stage]
        git(["add"] + rel_files, dry_run=args.dry_run)

        # Check if there's anything staged
        if not args.dry_run:
            status = git(["diff", "--cached", "--name-only"])
            if not status:
                print(f"    (nothing to commit in this chunk — already up to date)")
                newly_committed.extend(pnums)
                continue

        git(["commit", "-m", msg], dry_run=args.dry_run)
        newly_committed.extend(pnums)
        print(f"    ✅ {msg}")

    # Update commit log
    if not args.dry_run:
        all_committed = sorted(committed_pages | set(newly_committed))
        if slug not in commit_log:
            commit_log[slug] = {}
        commit_log[slug]["committed_pages"] = all_committed
        commit_log[slug]["total_committed"] = len(all_committed)
        commit_log[slug]["book"] = args.book
        save_commit_log(commit_log)
        # Stage the updated log
        git(["add", str(COMMIT_LOG.relative_to(ROOT))])
        staged = git(["diff", "--cached", "--name-only"])
        if staged:
            git(["commit", "-m", f"chore: update commit log for {slug}"])

    # Push
    if args.push:
        print(f"\n🚀 Pushing to origin/main …")
        out = git(["push", "origin", "main"], dry_run=args.dry_run)
        if out:
            print(f"  {out}")

    total_now = len(committed_pages) + len(newly_committed)
    print(f"\n✅ Done — {len(newly_committed)} new pages committed ({total_now}/{len(pages)} total)")
    if not args.push:
        print(f"\n   When ready to push:")
        print(f"   cd {ROOT} && git push origin main")


if __name__ == "__main__":
    main()

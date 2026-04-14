#!/usr/bin/env python3
"""
geo/scripts/watch.py
────────────────────────────────────────────────────────
File-watcher: auto-runs ocr_pipeline.py + adapt_content.py
when a new image lands in screenshots/.

Requires: pip install watchdog
Usage   : python3 scripts/watch.py --book "Light on Yoga"
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    sys.exit("Run: pip install watchdog")

ROOT = Path(__file__).parent.parent
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif"}


class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, book: str):
        self.book = book
        self._pending: set = set()

    def on_created(self, event):
        p = Path(event.src_path)
        if p.suffix.lower() in IMAGE_EXTS and not event.is_directory:
            self._pending.add(p)
            print(f"\n📸 Detected: {p.name}")
            self._run()

    def _run(self):
        print(f"  → Running OCR pipeline …")
        subprocess.run(
            [sys.executable, str(ROOT / "ocr_pipeline.py"), "--book", self.book],
            check=False
        )
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "adapt_content.py"), "--book", self.book],
            check=False
        )
        self._pending.clear()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True, help="Book title")
    args = parser.parse_args()

    watch_dir = ROOT / "screenshots"
    watch_dir.mkdir(exist_ok=True)

    handler = ScreenshotHandler(args.book)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    print(f"👁  Watching {watch_dir} for new images …  (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()

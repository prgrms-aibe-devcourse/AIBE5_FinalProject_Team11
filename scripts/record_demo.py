"""
record_demo.py — headless Playwright recording of the Studio Match Score demo
==============================================================================

Records the LIVE Streamlit app (demo_match_score.py) with real UI interactions:
  - Map rendering with colored studio dots
  - Sidebar: change physical need, location, distance slider
  - Top metric cards updating live
  - Ranked results table
  - Score breakdown section

Usage:
    # Start Streamlit first:
    python3 -m streamlit run scripts/demo_match_score.py --server.port 8510 --server.headless true

    # Record (Chromium must be installed):
    python3 scripts/record_demo.py [--url http://localhost:8510] [--out assets/demo]

    # One-time Chromium install:
    pip install playwright && python3 -m playwright install chromium
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def wait_for_streamlit(url: str, timeout: int = 40) -> None:
    """Block until Streamlit health endpoint responds OK."""
    health = url.rstrip("/") + "/_stcore/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(health, timeout=2)
            if resp.status == 200:
                print(f"[record] Streamlit healthy: {url}")
                time.sleep(2)
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(
        f"Streamlit at {url} not healthy after {timeout}s\n"
        "  Run:  python3 -m streamlit run scripts/demo_match_score.py --server.port 8510 --server.headless true"
    )


def _w(seconds: float) -> None:
    time.sleep(seconds)


def _wheel(page, dy: int, x: int = 900, y: int = 450) -> None:
    page.mouse.move(x, y)
    page.mouse.wheel(0, dy)
    _w(0.5)


def _click_selectbox(page, label_text: str, option_text: str) -> None:
    try:
        box = page.locator(
            f'[data-testid="stSelectbox"]:has(label:has-text("{label_text}"))'
        ).first
        box.click(timeout=5_000)
        _w(0.6)
        page.locator(f'li[role="option"]:has-text("{option_text}")').first.click(timeout=5_000)
        _w(1.5)
        print(f"  [ok] selectbox '{label_text}' → '{option_text}'")
    except Exception as e:
        print(f"  [warn] selectbox '{label_text}' → '{option_text}': {e}")


def _drag_slider(page, label_text: str, target_fraction: float) -> None:
    try:
        slider = page.locator(
            f'[data-testid="stSlider"]:has(label:has-text("{label_text}"))'
        ).first
        thumb = slider.locator('[role="slider"]').first
        thumb.click(timeout=5_000)
        page.keyboard.press("Home")
        _w(0.3)
        steps = int(19 * target_fraction)
        for _ in range(steps):
            page.keyboard.press("ArrowRight")
            _w(0.05)
        _w(1.2)
        print(f"  [ok] slider '{label_text}' → {steps} steps")
    except Exception as e:
        print(f"  [warn] slider '{label_text}': {e}")


# ---------------------------------------------------------------------------
# recording
# ---------------------------------------------------------------------------

def record(url: str, out_dir: Path, headless: bool = True) -> Path:
    """Record the live Streamlit Studio Match Score UI with real interactions."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERROR] Run: pip install playwright && python3 -m playwright install chromium")
        sys.exit(1)

    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    webm_path = out_dir / "aeogeo_demo.webm"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(out_dir),
            record_video_size={"width": 1440, "height": 900},
        )
        page = context.new_page()

        # ── Load Streamlit ──────────────────────────────────────────────────
        print(f"[record] Loading {url} …")
        page.goto(url, wait_until="load", timeout=30_000)
        page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=20_000)
        _w(4)

        # ── Beat 1: Hero view — metric cards + map ──────────────────────────
        print("[record] Beat 1 — hero view")
        try:
            page.wait_for_selector('[data-testid="metric-container"]', timeout=8_000)
        except Exception:
            pass
        _w(5)
        _wheel(page, 150)
        _w(2)
        _wheel(page, -150)
        _w(3)

        # ── Beat 2: Change need → Prenatal ──────────────────────────────────
        print("[record] Beat 2 — change need: Prenatal")
        _click_selectbox(page, "Physical need", "Prenatal")
        _w(3)

        # ── Beat 3: Change need → Lower back pain ───────────────────────────
        print("[record] Beat 3 — change need: Lower back pain")
        _click_selectbox(page, "Physical need", "Lower back pain")
        _w(3)

        # ── Beat 4: Change location → Itaewon ──────────────────────────────
        print("[record] Beat 4 — location: Itaewon")
        _click_selectbox(page, "Your location", "Itaewon")
        _w(3)

        # ── Beat 5: Slider → ~5 km ─────────────────────────────────────────
        print("[record] Beat 5 — distance slider → 5 km")
        _drag_slider(page, "Max travel distance", 0.21)
        _w(3)

        # ── Beat 6: Scroll to ranked table ─────────────────────────────────
        print("[record] Beat 6 — ranked table")
        _wheel(page, 500)
        _w(2)
        _wheel(page, 500)
        _w(5)

        # ── Beat 7: Score breakdown ─────────────────────────────────────────
        print("[record] Beat 7 — score breakdown")
        _wheel(page, 600)
        _w(6)

        # ── Beat 8: Expand first accordion ─────────────────────────────────
        print("[record] Beat 8 — expand accordion")
        try:
            exp = page.locator('[data-testid="stExpander"]').first
            if exp.is_visible(timeout=3_000):
                exp.click()
                _w(3)
        except Exception:
            pass

        # ── Beat 9: Return to hero ──────────────────────────────────────────
        print("[record] Beat 9 — return to top")
        page.evaluate("window.scrollTo(0, 0)")
        _w(0.5)
        _wheel(page, -9999)
        _w(5)

        context.close()
        browser.close()

    # Rename Playwright's auto-named webm
    webm_files = sorted(out_dir.glob("*.webm"), key=lambda p: p.stat().st_mtime)
    if not webm_files:
        raise RuntimeError("No .webm found after recording.")
    latest = webm_files[-1]
    if latest.resolve() != webm_path.resolve():
        latest.rename(webm_path)
    print(f"[record] Saved: {webm_path}  ({webm_path.stat().st_size // 1024} KB)")
    return webm_path


# ---------------------------------------------------------------------------
# ffmpeg -> mp4
# ---------------------------------------------------------------------------

def to_mp4(webm: Path) -> Path:
    mp4 = webm.with_suffix(".mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(webm),
        "-c:v", "libx264",
        "-crf", "22",
        "-preset", "medium",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        str(mp4),
    ]
    print(f"[ffmpeg] Converting to MP4: {mp4}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[ffmpeg] STDERR:", result.stderr[-800:])
        raise RuntimeError("ffmpeg conversion failed")
    print(f"[ffmpeg] MP4 saved: {mp4}  ({mp4.stat().st_size // 1024} KB)")
    return mp4


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url",         default="http://localhost:8510",
                    help="Streamlit URL (default: http://localhost:8510)")
    ap.add_argument("--out",         default="assets/demo")
    ap.add_argument("--no-headless", action="store_true")
    ap.add_argument("--no-mp4",      action="store_true")
    args = ap.parse_args()

    out_dir  = Path(args.out)
    headless = not args.no_headless

    print(f"[record] URL     : {args.url}")
    print(f"[record] Output  : {out_dir.resolve()}")
    print(f"[record] Headless: {headless}")

    wait_for_streamlit(args.url)
    webm = record(args.url, out_dir, headless=headless)

    if not args.no_mp4:
        try:
            mp4 = to_mp4(webm)
            win_dl = Path("/mnt/c/Users/hsyyu/Downloads")
            if win_dl.exists():
                import shutil
                dest = win_dl / mp4.name
                shutil.copy2(mp4, dest)
                print(f"[copy] -> {dest}")
        except Exception as e:
            print(f"[warn] mp4 skip: {e}")


if __name__ == "__main__":
    main()

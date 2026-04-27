"""
Headless teaser recorder
========================

Drives Streamlit demos with Playwright and produces:
  - assets/teaser/match_demo.webm    (raw, full session)
  - assets/teaser/match_demo.mp4     (H.264 re-encode)
  - assets/teaser/shot_03_typing.png
  - assets/teaser/shot_04_ranked.png
  - assets/teaser/shot_05_breakdown.png
  - assets/teaser/shot_07_jsonld.png

Usage:
    python scripts/record_teaser.py            # full run
    python scripts/record_teaser.py --no-video # screenshots only

Requires: playwright (installed) + chromium (installed) + ffmpeg (system).
Streamlit demo + jsonld.html must be reachable; this script auto-spawns them.
"""

from __future__ import annotations

import argparse
import http.server
import shutil
import socketserver
import subprocess
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
TEASER_DIR = REPO / "assets" / "teaser"
TEASER_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORT = {"width": 1920, "height": 1080}
QUERY_KO = "허리가 아픈데 강남에서 추천해줘"


# ---------------------------------------------------------------------------
# Background services
# ---------------------------------------------------------------------------

def _wait_port(host: str, port: int, timeout: float = 30.0) -> bool:
    import socket
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def start_streamlit() -> subprocess.Popen:
    proc = subprocess.Popen(
        [
            "streamlit", "run", "scripts/demo_match_score.py",
            "--server.headless=true",
            "--server.port=8599",
            "--browser.gatherUsageStats=false",
        ],
        cwd=REPO,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_port("127.0.0.1", 8599, timeout=45):
        proc.terminate()
        raise RuntimeError("Streamlit failed to start on :8599")
    time.sleep(2)  # let pydeck mount
    return proc


def start_static_server(port: int = 8600) -> tuple[threading.Thread, socketserver.TCPServer]:
    handler = http.server.SimpleHTTPRequestHandler

    class QuietHandler(handler):  # type: ignore[misc]
        def log_message(self, *_a, **_kw):
            return

    httpd = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
    httpd.RequestHandlerClass.directory = str(TEASER_DIR)  # type: ignore[attr-defined]
    # Set cwd via a custom factory
    orig = httpd.finish_request

    def finish_request(request, client_address):
        # SimpleHTTPRequestHandler honors os.getcwd() at instance time;
        # serve from TEASER_DIR by chdir'ing once.
        return orig(request, client_address)

    import os
    os.chdir(TEASER_DIR)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    if not _wait_port("127.0.0.1", port, timeout=5):
        raise RuntimeError(f"Static server failed on :{port}")
    return t, httpd


# ---------------------------------------------------------------------------
# Recording
# ---------------------------------------------------------------------------

def _type_human(page, selector: str, text: str, per_char_ms: int = 60) -> None:
    el = page.locator(selector).first
    el.click()
    for ch in text:
        el.type(ch, delay=per_char_ms)
    page.wait_for_timeout(800)


def record_match_demo(record_video: bool) -> None:
    print("[teaser] starting Streamlit on :8599…")
    streamlit_proc = start_streamlit()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx_kwargs = dict(viewport=VIEWPORT, locale="ko-KR")
            if record_video:
                ctx_kwargs["record_video_dir"] = str(TEASER_DIR)
                ctx_kwargs["record_video_size"] = VIEWPORT
            ctx = browser.new_context(**ctx_kwargs)
            page = ctx.new_page()

            print("[teaser] navigating to Streamlit demo…")
            page.goto("http://127.0.0.1:8599", wait_until="networkidle", timeout=60_000)
            page.wait_for_timeout(3500)

            # Wait for the page title to render — proves the app is up.
            page.get_by_text("Studio Match Score").first.wait_for(
                state="visible", timeout=20_000
            )
            page.wait_for_timeout(1500)
            page.screenshot(path=str(TEASER_DIR / "shot_03a_blank.png"), full_page=False)

            # Open the "Physical need / intent" selectbox in the sidebar so
            # viewers see the system actually responding to user intent.
            print("[teaser] interacting with sidebar selectbox…")
            try:
                selectboxes = page.locator("[data-baseweb='select']")
                selectboxes.first.click(timeout=5_000)
                page.wait_for_timeout(1200)
                page.screenshot(path=str(TEASER_DIR / "shot_03_typing.png"))
                # Click on "Lower back pain" option (it's already default,
                # but clicking re-confirms and closes the dropdown).
                page.get_by_text("Lower back pain", exact=True).first.click(timeout=5_000)
                page.wait_for_timeout(2500)
            except Exception as e:
                print(f"[teaser] selectbox interaction skipped: {e}")
                page.screenshot(path=str(TEASER_DIR / "shot_03_typing.png"))

            # Scroll to ranked matches / map area
            page.mouse.wheel(0, 700)
            page.wait_for_timeout(1500)
            page.screenshot(path=str(TEASER_DIR / "shot_04_ranked.png"))

            # Scroll further down to score-breakdown expanders, open the
            # second one (the first is open by default).
            page.mouse.wheel(0, 900)
            page.wait_for_timeout(1500)
            try:
                summaries = page.locator("summary")
                count = summaries.count()
                if count > 1:
                    summaries.nth(1).click(timeout=5_000)
                    page.wait_for_timeout(1500)
            except Exception as e:
                print(f"[teaser] expander click skipped: {e}")
            page.screenshot(path=str(TEASER_DIR / "shot_05_breakdown.png"))

            page.wait_for_timeout(1000)
            ctx.close()
            browser.close()

        # Move the recorded video to a stable name
        if record_video:
            webms = sorted(TEASER_DIR.glob("*.webm"), key=lambda p: p.stat().st_mtime, reverse=True)
            if webms:
                src = webms[0]
                dst = TEASER_DIR / "match_demo.webm"
                if src != dst:
                    shutil.move(str(src), str(dst))
                print(f"[teaser] webm saved: {dst} ({dst.stat().st_size // 1024} KB)")

                # Re-encode to MP4 H.264 for Descript/DaVinci
                mp4 = TEASER_DIR / "match_demo.mp4"
                cmd = [
                    "ffmpeg", "-y", "-i", str(dst),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(mp4),
                ]
                r = subprocess.run(cmd, capture_output=True)
                if r.returncode == 0:
                    print(f"[teaser] mp4 saved: {mp4} ({mp4.stat().st_size // 1024} KB)")
                else:
                    print("[teaser] ffmpeg failed:", r.stderr.decode()[-500:])
    finally:
        streamlit_proc.terminate()
        streamlit_proc.wait(timeout=10)


def record_jsonld() -> None:
    """Capture the JSON-LD page (shot 7)."""
    page_path = TEASER_DIR / "jsonld.html"
    if not page_path.exists():
        print("[teaser] jsonld.html missing — generate it first")
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=VIEWPORT)
        page = ctx.new_page()
        page.goto(f"file://{page_path}")
        page.wait_for_timeout(800)
        page.screenshot(path=str(TEASER_DIR / "shot_07_jsonld.png"), full_page=True)
        browser.close()
    print(f"[teaser] shot_07 saved")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-video", action="store_true", help="screenshots only")
    ap.add_argument("--only", choices=["match", "jsonld"], default=None)
    args = ap.parse_args()

    if args.only in (None, "match"):
        record_match_demo(record_video=not args.no_video)
    if args.only in (None, "jsonld"):
        record_jsonld()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

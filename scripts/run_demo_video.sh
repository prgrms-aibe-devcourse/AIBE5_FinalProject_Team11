#!/usr/bin/env bash
# run_demo_video.sh — one-shot installer + recorder for aeogeo demo video
# -------------------------------------------------------------------------
# Usage:
#   bash scripts/run_demo_video.sh           # normal headless run
#   bash scripts/run_demo_video.sh --visible # show browser window
# =========================================================================
set -euo pipefail
# Ignore SIGINT so the recording isn't interrupted by terminal Ctrl+C forwarding
trap '' INT

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

STREAMLIT_PORT=8502
APP_SCRIPT="scripts/demo_match_score.py"
RECORD_SCRIPT="scripts/record_demo.py"
OUT_DIR="assets/demo"
VISIBLE="${1:-}"

echo "======================================="
echo " aeogeo · Demo Video Recorder"
echo "======================================="

# ── 1. Ensure playwright is installed ─────────────────────────────────────
echo "[setup] Checking playwright …"
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "[setup] Installing playwright Python package …"
    pip3 install --quiet playwright
fi

# ── 2. Ensure Chromium browser binary is present ──────────────────────────
echo "[setup] Checking Chromium …"
if ! python3 -m playwright install --help 2>/dev/null | grep -q "chromium" 2>/dev/null; then
    true  # command exists
fi
# Always run install (idempotent, skips if already present)
python3 -m playwright install chromium 2>&1 | tail -5

# ── 3. Start Streamlit if not already running ─────────────────────────────
echo "[setup] Checking if Streamlit is up on port $STREAMLIT_PORT …"
if curl -s --max-time 2 "http://localhost:$STREAMLIT_PORT" > /dev/null 2>&1; then
    echo "[setup] Streamlit already running ✓"
    STARTED_ST=false
else
    echo "[setup] Starting Streamlit in background …"
    streamlit run "$APP_SCRIPT" \
        --server.port "$STREAMLIT_PORT" \
        --server.headless true \
        --server.address 0.0.0.0 \
        > /tmp/streamlit_demo.log 2>&1 &
    ST_PID=$!
    echo "[setup] Streamlit PID: $ST_PID"
    STARTED_ST=true

    # Wait up to 30s for it to be ready
    echo -n "[setup] Waiting for Streamlit "
    for i in $(seq 1 30); do
        if curl -s --max-time 1 "http://localhost:$STREAMLIT_PORT" > /dev/null 2>&1; then
            echo " ready!"
            break
        fi
        echo -n "."
        sleep 1
    done
fi

# ── 4. Record ──────────────────────────────────────────────────────────────
echo ""
echo "[record] Starting headless recording …"
if [[ "$VISIBLE" == "--visible" ]]; then
    python3 "$RECORD_SCRIPT" --out "$OUT_DIR" --match "http://localhost:$STREAMLIT_PORT" --no-headless
else
    python3 "$RECORD_SCRIPT" --out "$OUT_DIR" --match "http://localhost:$STREAMLIT_PORT"
fi

# ── 5. Clean up Streamlit if we started it ─────────────────────────────────
if [[ "${STARTED_ST:-false}" == "true" ]]; then
    echo "[cleanup] Stopping Streamlit (PID $ST_PID) …"
    kill "$ST_PID" 2>/dev/null || true
fi

echo ""
echo "======================================="
echo " Done!  Output: $REPO_ROOT/$OUT_DIR/"
ls -lh "$REPO_ROOT/$OUT_DIR/" 2>/dev/null || true
echo "======================================="

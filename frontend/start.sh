#!/usr/bin/env bash
# frontend/start.sh — Start the Vite dev server
# Run from the repo root or frontend/ directory.
# Requires Node 18+. Uses nvm if available, otherwise checks for node18.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── Ensure Node 18+ is available ─────────────────────────────────────
load_nvm() {
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
}

check_node_version() {
  local ver
  ver=$(node -e "process.exit(parseInt(process.version.slice(1)) < 18 ? 1 : 0)" 2>/dev/null && echo "ok" || echo "old")
  echo "$ver"
}

load_nvm
if [[ "$(check_node_version)" == "old" ]]; then
  echo "⚠️  Node $(node --version) detected — Vite 5 requires Node 18+."
  if command -v nvm &>/dev/null; then
    echo "→ Installing Node 18 via nvm…"
    nvm install 18
    nvm use 18
  else
    echo "→ Installing nvm…"
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    load_nvm
    nvm install 18
    nvm use 18
  fi
fi

echo "✓ Node $(node --version) — starting Vite dev server on http://localhost:5173"

# ── Install deps if node_modules is missing ───────────────────────────
if [ ! -f "package.json" ]; then
  echo "❌ package.json not found. Run from the frontend/ directory."
  exit 1
fi

# ── Start dev server ─────────────────────────────────────────────────
exec node node_modules/.bin/vite --host 0.0.0.0 --port 5173

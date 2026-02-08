#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

STREAMLIT_BIN="streamlit"
if [ -x "$ROOT_DIR/.venv/bin/streamlit" ]; then
  STREAMLIT_BIN="$ROOT_DIR/.venv/bin/streamlit"
fi

(
  sleep 2
  if command -v open >/dev/null 2>&1; then
    open http://localhost:8501
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:8501
  fi
) &

exec "$STREAMLIT_BIN" run main.py --server.address 127.0.0.1 --server.port 8501

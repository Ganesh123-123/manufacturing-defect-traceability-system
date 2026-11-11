#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "Starting Frontend HTTP Server on http://localhost:8000..."
python -m http.server 8000 --directory frontend


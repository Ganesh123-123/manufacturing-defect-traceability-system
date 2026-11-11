#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "Starting Flask Backend on http://127.0.0.1:5000..."
python backend/app.py

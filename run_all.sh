#!/usr/bin/env bash
# Start all services for Linux / macOS environments
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "Starting Manufacturing Defect Traceability System"
echo "=========================================================="

# Check if MySQL is running or use environment variables
export MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
export MYSQL_PORT="${MYSQL_PORT:-3306}"
export MYSQL_USER="${MYSQL_USER:-root}"
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"
export MYSQL_DB="${MYSQL_DB:-defect_traceability}"

echo "Starting Flask Backend Server on port 5000..."
python backend/app.py &
BACKEND_PID=$!

echo "Starting Frontend HTTP Server on port 8000..."
python -m http.server 8000 --directory frontend &
FRONTEND_PID=$!

echo ""
echo "System running successfully!"
echo "Frontend: http://localhost:8000"
echo "Backend:  http://127.0.0.1:5000"
echo "Press CTRL+C to terminate all services."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait

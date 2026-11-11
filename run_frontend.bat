@echo off
title Frontend HTTP Server
cd /d %~dp0
echo Starting Frontend HTTP Server on http://localhost:8000...
start http://localhost:8000
python -m http.server 8000 --directory frontend
pause

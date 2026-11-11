@echo off
title Flask Backend Server
cd /d %~dp0
echo Starting Flask REST API on http://127.0.0.1:5000...
python backend\app.py
pause

@echo off
title Manufacturing Defect Traceability System
echo ==============================================================
echo Starting Manufacturing Defect Traceability System...
echo ==============================================================

:: Start MySQL Server in background if not already running
start "MySQL 8.0 Server" /B "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --defaults-file="%~dp0.mysql_data\my.ini" --console
timeout /t 3 /nobreak >nul

:: Start Flask Backend Server
start "Flask Backend Server (Port 5000)" cmd /k "cd /d %~dp0 && python backend\app.py"
timeout /t 2 /nobreak >nul

:: Start Frontend HTTP Server
start "Frontend Static Server (Port 8000)" cmd /k "cd /d %~dp0 && python -m http.server 8000 --directory frontend"
timeout /t 1 /nobreak >nul

:: Open Browser
start http://localhost:8000

echo.
echo ==============================================================
echo System running successfully!
echo Frontend: http://localhost:8000
echo Backend:  http://localhost:5000
echo ==============================================================
pause

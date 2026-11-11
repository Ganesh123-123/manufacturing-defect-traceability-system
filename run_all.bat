@echo off
setlocal
title Manufacturing Defect Traceability System
cd /d "%~dp0" || exit /b 1

echo ==============================================================
echo Starting Manufacturing Defect Traceability System...
echo ==============================================================

if exist "venv\Scripts\python.exe" (
    set "PYTHON=%CD%\venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)
echo Python: %PYTHON%

"%PYTHON%" -c "import flask, flask_cors, flask_sqlalchemy, pymysql" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python dependencies are missing.
    echo Install them with: "%PYTHON%" -m pip install -r requirements.txt
    exit /b 1
)

if not defined MYSQL_PORT set "MYSQL_PORT=3307"
if not defined PORT set "PORT=5000"

call :check_database
if not errorlevel 1 goto database_ready

if not "%MYSQL_PORT%"=="3307" (
    echo ERROR: MySQL is not available on port %MYSQL_PORT%.
    echo Start the configured database, or use the bundled MySQL configuration on port 3307.
    exit /b 1
)
if not exist ".mysql_data\my.ini" (
    echo ERROR: MySQL is unavailable and .mysql_data\my.ini was not found.
    exit /b 1
)

set "MYSQLD="
for /f "delims=" %%M in ('where mysqld.exe 2^>nul') do if not defined MYSQLD set "MYSQLD=%%M"
if not defined MYSQLD if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" set "MYSQLD=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
if not defined MYSQLD (
    echo ERROR: MySQL is not running and mysqld.exe could not be found.
    exit /b 1
)

"%PYTHON%" -c "import socket; s=socket.socket(); s.settimeout(1); result=s.connect_ex(('127.0.0.1',3307)); s.close(); raise SystemExit(0 if result == 0 else 1)" >nul 2>&1
if not errorlevel 1 (
    echo ERROR: Port 3307 is occupied, but the configured MySQL database is not responding.
    exit /b 1
)

echo Starting local MySQL on port 3307...
start "MySQL 8.0 Server" /D "%CD%" "%MYSQLD%" --defaults-file="%CD%\.mysql_data\my.ini" --console
for /L %%i in (1,1,30) do (
    call :check_database
    if not errorlevel 1 goto database_ready
    timeout /t 1 /nobreak >nul
)
echo ERROR: MySQL did not become available on port 3307.
exit /b 1

:database_ready
call :check_backend
if not errorlevel 1 goto backend_ready

"%PYTHON%" -c "import socket; s=socket.socket(); s.settimeout(1); result=s.connect_ex(('127.0.0.1',%PORT%)); s.close(); raise SystemExit(0 if result == 0 else 1)" >nul 2>&1
if not errorlevel 1 (
    echo ERROR: Port %PORT% is occupied, but the backend health check failed.
    exit /b 1
)

echo Starting Flask backend on port %PORT%...
start "Flask Backend Server" /D "%CD%" "%ComSpec%" /k ""%PYTHON%" backend\app.py"
for /L %%i in (1,1,30) do (
    call :check_backend
    if not errorlevel 1 goto backend_ready
    timeout /t 1 /nobreak >nul
)
echo ERROR: The backend did not become healthy. Check the Flask server window.
exit /b 1

:backend_ready
call :check_frontend
if errorlevel 1 (
    echo ERROR: The unified application page could not be loaded from port %PORT%.
    exit /b 1
)

echo.
echo ==============================================================
echo System is running.
echo Frontend and Backend: http://localhost:%PORT%
echo ==============================================================
start "" "http://localhost:%PORT%"
exit /b 0

:check_database
"%PYTHON%" -c "from backend.config import Config; import pymysql; c=pymysql.connect(host=Config.MYSQL_HOST,port=Config.MYSQL_PORT,user=Config.MYSQL_USER,password=Config.MYSQL_PASSWORD,database=Config.MYSQL_DB,connect_timeout=2); c.close()" >nul 2>&1
exit /b %errorlevel%

:check_backend
"%PYTHON%" -c "import json,urllib.request; d=json.load(urllib.request.urlopen('http://127.0.0.1:%PORT%/api/system/health',timeout=2)); assert d.get('status')=='healthy' and d.get('database')=='connected'" >nul 2>&1
exit /b %errorlevel%

:check_frontend
"%PYTHON%" -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:%PORT%/',timeout=3); page=r.read(65536).decode('utf-8'); assert r.status==200 and '<html' in page.lower() and 'js/api.js' in page" >nul 2>&1
exit /b %errorlevel%

@echo off
chcp 65001 > nul
echo ==============================================
echo  Self-Mirror — Web Interface
echo ==============================================
echo.

:: Check for python/py
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
) else (
    set PYTHON_CMD=python
)

echo [1/3] Checking requirements...
%PYTHON_CMD% -c "import flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Flask not found. Installing requirements...
    %PYTHON_CMD% -m pip install -r requirements.txt
)

echo [2/3] Starting Backend Server on port 3004...
set PORT=3004
set FLASK_APP=app.py

:: Start Flask server in the background and wait a bit
start /b cmd /c "%PYTHON_CMD% app.py"
timeout /t 3 /nobreak > nul

echo [3/3] Opening Web Interface...
start http://127.0.0.1:3004

echo.
echo ==============================================
echo  [SUCCESS] Self-Mirror Web is running!
echo  Please use the web interface in your browser.
echo.
echo  Note: To stop the server, click "關閉系統" 
echo  in the top right corner of the web interface,
echo  or close this command window.
echo ==============================================
pause

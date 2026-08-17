@echo off
chcp 65001 > nul
echo ==============================================
echo  Self-Mirror — GitHub Auto Updater
echo  Repository: awesomerex09/Villain
echo ==============================================
echo.

:: Get current date and time for commit message
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%

echo [1/3] Adding all changes...
git add -A

echo [2/3] Committing changes...
git commit -m "chore: auto-update [%TIMESTAMP%]"

if %errorlevel% equ 1 (
    echo [INFO] Nothing to commit. Working tree clean.
    echo.
    pause
    exit /b 0
)

echo [3/3] Pushing to GitHub (awesomerex09/Villain)...
git push origin main

echo.
if %errorlevel% neq 0 (
    echo [ERROR] Push failed. Check your Git credentials and network connection.
    echo.
    echo  Troubleshooting:
    echo    1. Make sure you have set up SSH key or Personal Access Token
    echo    2. Run: git remote -v  (to verify remote URL)
    echo    3. Run: git remote set-url origin https://github.com/awesomerex09/Villain.git
) else (
    echo [SUCCESS] Successfully pushed to https://github.com/awesomerex09/Villain
)
echo.
pause

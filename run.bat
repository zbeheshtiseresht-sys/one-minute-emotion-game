@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   One Minute Emotion Game - Anywhere
echo ============================================
echo.

if not exist cloudflared.exe (
  echo ERROR: cloudflared.exe was not found.
  echo Put cloudflared.exe in this folder, next to run.bat.
  pause
  exit /b 1
)

echo Starting Flask server...
start "Emotion Game Server" /B py app.py

echo Waiting for the server to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting Cloudflare Tunnel...
echo When a https://*.trycloudflare.com link appears, open it on your phone.
echo Keep this window open while using the game.
echo.
.\cloudflared.exe tunnel --url http://127.0.0.1:5000

endlocal

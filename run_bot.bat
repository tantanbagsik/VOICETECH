@echo off
echo ========================================
echo Voice Appointment Bot - Setup & Run
echo ========================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo Python not found! Install from https://python.org
    pause
    exit /b
)

echo.
echo [2/4] Downloading/updating code...
git clone https://github.com/tantanbagsik/VOICETECH.git
cd VOICETECH

echo.
echo [3/4] Installing dependencies...
pip install pyttsx3 dateparser SpeechRecognition

echo.
echo [4/4] Starting Voice Bot...
echo.
echo ========================================
echo BOT IS RUNNING - SPEAK TO IT!
echo ========================================
echo.
py bot.py

pause

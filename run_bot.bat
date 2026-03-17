@echo off
echo ========================================
echo Voice Appointment Bot - Setup & Run
echo ========================================
echo.

echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo Python not found! Install from https://python.org
    pause
    exit /b
)

echo.
echo [2/5] Getting code...
cd %USERPROFILE%\Desktop
if not exist "VOICETECH" (
    git clone https://github.com/tantanbagsik/VOICETECH.git
)
cd VOICETECH
git pull

echo.
echo [3/5] Installing dependencies...
pip install --upgrade pyttsx3 dateparser SpeechRecognition

echo.
echo [4/5] Testing imports...
python -c "from bot import VoiceAppointmentBot; print('OK')"

echo.
echo [5/5] Starting Voice Bot...
echo.
echo ========================================
echo BOT IS RUNNING - SPEAK TO IT!
echo ========================================
echo.
py bot.py

pause

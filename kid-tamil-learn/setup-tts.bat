@echo off
REM Tamil Learning App - TTS Setup Helper (Windows)

echo 🇹🇷 Tamil Learning App - TTS Setup Helper
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    echo Download from: https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
    echo ✅ Python %%i found
)
echo.

REM Menu
echo Choose your setup option:
echo.
echo 1) Setup Local Backend (pyttsx3 - Offline)
echo 2) Setup Local Backend (Coqui TTS - High Quality)
echo 3) Setup Google Cloud TTS (Professional Quality)
echo 4) Test Current Installation
echo 5) Start Backend Server
echo 6) Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo 📦 Installing pyttsx3 backend...
    pip install pyttsx3 flask flask-cors
    echo.
    echo ✅ pyttsx3 installed successfully!
    echo 🚀 Next: Run 'python backend.py' to start server
    pause
) else if "%choice%"=="2" (
    echo.
    echo 📦 Installing Coqui TTS (High Quality Neural Voice)...
    echo ⚠️  This is large ^(~500MB^) and may take 5-10 minutes...
    pip install TTS flask flask-cors
    echo.
    echo ✅ Coqui TTS installed successfully!
    echo 🚀 Next: Run 'python backend.py' to start server
    pause
) else if "%choice%"=="3" (
    echo.
    echo 🔑 Google Cloud Text-to-Speech Setup
    echo ======================================
    echo.
    echo 1. Go to: https://cloud.google.com/text-to-speech
    echo 2. Click 'Try Free' and sign in
    echo 3. Create a new project
    echo 4. Enable Text-to-Speech API
    echo 5. Create Service Account ^(with JSON key^)
    echo 6. Download the JSON file
    echo 7. Set environment variable:
    echo.
    echo    set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\key.json
    echo.
    echo 8. Test with:
    echo    pip install google-cloud-texttospeech flask flask-cors
    echo    python backend.py
    echo.
    pause
) else if "%choice%"=="4" (
    echo.
    echo 🧪 Testing current TTS installation...
    echo.
    python -c "import pyttsx3; print('✅ pyttsx3: Available')" 2>nul || echo ❌ pyttsx3: Not installed
    python -c "from TTS.api import TTS; print('✅ Coqui TTS: Available')" 2>nul || echo ❌ Coqui TTS: Not installed
    python -c "from google.cloud import texttospeech; print('✅ Google Cloud TTS: Available')" 2>nul || echo ❌ Google Cloud TTS: Not installed
    python -c "import flask; print('✅ Flask: Available')" 2>nul || echo ❌ Flask: Not installed
    echo.
    echo Run 'python backend.py' to start the server
    echo.
    pause
) else if "%choice%"=="5" (
    echo.
    echo 🚀 Starting Tamil Learning Backend...
    echo ======================================
    echo.
    echo Make sure you're in the kid-tamil-learn directory
    echo.
    python backend.py
    pause
) else if "%choice%"=="6" (
    echo Goodbye! 👋
    exit /b 0
) else (
    echo ❌ Invalid choice
    pause
    exit /b 1
)

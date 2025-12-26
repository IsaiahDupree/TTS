@echo off
REM Windows Setup Script for IndexTTS2 API
REM Sets up environment variables for Windows

echo ========================================
echo IndexTTS2 API Windows Setup
echo ========================================
echo.

REM Set Hugging Face Token
REM Replace YOUR_HF_TOKEN_HERE with your actual Hugging Face token
set HF_TOKEN=YOUR_HF_TOKEN_HERE
set HUGGINGFACE_HUB_TOKEN=YOUR_HF_TOKEN_HERE

echo ✅ Hugging Face token set
echo.

REM Activate virtual environment (adjust path as needed)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found
    echo    Create with: python -m venv venv
)

echo.
echo ========================================
echo Setup Complete
echo ========================================
echo.
echo You can now run:
echo   python run_emotion_generations.py --voice "path\to\voice.wav" --text "Your text"
echo.

pause


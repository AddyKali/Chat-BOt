@echo off
echo ================================================
echo Voice Assistant Setup Script
echo ================================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo Creating directories...
if not exist "logs" mkdir logs
if not exist "configs" mkdir configs
echo.

echo Setup complete!
echo.
echo ================================================
echo Next Steps:
echo ================================================
echo 1. Edit configs/config.json with your settings
echo 2. Add your Anthropic API key (optional)
echo 3. Run: python enhanced_main.py
echo.
echo For PyAudio issues, see README.md
echo ================================================
echo.
pause

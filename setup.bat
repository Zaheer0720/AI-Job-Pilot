@echo off
echo =========================================
echo   AI Job Hunter - Setup Script
echo =========================================

echo.
echo [1/4] Setting up Python virtual environment...
cd /d "%~dp0backend"
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/4] Installing Playwright browsers...
playwright install chromium

echo.
echo [4/4] Setting up frontend...
cd /d "%~dp0frontend"
npm install

echo.
echo =========================================
echo   Setup Complete!
echo.
echo   Next steps:
echo   1. Copy .env.example to .env
echo   2. Add your GEMINI_API_KEY to .env
echo   3. Run start.bat to launch the app
echo =========================================
pause

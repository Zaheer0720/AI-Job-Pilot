@echo off
echo =========================================
echo   Starting AI Job Hunter
echo =========================================

echo.
echo Starting Backend (FastAPI)...
start "AI Job Hunter - Backend" cmd /k "cd /d "%~dp0backend" && venv\Scripts\activate.bat && python main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting Frontend (Vite)...
start "AI Job Hunter - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo =========================================
echo   App is starting!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo =========================================

timeout /t 4 /nobreak > nul
start http://localhost:5173

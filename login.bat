@echo off
echo =========================================
echo   LinkedIn one-time login
echo =========================================
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
python linkedin_login.py
pause

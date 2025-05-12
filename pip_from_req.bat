@echo off
cd /d "%~dp0"

REM Activate virtual environment
if exist "venv\" (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Install from requirements.txt
echo Installing packages from requirements.txt...
pip install -r requirements.txt

pause

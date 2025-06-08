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

REM Open the folder in VS Code
echo Opening project in PyCharm...
code .

REM Run Django migrations
echo Running makemigrations...
python manage.py makemigrations

echo Running migrate...
python manage.py migrate

pause

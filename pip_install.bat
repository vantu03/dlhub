@echo off
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

:loop
set /p LIBS=Enter the library to install (or leave blank to exit): 
if "%LIBS%"=="" goto end

echo Installing %LIBS%...
pip install %LIBS%
set LIBS=
goto loop

:end
echo Exiting. Saving installed libraries to requirements.txt...
pip freeze > requirements.txt
pause

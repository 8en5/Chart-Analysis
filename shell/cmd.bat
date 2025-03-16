@echo off

echo Start routine for ready to use cmd ...

:: Step 1: Go to workspace
echo cd ..
cd ..
set "WORKSPACE=%cd%"

:: Step 2: Activate virtual environment
set "VENV_ACTIVATE=%WORKSPACE%\.venv\Scripts\activate.bat"
if exist "%VENV_ACTIVATE%" (
    echo call .venv\Scripts\activate.bat
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found - call setup_workspace.py
    exit /b 1
)

:: Step 3: Add workspace to PYTHONPATH
echo set "PYTHONPATH=%PYTHONPATH%;%WORKSPACE%"
set "PYTHONPATH=%PYTHONPATH%;%WORKSPACE%"

REM Keep terminal open
echo.
cmd /k

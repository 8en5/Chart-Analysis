@echo off

echo Start routine for ready to use cmd ...

:: Step 1: Go to workspace
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
echo PYTHONPATH set to %WORKSPACE%
set "PYTHONPATH=%PYTHONPATH%;%WORKSPACE%"


:: Step 4: Ensure 'data/' directory exists
if not exist "data" (
    echo Creating 'data' directory...
    mkdir data
)

:: Step 5: run python script
::set SCRIPT=scripts\meta_analysis\study_visualize_strategies.py
set SCRIPT=scripts\study\study_indicator_invested.py
if exist %SCRIPT% (
    echo Starting script %SCRIPT%...
    ::python %SCRIPT% > data\output.log 2>&1
    python %SCRIPT%
    echo Script started successfully. Check data\output.log for logs.
) else (
    echo Python script %SCRIPT% not found.
    exit /b 1
)


REM Keep terminal open
echo.
pause

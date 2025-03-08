@echo off

REM Create venv if venv does not exists
echo Virtual Environment:
if exist .venv (
    echo venv already exists
) else (
    echo Create venv ...
    python -m venv venv
)


REM Activate venv and install libraries
call venv\Scripts\activate
echo Install libraries (only missing libraries)
pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

echo Setup finished
pause
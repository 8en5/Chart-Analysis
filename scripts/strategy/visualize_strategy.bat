@echo off
REM With this bat you can call "run.py" in another cmd
REM it activates the venv and call run.py in a cmd

REM navigate to ws
cd ../..

REM navigate to folder .venv/Scripts
cd .venv\Scripts

REM activate virtual environment
call activate

REM Back to ws
cd ../..

REM navigate to the python script
cd scripts\strategy

REM call python script
python visualize_strategy.py
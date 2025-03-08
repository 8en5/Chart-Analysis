@echo off
REM With this bat you can run a python file in another cmd
REM it first activates the venv and then run the python file

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
python visualize_strategies.py

REM Keep the cmd open
cmd /k
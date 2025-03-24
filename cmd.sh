#!/bin/bash

echo "Start routine for ready to use shell..."

# Step 1: Go to workspace
#echo "cd ../.."
#cd ../..
WORKSPACE=$(pwd)

# Step 2: Activate virtual environment
VENV_ACTIVATE="$WORKSPACE/.venv/bin/activate"
if [ -f "$VENV_ACTIVATE" ]; then
    echo "source .venv/bin/activate"
    source .venv/bin/activate
else
    echo "Virtual environment not found - call setup_workspace.py"
    exit 1
fi

# Step 3: Add workspace to PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$WORKSPACE"
echo "PYTHONPATH set to $PYTHONPATH"

# Step 4: Ensure 'data/' directory exists
if [ ! -d "data" ]; then
    echo "Creating 'data' directory..."
    mkdir -p data
fi

# Step 5: Run python script (in background with nohup)
#SCRIPT="scripts/meta_analysis/study_visualize_strategies.py"
SCRIPT="scripts/meta_analysis/study_indicator_params.py"
if [ -f "$SCRIPT" ]; then
    echo "Starting script $SCRIPT with nohup..."
    nohup python3 $SCRIPT > data/output.log 2>&1 &
    echo "Script started successfully and is running in the background. Check data/output.log for logs."
else
    echo "Python script $SCRIPT not found."
    exit 1
fi
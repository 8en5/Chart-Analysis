#!/bin/bash

echo "Start routine for ready to use shell..."

# Step 1: Go to workspace
echo "cd .."
cd ..
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

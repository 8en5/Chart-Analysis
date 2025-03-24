# Chart-Analysis
Analyze charts using indicators and backtesting

## Getting started
### Setting up workspace
- run `python setup_workspace.py`
  - creates a virtual environment (venv)
  - downloads teh required libraries from requirements.txt
  - fixes the import error from the lib pandas_ta
    - squeeze_pro.py line 2: replace `from numpy import NaN as npNaN` with `from numpy import nan as npNaN`

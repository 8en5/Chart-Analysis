# Chart-Analysis
Analyze charts using indicators and backtesting

## Getting started
- import libraries via requirements.txt

### Fix ImportError in pandas_ta
- Error in `import pandas_ta as ta`
    - *ImportError: cannot import name 'NaN' from 'numpy' (C:\..\Chart-Analysis\.venv\Lib\site-packages\numpy\__init__.py). Did you mean: 'nan'?*
- Solution:
  - go to *'.venv\Lib\site-packages\pandas_ta\momentum\squeeze_pro.py", line 2, in module'* and replace 'NaN' with 'nan'
    - `from numpy import nan as npNaN`

### First steps
- run `cc_api_load_symbols.py` (csv with all symbols in crypto compare)
- run `cc_api_download_courses.py` (to get historical course data)
  - run 2x: 1x with `source = yaml` and 1x with `source = api` (getting 2 folders with data, yaml for testing and api for extensive analyses)
- run your first strategy for testing: `visualize_strategy.py` with `run_type = 1` and an existing strategy
  - then try `run_type = 2` for param_study and `run_type = 3` for symbol study and see the output plots in the folders
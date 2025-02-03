# Chart-Analysis
Analyze charts using indicators and backtesting

## Workspace setup
- import libraries via requirements.txt

### ImportError in pandas_ta
- Error in `import pandas_ta as ta`
    - *ImportError: cannot import name 'NaN' from 'numpy' (C:\..\Chart-Analysis\.venv\Lib\site-packages\numpy\__init__.py). Did you mean: 'nan'?*
- Solution:
  - go to *'.venv\Lib\site-packages\pandas_ta\momentum\squeeze_pro.py", line 2, in module'* and replace 'NaN' with 'nan'
    - `from numpy import nan as npNaN`

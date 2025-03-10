import subprocess
import sys
import os


def create_venv():
    """ Create virtual environment (venv) if it does not exists
    """
    print('Virtual Environment ...')
    if not os.path.exists('.venv'):
        print('Create virtual environment (venv) ...')
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
    else:
        print('Virtual environment (venv) already exists')
    print('\n')


def install_requirements():
    """ Install requirements.txt
    """
    print('Install libraries (only missing libraries) ...')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    print('\n')


from pathlib import Path
def repair_import_error_pandas_ta():
    """ Fixes the import error from the lib pandas_ta
    file: .venv/Lib/site-packages/pandas_ta/momentum/squeeze_pro.py
      line 2: replace `from numpy import NaN as npNaN` with `from numpy import nan as npNaN`
    """
    file_path = Path(__file__).parent / '.venv/Lib/site-packages/pandas_ta/momentum/squeeze_pro.py'
    target_string = 'from numpy import NaN as npNaN'
    replacement_string = 'from numpy import nan as npNaN'

    print('Fix pandas_ta import error ...')
    if not file_path.exists():
        raise ValueError(f'file path {file_path} does not exist - there was a problem installing the libraries from requirements.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if len(lines) >= 2 and lines[1].strip() == target_string:
        lines[1] = replacement_string + '\n'

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        print('Import Error in lib pandas_ta fixed')
    else:
        print('Import Error in lib pandas_ta was already fixed')
    print('\n')



if __name__ == '__main__':
    create_venv()
    install_requirements()
    repair_import_error_pandas_ta()
    input()
import sys
import os
import platform
import subprocess


def create_venv():
    """ Create virtual environment (venv) if it does not exist
    """
    print('1) Virtual Environment ...')
    if not os.path.exists('.venv'):
        print('Create virtual environment (venv) ...')
        print('python -m venv .venv') # command in terminal
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
    else:
        print('Virtual environment (venv) already exists')
    print('\n')


def install_requirements():
    """ Install requirements.txt
    """
    print('2) Install (only missing) libraries from requirements.txt ...')
    # Path to pip from venv (not global)
    if platform.system() == 'Windows':
        venv_pip = '.venv/Scripts/pip.exe'
    elif platform.system() == 'Linux':
        venv_pip = '.venv/bin/pip'
    else:
        print(f'Platform not supported: "{platform.system()}"')
        return
    print('pip install -r requirements.txt') # command in terminal
    subprocess.run([venv_pip, 'install', '-r', 'requirements.txt'], check=True)
    print('\n')


from pathlib import Path
def repair_import_error_pandas_ta():
    """ Fixes the import error from the lib pandas_ta
    file: .venv/Lib/site-packages/pandas_ta/momentum/squeeze_pro.py
      line 2: replace `from numpy import NaN as npNaN` with `from numpy import nan as npNaN`
    """
    print('3) Fix pandas_ta import error (NaN to nan) ...')

    # Path to the file with import errors: squeeze_pro.py
    if platform.system() == 'Windows':
        file_path = Path(__file__).parent / '.venv/Lib/site-packages/pandas_ta/momentum/squeeze_pro.py'
    elif platform.system() == 'Linux':
        file_path = Path(__file__).parent / '.venv/lib/python3.11/site-packages/pandas_ta/momentum/squeeze_pro.py'
    else:
        print(f'Platform not supported: "{platform.system()}"')
        return

    target_string = 'from numpy import NaN as npNaN'        # wrong import
    replacement_string = 'from numpy import nan as npNaN'   # fixed import

    if not file_path.exists():
        raise ValueError(f'file path {file_path} does not exist - there was a problem installing the libraries from requirements.txt (probably global and not in the .venv folder)')

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if len(lines) <= 2:
        raise ValueError(f'There was a problem with the file squeeze_pro.py: \n{"\n".join(lines)}')
    if lines[1].strip() == target_string:
        lines[1] = replacement_string + '\n'
        # Replace line with fixed line
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
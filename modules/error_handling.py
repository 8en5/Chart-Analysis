import traceback
import json
import pandas as pd
from pathlib import Path

from modules.file_handler import get_path, create_dir


errors = []

def log_error(error:Exception, save=True, file_path:Path=None):
    # Error info in log
    error_info = {
        'date': pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S"),
        'type': type(error).__name__,
        'message': str(error),
        'traceback': traceback.format_exc(),
        'count': 1
    }

    # Print Error (full if new, else short)
    new = True
    log_message = 'ERROR'
    for e in errors:
        if e['message'] == error_info['message']:
            e['count'] += 1
            new = False
            log_message = f"{error_info['type']}: {error_info['message']}"
            break
    if new:
        errors.append(error_info)
        log_message = f"{error_info['type']}: {error_info['message']}\n{error_info['traceback']}\n"
    print(log_message)

    if save:
        save_errors(file_path)


def save_errors(folder:Path=None):
    # Folder and file name
    if not folder:
        # Default folder
        folder = get_path() / 'data'

    file_name = f'error_log.txt'
    file_path = folder / file_name
    create_dir(folder)

    # Print and save message
    with open(file_path, 'w') as file:
        for e in errors:
            error_str = json.dumps(e, indent=4)
            #print(error_str)
            file.write(error_str)
            file.write('\n\n')
            file.write(e['traceback'])
            file.write('\n\n\n')
            file.write('-'*100)
            file.write('\n\n\n')
        file.close()
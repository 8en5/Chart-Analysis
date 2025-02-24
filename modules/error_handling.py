import logging
import traceback
from datetime import datetime
import json
import re
import pandas as pd

from modules.file_handler import get_path, create_dir


KNOWN_ERRORS = [
    # Crypto Compare Api
    'CCCAGG market does not exist for this coin pair',  # Coin par is invalid (symbol to USD)
    'limit is smaller than min value.'                  # if limit = 0
]


# Config logger
folder = get_path() / 'data/errors'
create_dir(folder)
logging.basicConfig(
    filename = folder / '_error_log.txt',
    level = logging.ERROR,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

class ErrorHandling:

    def __init__(self):
        self.new_errors = []
        self.group_errors = {
            'new_errors': {},
            'known_errors': {}
        }


    def log_error(self, error: Exception, grouping=''):
        error_msg = str(error)
        print(error_msg)

        # Append Error for grouping
        known = False
        for known_error in KNOWN_ERRORS:
            if known_error in error_msg:
                # Append Error to the dict 'known_errors'
                if known_error in self.group_errors['known_errors']:
                    self.group_errors['known_errors'][known_error].append(grouping)
                else:
                    self.group_errors['known_errors'][known_error] = [grouping]
                known = True
                break

        # Log Error if not known
        if not known:
            # Append Error to dict 'new_errors'
            if error_msg in self.group_errors['new_errors']:
                self.group_errors['new_errors'][error_msg].append(grouping)
            else:
                self.group_errors['new_errors'][error_msg] = [grouping]

            # Error info in live log
            error_info = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
            self.new_errors.append(error_info)

            # Log the new error
            log_message = f'{error_info['type']}: {error_info['message']}\n{error_info['traceback']}\n'
            logging.error(log_message)


    def save_summary(self, file_name=None):
        if len(self.group_errors['known_errors']) == 0 and len(self.group_errors['new_errors']) == 0:
            # no Errors
            return

        # Prepare output format (list without new line - basic json.dump makes many line breaks
        output = json.dumps(self.group_errors, indent=4)
        output = re.sub(r'",\s+', '", ', output) # https://stackoverflow.com/questions/48969984/python-json-dump-how-to-make-inner-array-in-one-line

        # Print in Terminal
        print('\n')
        print('-' * 70)
        print('Error evaluation:', '\n')
        print(output)

        # Save Errors in Log file
        if not file_name:
            file_name = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = get_path() / 'data/errors' / f'{file_name}.txt'
        with file_path.open('w', encoding='utf-8') as f:
            f.write(output)
        print(f'Save Error-Log in {file_path}')

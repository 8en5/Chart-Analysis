import traceback
import json
import pandas as pd

from modules.file_handler import get_path, create_dir



class ErrorHandling:

    def __init__(self):
        self.errors = []

        # Save file
        folder = get_path() / 'data/errors'
        create_dir(folder)
        file_name = f'error_log_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        self.file_path = folder / file_name


    def log_error(self, error:Exception, save=True):
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
        for e in self.errors:
            if e['message'] == error_info['message']:
                e['count'] += 1
                new = False
                log_message = f"{error_info['type']}: {error_info['message']}"
                break
        if new:
            self.errors.append(error_info)
            log_message = f"{error_info['type']}: {error_info['message']}\n{error_info['traceback']}\n"
        print(log_message)

        if save:
            self.save_errors()


    def save_errors(self):
        # Print and save message
        with open(self.file_path, 'w') as file:
            for e in self.errors:
                error_str = json.dumps(e, indent=4)
                #print(error_str)
                file.write(error_str)
                file.write('\n\n')
                file.write(e['traceback'])
                file.write('\n\n\n')
                file.write('-'*100)
                file.write('\n\n\n')
            file.close()
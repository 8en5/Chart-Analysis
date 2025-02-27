"""
Copy defined courses (from api download) to specific folders (stages)
  so that different courses can be analysed in the big meta parameter study
"""

import shutil

from modules.file_handler import *


stages_dict = {
    'crypto_stage1': ['ADA', 'BTC', 'ETH', 'LINK']
}


def copy_file_to_folder(source_file, destination_folder):
    """ Copy file to folder
    :param source_file: file
    :param destination_folder: folder
    """
    # Absolute file paths
    source_path = Path(source_file)
    destination_path = Path(destination_folder) / source_path.name  # Folder + copy filename
    create_dir(destination_folder)  # create folder if folder does not exist

    # Check if both paths are in the workspace
    ws = get_path()
    if not source_path.is_relative_to(ws) or not destination_path.is_relative_to(ws):
        raise AssertionError(f'Folder {source_path} or {destination_path} is not in workspace {ws}')

    # Check if file available
    if not source_path.is_file():
        print(f'Path "{source_path}" is not a valid file')
        return

    # Copy
    shutil.copy2(source_path, destination_path)

    # Print (relative file paths)
    #print(f'Copy \t "{get_relative_folder(source_path)}" \t to \t "{get_relative_folder(destination_path)}"')



def _routine_copy_stage(symbols, folder):
    """ Routine to copy all symbols to a one folder (stage)
    :param symbols: list of symbols
    :param folder: folder_path stage
    """
    print(f'Copy to folder "{get_relative_folder(folder)}": {symbols}')
    for index, symbol in enumerate(symbols):
        #print(f'{index+1}/{len(symbols)}: {symbol}')
        file_path = find_file_in_directory(get_path('course_cc'), symbol)
        copy_file_to_folder(file_path, folder)



def routine_loop_stages():
    """ Main routine to loop over all stages and copy them to the new folders
    """
    for index, (key, value) in enumerate(stages_dict.items()):
        print(f'{index+1}/{len(stages_dict)}: Stage "{key}"')
        folder_path = get_path() / 'data/course' / key
        _routine_copy_stage(value, folder_path)


if __name__ == "__main__":
    routine_loop_stages()
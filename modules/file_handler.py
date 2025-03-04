
from pathlib import Path
import matplotlib.pyplot as plt

from modules.utils import *


def get_path(key:str='ws') -> Path:
    # Calculate workspace
    current_path = Path(__file__).resolve()   # location of this file
    workspace_path = current_path.parents[1]  # "../../"

    folder_dict = {
        'ws': workspace_path,
        'course_cc': workspace_path / "data/course/crypto_compare",
        'analyse_cc': workspace_path / "data/analyse/crypto_compare",
    }

    if key not in folder_dict:
        raise KeyError(f'Key "{key}" not in folder_dict "{list(folder_dict.keys())}"')

    return folder_dict[key]


def create_dir(folder_path:Path) -> None:
    folder_path = Path(folder_path)  # Make sure path is a Path object
    if folder_path.exists():
        # Folder exists
        #print(f'Folder "{folder_path}" exists')
        return
    else:
        # Folder doesn't exist
        # Create folder only, if folder in workspace
        workspace_path = get_path('ws')
        if not folder_path.is_relative_to(workspace_path):
            raise AssertionError(f'Folder {folder_path} not in workspace {workspace_path}')

        # Folder doesn't exists, create folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f'Make directory {folder_path}')


def get_relative_folder(folder_path:Path) -> Path:
    """ Return relative folder path to workspace
    :param folder_path: e.g. C:/Users/bense/PycharmProjects/Chart-Analysis/data/course/cryptocompare/api
    :return: relative folder path - e.g. data/course/cryptocompare/api
    """
    folder_path = Path(folder_path)  # Make sure path is a Path object
    ws = get_path()
    folder_rel = folder_path.relative_to(ws)
    return folder_rel



def find_file_in_directory(folder_path:Path, filename:str) -> Path:
    """ Find file in directory
    :param folder_path: folder
    :param filename: name (extension doesn't matter)
    :return: founded file path in the folder (else raise Error)
    """
    folder_path = Path(folder_path)         # Make sure path is a Path object
    found_files = [file for file in folder_path.rglob('*') if file.name == filename or file.stem == filename]

    # Evaluate search
    if not found_files:
        raise FileNotFoundError(f'File "{filename}" not found in directory "{folder_path}"')
    if len(found_files) > 1:
        raise ValueError(f'Multiple files named "{filename}" found in directory "{folder_path}": {found_files}')

    return found_files[0]


def find_files_in_directory(folder_path:Path, filename_list:list) -> list[Path]:
    """ Check if a list of files are all in directory, then return True (else False)
    :param folder_path: folder
    :param filename_list: name (extension doesn't matter)
    :return: list of all founded file paths
    """
    found_file_paths = []
    for filename in filename_list:
        found_file_paths.append(find_file_in_directory(folder_path, filename))
    return found_file_paths


def list_file_paths_in_folder(folder_path:Path, filter:str='') -> list[Path]:
    """ list of all relative file paths in folder
    :param folder_path: Directory (Path)
    :param filter: filter criteria (e.g. '.csv')
    :return: [], list of all files in path
    """
    folder_path = Path(folder_path)         # Make sure path is a Path object
    # Check, if folder_path is valid
    if not folder_path.exists():
        raise FileNotFoundError(f'Folder "{folder_path}" does not exist')

    # Return all files in folder
    file_paths = []
    for file in folder_path.iterdir():
        if file.is_file() and filter in file.name:
            file_paths.append(file)
    #print(filepaths)
    return file_paths


def get_file_in_folder(folder_path:Path, file_name:str) -> Path | None:
    """ Returns file path if file exists in folder.
    :param folder_path: Directory (Path)
    :param file_name: Name of the file to search for
    :return: Path of the file if found, else None
    """
    # If folder does not exist, there are no existing files
    if not folder_path.exists():
        return None

    # Search if file exists in folder
    for file_path in list_file_paths_in_folder(folder_path):
        if file_name in file_path.stem:
            return file_path

    return None


def load_pandas_from_symbol(symbol:str) -> pd.DataFrame:
    # Find file path from symbol in folder
    folder_path = get_path('course_cc')
    file_name = f'{symbol}.csv'
    file_path = find_file_in_directory(folder_path, file_name)

    return load_pandas_from_file_path(file_path)


def load_pandas_from_file_path(file_path:Path):
    if not file_path.exists():
        raise FileNotFoundError(f'File "{file_path}" does not exist')

    # load data in pandas frame
    df = pd.read_csv(file_path)

    # Prepare df
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    # print(df.dtypes)

    return df


def save_pandas_to_file(df:pd.DataFrame, folder_path:Path, name:str, extension:str='csv') -> None:
    """ Saves a Pandas DataFrame to a file.
    :param df: Pandas DataFrame to save
    :param folder_path: Directory where the file should be saved
    :param name: File name without extension
    :param extension: File extension (default: 'csv')
    """
    folder_path = Path(folder_path)  # Make sure path is a Path object

    # Create folder if it doesn't exist
    create_dir(folder_path)

    # Calculate absolute file path
    file_name = f'{name}.{extension}'
    file_path = folder_path / file_name

    # Calculate relative path from workspace
    ws_folder = get_path('ws')
    relative_folder = file_path.relative_to(ws_folder) if file_path.is_relative_to(ws_folder) else file_path

    # Save file
    df.to_csv(file_path)
    print(f'Saved {file_name} to {relative_folder}')


def save_matplotlib_figure(fig:plt.Figure, folder_path:Path, name:str, extension:str='png') -> None:
    """ Saves a Matplotlib figure to a file.
    :param fig: Matplotlib figure to save
    :param folder_path: Directory where the figure should be saved
    :param name: File name without extension
    :param extension: File format (default: 'png')
    """
    folder_path = Path(folder_path)  # Make sure path is a Path object

    # Create folder if it doesn't exist
    create_dir(folder_path)

    # Calculate absolute file path
    file_name = f'{name}.{extension}'
    file_path = folder_path / file_name

    # Check if file exists, and append a number if it does
    """
    counter = 1
    while file_path.exists():
        # Create new file name with a number appended
        file_name = f'{name}_{counter}.{extension}'
        file_path = folder_path / file_name
        counter += 1
    """

    # Calculate relative path from workspace
    ws_folder = get_path('ws')
    relative_folder = file_path.relative_to(ws_folder) if file_path.is_relative_to(ws_folder) else file_path

    # Save figure
    fig.set_size_inches((8, 6))
    fig.savefig(file_path, format=extension, dpi=300)
    print(f'Saved {file_name} to {relative_folder}')

from pathlib import Path
import matplotlib.pyplot as plt
import yaml

from modules.utils import *


def get_path(key:str='ws') -> Path:
    """ Return selected paths to important folders or files
    :param key: key for the specific path
    :return:
    """
    # Calculate workspace
    current_path = Path(__file__).resolve()   # location of this file
    workspace_path = current_path.parents[1]  # "../../"

    folder_dict = {
        # Folders
        'ws': workspace_path,
        'cc': workspace_path / 'data/course/crypto_compare',

        # Files
        'cc_symbols_api_csv': workspace_path / 'data/course/crypto_compare/cc_symbols_api.csv',
        'course_selection_yaml': workspace_path / 'modules/input_files/course_selection.yaml',
        'indicator_params_yaml': workspace_path / 'modules/input_files/indicator_params.yaml',
    }

    if key not in folder_dict:
        raise KeyError(f'Key "{key}" not in folder_dict "{list(folder_dict.keys())}"')

    return folder_dict[key]


def get_last_created_folder_in_dir(dir_path) -> Path:
    """ Returns the latest created folder in a directory (without recursive, only this dir)
    :param dir_path: folder_path
    :return: Path of the latest created folder (raise Error if there is no folder)
    """
    dir_path = Path(dir_path)  # Make sure path is a Path object
    # Check folder exists and folder is a folder
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f'Folder "{dir_path}" does not exist')
    # List of all folders in the directory
    folders = [f for f in dir_path.iterdir() if f.is_dir()]
    if not folders:
        raise AssertionError(f'Folder "{dir_path} has no subfolders')
    # Find the folder with the most recent creation time
    latest_folder = max(folders, key=lambda f: f.stat().st_ctime)
    return latest_folder


def create_dir(folder_path:Path) -> None:
    """ Create folder, if folder does not exist
    Folder must be in the workspace
    :param folder_path: directory (which should be created)
    """
    folder_path = Path(folder_path)  # Make sure path is a Path object
    if folder_path.exists():
        # Folder exists
        #print(f'Folder "{folder_path}" exists')
        return
    else:
        # Folder doesn't exist
        # Create folder only, if folder is in workspace
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


#---------------------- Files and names in directory ----------------------#
def get_file_in_directory(folder_path:Path, filename:str, extension=None) -> Path:
    """ Find file in directory
    :param folder_path: folder
    :param filename: name (extension doesn't matter)
    :param extension: file extension (csv, txt, png)
    :return: founded file path in the folder (else raise Error)
    """
    folder_path = Path(folder_path)         # Make sure path is a Path object
    if extension:  # If an extension is provided, add it to the filename
        search_pattern = f'{filename}.{extension}'
        found_files = [file for file in folder_path.rglob('*') if file.name == search_pattern and file.is_file()]
    else:  # Search by name only, ignoring extension
        found_files = [file for file in folder_path.rglob('*') if file.stem == filename and file.is_file()]

    # Evaluate search
    if not found_files:
        raise FileNotFoundError(f'File "{filename}" not found in directory "{folder_path}"')
    if len(found_files) > 1:
        raise ValueError(f'Multiple files named "{filename}" found in directory "{folder_path}": {found_files}')

    return found_files[0]


def founded_files_in_directory(folder_path:Path, filename_list:list, extension=None) -> tuple[list[Path],list[Path]]:
    """ Return tuple of files, which are found in workspace and which are not
    :param folder_path: folder
    :param filename_list: name (extension doesn't matter)
    :param extension: file extension (csv, txt, png)
    :return: tuple(paths_available, paths_unavailable)
    """
    file_paths_positive = []
    file_paths_negative = []
    for filename in filename_list:
        try:
            file_paths_positive.append(get_file_in_directory(folder_path, filename, extension))
        except FileNotFoundError:
            # Run into Error, but it is ok -> file not found
            file_paths_negative.append(filename)
    return file_paths_positive, file_paths_negative


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


def get_names_from_paths(list_file_paths:list) -> list[str]:
    """ Return list of file names based on a list of file paths
    :param list_file_paths: list of file paths
    :return: list of file names
    """
    return [Path(path).stem for path in list_file_paths]


#---------------------- Pandas ----------------------#
def load_pandas_from_symbol(symbol:str) -> pd.DataFrame:
    # Find file path from symbol in folder
    folder_path = get_path('cc')
    file_name = f'{symbol}.csv'
    file_path = get_file_in_directory(folder_path, file_name)

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
    df.to_csv(file_path, float_format='%.3f')
    print(f'Saved {file_name} to {relative_folder}')


#---------------------- Matplotlib ----------------------#
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


#---------------------- Yaml ----------------------#
def load_yaml_from_file_path(file_path:Path) -> dict:
    file_path = Path(file_path)  # Make sure path is a Path object
    # Check, if folder_path is valid
    if not file_path.exists():
        raise FileNotFoundError(f'File "{file_path}" does not exist')

    with file_path.open('r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data
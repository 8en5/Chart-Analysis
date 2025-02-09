
from modules.utils import *


def get_path(key='ws'):
    # Calculate workspace
    current_path = os.path.abspath(__file__)
    workspace_path = os.path.abspath(os.path.join(current_path, '../../'))
    folder_dict = {
        'ws': str(workspace_path),
        'course_cc': r'data\course\crypto_compare',
        'analyse_cc': r'data\analyse\crypto_compare',
    }
    if not key in folder_dict:
        raise KeyError(f'Key "{key}" not in folder_dict "{list(folder_dict.keys())}"')

    if key == 'ws':
        return folder_dict[key]

    target_dir = str(os.path.join(workspace_path, folder_dict[key]))
    return target_dir


def create_dir(folder_path:str):
    if os.path.exists(folder_path):
        # Folder exists
        return
    else:
        # Create folder only, if folder in workspace
        workspace_path = get_path('ws')
        if workspace_path not in folder_path:
            print(f'Warning: Folder {folder_path} not in workspace {workspace_path}')
            exit()

        # Folder doesn't exists, create folder
        os.makedirs(folder_path)
        print(f'Make directory {folder_path}')


def find_file_in_directory(folder_path, filename):
    for root, dirs, files in os.walk(folder_path):
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFoundError(f'File "{filename} not in directory "{folder_path}"')


def get_filename_from_path(file_path: str):
    return os.path.splitext(os.path.basename(file_path))[0]


def list_file_paths_in_folder(folder_path:str, filter=''):
    """ list of all relative file paths in folder
    :param folder_path: dir
    :param filter: filter criteria (e.g. '.csv')
    :return: [], list of files in path
    """
    # Check, if folder_path is valid
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f'Folder "{folder_path}" does not exist')

    # Return all files in folder
    file_paths = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path): # file
            if filter in file_path:
                file_paths.append(file_path)
        else: # folder
            pass
    #print(filepaths)
    return file_paths


def get_file_names_in_folder(folder_path:str):
    list_file_paths = list_file_paths_in_folder(folder_path)
    list_file_paths = list(map(get_filename_from_path, list_file_paths))
    return list_file_paths


def get_file_in_folder(folder_path, file_name):
    """ Returns filepath if file in folder
    :param folder_path: directory
    :param file_name: name
    :return: file path if file found | else None
    """
    # If folder does not exist, there are no existing files
    if not os.path.exists(folder_path):
        return None
    # Search if file exists in folder
    for file_path in list_file_paths_in_folder(folder_path):
        if file_name in get_filename_from_path(file_path):
            return file_path
    return None


def load_pandas_from_symbol(symbol:str):
    # Find file path from symbol in folder
    folder_path = get_path('course_cc')
    file_name = f'{symbol}.csv'
    file_path = str(find_file_in_directory(folder_path, file_name))

    return load_pandas_from_file_path(file_path)


def load_pandas_from_file_path(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File "{file_path}" does not exist')

    # load data in pandas frame
    df = pd.read_csv(file_path)

    # Prepare df
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    # print(df.dtypes)

    return df


def save_pandas_to_file(df:pd.DataFrame, folder_path:str, name:str, extension:str='csv'):
    # Create folder, if folder doesn't exists
    create_dir(folder_path)

    # Calculate relative path from ws
    ws_folder = get_path('ws')
    relative_folder = folder_path.split(ws_folder)[-1]

    # Calculate absolute path
    file_name = f'{name}.{extension}'
    file_path = str(os.path.join(folder_path, file_name))
    #print(file_path)

    # Save file
    df.to_csv(file_path)
    print(f'Save {file_name} to relative folder {relative_folder}')


def save_matplotlib_figure(fig, folder_path:str, name:str, extension='png'):
    # Create folder, if folder doesn't exists
    create_dir(folder_path)

    # Calculate relative path from ws
    ws_folder = get_path('ws')
    relative_folder = folder_path.split(ws_folder)[-1]

    # Calculate absolute path
    file_name = f'{name}.{extension}'
    file_path = str(os.path.join(folder_path, file_name))
    #print(file_path)

    # Save figure
    fig.set_size_inches((8,6))
    fig.savefig(file_path, format=extension, dpi=300)
    print(f'Save {file_name} to relative folder {relative_folder}')
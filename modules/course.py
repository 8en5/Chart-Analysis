
from pathlib import Path
import yaml

from modules.file_handler import *


def get_symbols_from_api_csv(n=None, asset_type=None, order=0):
    """
    :param n: amount of symbols
    :param asset_type: [BLOCKCHAIN, TOKEN, FIAT, INDEX]
    :param order: [0 - default, 1 - newest, 2 - oldest]
    :return: list of symbols
    """
    if n is None:
        n = -1 # all data

    # Load api csv with symbols
    folder_path = get_path('course_cc')
    file_name = 'cc_symbols_api.csv'
    file_path = folder_path / file_name
    if not file_path.exists():
        raise FileNotFoundError(f'File "{file_name}" does not exist -> run cc_load_symbols.py')
    df = pd.read_csv(file_path)
    if n > len(df)-2:
        n = -1

    # Prepare df
    df['date'] = pd.to_datetime(df['LAUNCH_DATE'], unit='s')
    if asset_type:
        allowed_asset_type = ['BLOCKCHAIN', 'TOKEN', 'FIAT', 'INDEX']
        if asset_type not in allowed_asset_type:
            raise ValueError(f'Asset type "{asset_type}" not in {allowed_asset_type}')
        df = df[df['ASSET_TYPE'] == asset_type]                  # e.g. only BLOCKCHAIN (or TOKEN, INDEX, ...)

    match order:
        case 0:                 # default order
            df = df.iloc[0:n]
        case 1:                 # newest
            df = df.nlargest(n, 'date')
        case 2:                 # oldest
            df = df.nsmallest(n, 'date')
        case _:
            raise ValueError(f'order between [0-2]: {order}')
    # Return
    return df['SYMBOL'].tolist()


def get_symbols_list_from_yaml(key='default'):
    """ Load defined symbols from yaml
    :param key: key for different course selections in the yaml file
    :return: list of symbols
    """
    # Load yaml with symbols
    file_name = 'input_files/course_selection.yaml'
    file_path = Path(__file__).parent / file_name
    with file_path.open('r', encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if key not in data:
        raise ValueError(f'Key {key} not in yaml: {data.keys}')

    course_selection = data[key]
    return course_selection


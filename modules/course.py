
from pathlib import Path
import yaml
from scipy.constants import value

from modules.file_handler import *
from modules.api.crypto_compare.download_csv_symbols import main_routine_download_available_symbols
from modules.api.crypto_compare.download_courses import main_routine_download_course_list_cc


#---------------------- Crypto Compare ----------------------#

def get_available_symbols_cc() -> pd.DataFrame:
    """ Load api csv with all available symbols in Crypto Compare
    :return: df with all symbols
    """
    # Folder path
    folder_path = get_path('course_cc')
    file_name = 'cc_symbols_api.csv'
    file_path = folder_path / file_name
    if not file_path.exists():
        # Download file
        print(f'File "{file_name}" with available symbols in CryptoCompare does not exist')
        print('Start downloading ...')
        main_routine_download_available_symbols()

    # Load csv as pandas frame
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['LAUNCH_DATE'], unit='s')
    return df


def get_symbols_list_from_api_csv_cc(n=None, asset_type=None, order=0):
    """
    :param n: amount of symbols
    :param asset_type: [BLOCKCHAIN, TOKEN, FIAT, INDEX]
    :param order: [0 - default, 1 - newest, 2 - oldest]
    :return: list of symbols
    """
    if n is None:
        n = -1 # all data

    # Load available symbols
    df = get_available_symbols_cc()
    if n > len(df)-2:
        n = -1

    # Specify asset type
    if asset_type:
        allowed_asset_type = ['BLOCKCHAIN', 'TOKEN', 'FIAT', 'INDEX']
        if asset_type not in allowed_asset_type:
            raise ValueError(f'Asset type "{asset_type}" not in {allowed_asset_type}')
        df = df[df['ASSET_TYPE'] == asset_type]                  # e.g. only BLOCKCHAIN (or TOKEN, INDEX, ...)

    # Specify order for downloading
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



#---------------------- All courses ----------------------#

def get_hits_symbols_in_csv(key_api:str, list_symbols:list):
    """ List of the given symbols, which are in the csv
    :param key_api: [cc]
    :param list_symbols: symbols input (see which of them are included in the csv)
    :return: list of symbols defined in the csv
    """
    if key_api == 'cc':
        # Get a list of all symbols from list_symbols, which are from crypto_compare
        df_symbols_cc = get_available_symbols_cc()
        df_found = df_symbols_cc[df_symbols_cc['SYMBOL'].isin(list_symbols)]
        return list(df_found['SYMBOL'])


def get_file_paths_of_course_selection(key_course_selection='default') -> list[Path]:
    """ Get all file paths from the selected symbols from yaml
    :param key_course_selection: key for different course selections in the yaml file
    :return: if all symbols found list of paths, else raise Error
    """
    # Load yaml with course selection (symbols)
    file_name = 'input_files/course_selection.yaml'
    file_path = Path(__file__).parent / file_name
    with file_path.open('r', encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Check key
    if key_course_selection not in data:
        raise ValueError(f'course_selection {key_course_selection} not in yaml: {data.keys}')

    # Get course selection from yaml
    course_selection_symbols = data[key_course_selection]

    # Make sure all selected courses are in the directory
    folder_courses = get_path() / 'data/course'
    try:
        return find_files_in_directory(folder_courses, course_selection_symbols)
    except FileNotFoundError: # Run into Error, but it is ok
        # Some selected courses are not available
        print(f'Some selected courses are not downloaded -> update all courses')
        download_course_list(course_selection_symbols)
        return find_files_in_directory(folder_courses, course_selection_symbols)


def download_course_list(symbols:list):
    """ Download all symbols (different APIs possible)
    :param symbols: list of symbols to download
    """

    # Download (ore update) all selected courses
    # CryptCompare
    list_symbols_cc = get_hits_symbols_in_csv('cc', symbols)
    main_routine_download_course_list_cc(list_symbols_cc)

    # Check, that now all courses are downloaded
    try:
        folder_courses = get_path() / 'data/course'
        find_files_in_directory(folder_courses, symbols)
    except FileNotFoundError:
        print(f'Error: Not all symbols are downloaded')


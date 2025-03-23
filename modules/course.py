
from modules.file_handler import *
from modules.api.crypto_compare.download_csv_symbols import main_routine_download_available_symbols_cc
from modules.api.crypto_compare.download_courses import main_routine_download_course_list_cc



def get_course_selection_from_yaml(key_course_selection='default') -> list[str]:
    """ Get the symbol names by a key from the yaml
    :param key_course_selection: key for different course selections in the yaml file
    :return: if all symbols found list of paths, else raise Error
    """
    # Load yaml with course selection (symbols)
    file_path = get_path('course_selection_yaml')
    data = load_yaml_from_file_path(file_path)

    # Check key
    if key_course_selection not in data:
        raise ValueError(f'course_selection {key_course_selection} not in yaml: {data.keys}')

    # Get course selection from yaml
    course_selection_symbols = data[key_course_selection]
    if isinstance(course_selection_symbols, str):
        course_selection_symbols = [course_selection_symbols]
    return course_selection_symbols


#---------------------- All courses ----------------------#

def get_courses_paths(source_courses:str|list[str]) -> list:
    """ Central function to get a list of symbol file paths
    Get the file_paths either from the course_selection_key via yaml or a list of symbol names
    This function checks, if the requests symbols are already downloaded. If not, download it

    :param source_courses: multiple sources possible: course_selection_key / list symbol_names
    :return: list of symbol file paths

    e.g.
      1 get_courses_paths('default')               -> Path[ADA, BTC, ETH, LINK] (defined in the yaml)
      2 get_courses_paths('BTC')                   -> Path[BTC]
      3 get_courses_paths(['BTC', 'ETH', 'SOL'])   -> Path[BTC, ETH, SOL]
      4 get_courses_paths(['../data/../BTC.csv'])  -> Path[BTC, ETH, SOL]
    """
    # Get list of symbols based on different sources
    if isinstance(source_courses, str):
        try:
            # 1 - source_courses = course_selection_key -> load symbols defined in the yaml
            symbol_names = get_course_selection_from_yaml(source_courses)
        except ValueError:
            # Run into Error, but it is ok (source_courses was not a course_selection_key)
            # 2 - convert one given course to a list - e.g. 'BTC' -> ['BTC']
            symbol_names = [source_courses]
    elif isinstance(source_courses, list):
        if isinstance(source_courses[0], str):
            # 3 - source_courses = list[symbol_names] -> already list of symbol names
            symbol_names = source_courses
        elif isinstance(source_courses[0], Path):
            # 4 - source_courses = list[Path]
            symbol_names = get_names_from_paths(source_courses)
        else:
            raise ValueError(f'Wrong instance, should be str or Path: {source_courses}')
    else:
        raise ValueError(f'Wrong instance, should be str or list: {source_courses}')


    # Check if all courses are already downloaded
    paths_pos, names_neg = founded_files_in_directory(get_path(), symbol_names, 'csv')
    if len(names_neg) == 0:
        # all courses already downloaded
        return paths_pos

    # Download courses
    download_courses(symbol_names, False) # [update=True to update all, update=False to download only missing courses]

    # Check, if all courses are now downloaded
    paths_pos, names_neg = founded_files_in_directory(get_path(), symbol_names, 'csv')
    if len(names_neg) == 0:
        return paths_pos
    else:
        raise AssertionError(f'Here is a problem: Not all courses are downloaded, but they should be: "{names_neg}"')


def download_courses(symbol_names:list, update=False) -> None:
    """ Ensures that all courses are downloaded
    Download all courses (from different APIs) if not already downloaded
    If a given symbol name is not available in any API then throw an Error

    :param symbol_names: list of symbol names
    :param update: whether an already downloaded course should be updated
    :return: None
    """
    # Check that all symbols can be downloaded via some API
    # (currently only one API - CC)
    pos_cc, neg_cc = symbols_available_for_cc(symbol_names)
    if len(neg_cc) > 0:
        raise ValueError(f'Not all symbols can be downloaded via the API: {neg_cc}')

    # Download symbols
    # (currently only one API - CC)
    if update:
        # Update all courses (regardless of whether they were downloaded in the past) -> All courses are then up to date
        print('Update or download all needed courses')
        main_routine_download_course_list_cc(symbol_names)
    else:
        # Download only missing courses -> newly downloaded courses may have more data than already downloaded courses
        paths_pos, names_neg = founded_files_in_directory(get_path(), symbol_names, 'csv')
        if len(names_neg) > 0:
            print('Download only missing courses ...')
            main_routine_download_course_list_cc(names_neg)
        else:
            print('All courses already available')



#---------------------- Crypto Compare ----------------------#

def get_csv_cc() -> pd.DataFrame:
    """ Returns the csv with available symbols from CryptoCompare
    :return: df with information to the symbols available on CryptoCompare
    """
    # Download csv, if not available
    file_path = get_path('cc_symbols_api_csv')
    if not file_path.exists():
        # Download file
        print(f'CSV file from CryptoCompare with all available symbols does not exist')
        print('Start downloading ...')
        main_routine_download_available_symbols_cc()

    # Load csv as pandas frame
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['LAUNCH_DATE'], unit='s')
    return df


def symbols_available_for_cc(list_symbol_names) -> tuple[list, list]:
    """ Return tuple of symbols, which are available in CC and which are not
    Load api csv with all available symbols in Crypto Compare
    :return: tuple([available], [not available])

    Input: ['BTC', 'ETH', 'test']
    Output: (['ETH', 'BTC'], ['test'])
    """
    # Load csv with available symbols as list
    list_available_symbols = get_csv_cc()['SYMBOL'].tolist()
    # Symbols found in csv (available in the CC API)
    symbols_positive = list(set(list_available_symbols) & set(list_symbol_names)) # & -> elements in both lists
    # Symbols not in csv (not available in the CC API)
    symbols_negative = list(set(list_symbol_names) - set(symbols_positive)) # - -> elements in list_symbol names which are not in symbols_positive
    return symbols_positive, symbols_negative


def get_symbols_list_from_api_csv_cc(n=None, asset_type=None, order=0) -> list[str]:
    """ Return list of symbols from CC (controllable with amount, asset_type and order)
    :param n: amount of symbols
    :param asset_type: [BLOCKCHAIN, TOKEN, FIAT, INDEX]
    :param order: [0 - default, 1 - newest, 2 - oldest]
    :return: list of symbols
    """
    if n is None:
        n = -1 # all data

    # Load available symbols
    df = get_csv_cc()
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



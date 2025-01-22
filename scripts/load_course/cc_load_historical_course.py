import requests
import yaml

from modules.file_handler import *

sys.path.append(r'C:\Users\bense\PycharmProjects\Chart-Analysis') # to run py-file in separate cmd


def request_course(symbol:str, to_ts=None, limit=2000):
    """ API request to get historical course data for a symbol from CryptoCompare
    :param symbol: Cryptocurrency symbol (e.g., 'BTC')
    :param to_ts: time in seconds - last day in df (if to_ts=None download until today)
    :param limit: specifies how much data is requested, max 2000 data points per API call
    :return: df with historical course data for the symbol containing historical data containing to_ts datapoints
    """
    url = 'https://min-api.cryptocompare.com/data/v2/histoday'
    currency = 'USD'
    limit = limit  # 2000 is maximum data points per API request

    # Define API request parameters
    params = {
        'fsym': symbol,  # Cryptocurrency symbol
        'tsym': currency,  # Fiat currency
        'limit': limit,  # Maximum number of data points
        'toTs': to_ts
    }

    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Check for errors in the API response
    if data['Response'] != 'Success':
        raise Exception(f"API Error: {data['Message']}")

    # Convert the data to a DataFrame
    df = pd.DataFrame(data['Data']['Data']) # df = ['time', 'high', 'low', 'open', 'volumefrom', 'volumeto', 'close', 'conversionType', 'conversionSymbol']

    # Add date column YY-mm-ddd
    df['date'] = pd.to_datetime(df['time'], unit='s')
    df = df.set_index('date', drop=True)

    # Prepare df
    df = df.drop(['conversionType', 'conversionSymbol'], axis=1)

    # Print
    #start = df.index.min().strftime('%Y-%m-%d')
    #end = df.index.max().strftime('%Y-%m-%d')
    #print(f'Download {symbol} from {start} to {end}, {len(df)}')
    return df # df = ['time', 'high', 'low', 'open', 'volumefrom', 'volumeto', 'close']


def request_course_full(symbol):
    """ Get all historical course data with multiple requests for a symbol
        Because only 2000 data points can be requested per api call, it must be repeated x times for all data
    :param symbol: symbol (e.g., 'BTC')
    :return: df with historical course data for the symbol containing ALL historical data
    """
    print('<Full>')
    df = None
    to_ts = None
    first_datapoint = False     # True, if first datapoint in df['volumefrom'] is 0, which means no data
    while True:
        # Download 2000 data points
        df_i = request_course(symbol, to_ts)

        # Cut data, if the first course data df['volumefrom'] is 0
        if df_i['volumefrom'].iloc[0] == 0: # first date is 0, when no historical course data is available
            first_datapoint = True

            # Search for the first trading day != 0 and delete every date before
            first_non_zero_index = df_i[df_i['volumefrom'] != 0].index.min()
            df_i = df_i.loc[first_non_zero_index:]
            #print(f'Cut {symbol} - {df_i.index.min().strftime('%Y-%m-%d')}, {len(df_i)}')

        # Combine (merge) all data into one single df
        if df is None:
            df = df_i
        else:
            df = pd.concat([df_i, df], axis=0)

        if first_datapoint: # if first datapoint in df['volumefrom'] was 0, all data is fetched
            return df

        # Calculate new cycle for the next 2000 data points
        to_ts = df['time'].iloc[0] - 60 * 60 * 24


def request_course_update(file_path):
    """ Update the historical course data for a symbol
        This symbol has already been downloaded in the past and now only the days that are missing in the df are requested
    :param file_path: path to the df containing historical course data
    :return:
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File "{file_path}" does not exist')

    # load already existing df from file_path
    df_existing = load_pandas_from_file_path(file_path)
    symbol = get_filename_from_path(file_path)
    #print(df_existing)
    # Calculate amount of days (diff) to download
    n = (pd.Timestamp.today() - df_existing.index[-1]).days - 1
    if n == -1:                     # last_date = today -> no update needed
        print('<Already up to date>')
        return -1
    elif n == 0:                    # special case, 1 day is missing, that means to_ts must be None
        n = None
    # Download new data
    print('<Update>')
    df = request_course(symbol, None, n)
    #print(df)
    # Concat old with new data
    df = pd.concat([df_existing, df], axis=0)
    #print(df)
    return df


def routine_download_course(symbol, folder_path='', update=True):
    """ Routine for downloading symbols (request full or update course data)
    :param symbol: symbol (e.g., 'BTC')
    :param folder_path: folder to save the data
    :param update: bool whether course data is only updated (if available) or downloaded completely
    """
    try:
        if folder_path == '':
            folder_path = get_path('course_cc') # default folder
        if update:
            # Update course data, if available
            if os.path.exists(folder_path):
                # Search for file: if file in folder -> update | else -> download full
                file_path = os.path.join(folder_path, f'{symbol}.csv')
                if file_path in list_file_paths_in_folder(folder_path):
                    df = request_course_update(file_path)
                    if df != -1:
                        save_pandas_to_file(df, folder_path, symbol)
                    return

        # file does not exist or update is false
        df = request_course_full(symbol)
        save_pandas_to_file(df, folder_path, symbol)
        return
    except Exception as e:
        # Error management
        error_msg = str(e)
        # Append Error to error_dict (dict with all Errors and the corresponding symbols
        if error_msg in error_dict:
            error_dict[error_msg].append(symbol)
        else:
            error_dict[error_msg] = [symbol]

        # Known Errors
        known_errors = ['CCCAGG market does not exist for this coin pair',
                        'API Error: limit is smaller than min value.']
        for known_error in known_errors:
            if known_error in str(e):
                print(f'Known Error: {known_error}')
                return
        print(f'New error occurred for symbol "{symbol}": {e}')


def download_manager(source):
    """ Manage downloads from different sources
    :param source: source
    """
    # Check
    allowed_source = ['yaml', 'all', 'new']
    if source not in allowed_source:
        raise ValueError(f'Wrong source: "{source}" not in "{allowed_source}"')

    update = True   # default download type - whether existing courses should be completely downloaded (and overwritten) or updated

    if source == 'yaml':                        # self-defined coins in the yaml
        symbols = load_symbols_from_yaml()
    elif source == 'all':                       # all symbols (from crypto compare api saved in csv)
        symbols = load_symbols_from_api_csv()
    elif source == 'new':                       # newest n symbols (from crypto compare api saved in csv)
        symbols = load_symbols_from_api_csv(20)
    else:
        print(f'Logic Error - download_manager, {source}')
        exit()

    # Storage location
    folder_path = str(os.path.join(get_path('course_cc'), source))

    # Download list
    for index, symbol in enumerate(symbols):
        # Print
        print(f'\r[{index + 1}/{len(symbols)}] - {symbol}')
        # Download each symbol
        routine_download_course(symbol, folder_path, update)
        print()

    # Error Log
    save_errors(folder_path)


def load_symbols_from_yaml():
    """ Load defined symbols from yaml
    :return: list of symbols
    """
    # Load yaml with symbols
    file_path = 'cc_symbols_selected.yaml'
    with open(file_path, 'r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
    symbols = data['active']
    return symbols

def load_symbols_from_api_csv(n=-1):
    """
    :param n: amount of symbols (the n newest ones)
    :return: list of symbols
    """
    # Load api csv with symbols
    folder_path = get_path('course_cc')
    file_name = 'cc_symbols_api.csv'
    file_path = os.path.join(folder_path, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File "{file_name}" does not exist -> run cc_load_symbols.py')
    df = pd.read_csv(file_path)
    if n == -1:
        return df['SYMBOL']
    else:
        df['date'] = pd.to_datetime(df['LAUNCH_DATE'], unit='s')
        #df = df[df['ASSET_TYPE'] == 'BLOCKCHAIN']                  # only BLOCKCHAIN (else TOKEN, INDEX, ...)
        df_newest = df.nlargest(n, 'date')
        return df_newest['SYMBOL'].tolist()


def save_errors(folder_path):
    # Error management
    print('\n')
    print('-' * 70)
    if len(error_dict) > 0:
        print('Error evaluation:', '\n')
    else:
        print('No Errors')

    # Save Errors in Log file
    file_name = '_Error-Log.txt'
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as f:
        for key, value in error_dict.items():
            msg = f'{len(error_dict[key])}x - {key}: {value}'
            print(msg)
            f.write(msg)
    print(f'Save Error-Log in {file_path}')


if __name__ == "__main__":
    error_dict = {}

    # Download historical course data - 4 sources
    #routine_download_course('BTC')     # download 1 hard coded symbol
    download_manager('yaml')            # download from yaml
    #download_manager('all')            # download all symbols (in csv from api call)
    #download_manager('new')            # download the newest symbols (in csv from api call)

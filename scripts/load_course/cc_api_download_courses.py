""" # Aim
Download historical price data from CryptoCompare:
- in an automated and robust manner
- many symbols which are defined in a file
- save the symbols in the same directory

   # Architecture
The api request for Crypto Compare is compact in the first function
Each downloaded symbol is controlled in the object of the class DownloadManagerCC
- symbols can be downloaded completely (via multiple api calls) or updated (if symbol is present in the folder)
- the requested data is saved
- all errors are stored in the class variable error_dict, processed and output at the end
"""

import sys
from pathlib import Path
ws_dir = (Path(__file__).parent / ".." / "..").resolve()  # Workspace
sys.path.insert(0, str(ws_dir))                    # add ws to sys-path to run py-file in separate cmd

import requests
import yaml
import json
import re

from modules.file_handler import *


def API_request_course(symbol:str, to_ts=None, limit=2000):
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
        'fsym': symbol,     # Cryptocurrency symbol
        'tsym': currency,   # Fiat currency
        'limit': limit,     # Maximum number of data points
        'toTs': to_ts       # datetime download until this date
    }

    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Check for errors in the API response
    if data['Response'] != 'Success':
        raise Exception(f'{data['Message']}')

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



class DownloadManagerCC:
    """
    This class manages to download historical course data for a given symbol.
    If self.allow_update = True, then already downloaded symbols will only be updated.
    This class tracks errors across all instances (in class methods). They are categorizing in new and known errors.
    """

    # Class methods concerning all instances
    # Error management across all instances of the class
    error_dict = {
        'new_errors': {},
        'known_errors': {}
    }
    known_errors = ['CCCAGG market does not exist for this coin pair',  # Coin par is invalid (symbol to USD)
                    'limit is smaller than min value.']                 # if limit = 0

    @classmethod
    def _append_error(cls, symbol, error_msg):
        # Decide existing or new error
        for known_error in cls.known_errors:
            if known_error in error_msg:
                if known_error in cls.error_dict['known_errors']:
                    cls.error_dict['known_errors'][known_error].append(symbol)
                else:
                    cls.error_dict['known_errors'][known_error] = [symbol]
                return
        # Append Error to dict
        if error_msg in cls.error_dict['new_errors']:
            cls.error_dict['new_errors'][error_msg].append(symbol)
        else:
            cls.error_dict['new_errors'][error_msg] = [symbol]


    @classmethod
    def show_errors(cls, source):
        # Check if there are Errors
        if len(cls.error_dict['known_errors']) == 0 and len(cls.error_dict['new_errors']) == 0:
            # no Errors
            return

        # Prepare output format (list without new line - basic json.dump makes many line breaks
        output = json.dumps(cls.error_dict, indent=4)
        output = re.sub(r'",\s+', '", ', output) # https://stackoverflow.com/questions/48969984/python-json-dump-how-to-make-inner-array-in-one-line

        # Print in Terminal
        print('\n')
        print('-' * 70)
        print('Error evaluation:', '\n')
        print(output)

        # Save Errors in Log file
        folder_path = get_path('course_cc')
        file_name = f'_Error-Log_{source}.txt'
        file_path = folder_path / file_name
        with file_path.open('w', encoding='utf-8') as f:
            f.write(output)
        print(f'Save Error-Log in {file_path}')


    # Instance methods
    def __init__(self, symbol:str, folder_path:Path):
        self.symbol = symbol                    # symbol
        self.folder_path = Path(folder_path)    # folder to save all symbols

        self.allow_update = True                # bool, whether updates are allowed if file with old data exists (if False, always full download)

        # Initialize variables, value assigned at runtime
        self.df = pd.DataFrame()                # requested data (summarized if multiple requests needed)


    def run(self):
        """ Main routine to download a symbol (request full data or update data)
        """
        try:
            # Check, if data is available for the symbol
            file_path = self.folder_path / f'{self.symbol}.csv'      # Calculate filepath name and check if it exists
            # Get new data - <Update> or <Full>
            if file_path.exists() and self.allow_update:
                # Update data
                self._routine_update_available_course(file_path)
            else:
                # Full data
                self._routine_request_full_course()
            #print(self.df)
            # Save data to csv
            if not self.df.empty:
                save_pandas_to_file(self.df, self.folder_path, self.symbol)
        except Exception as e:
            error_msg = str(e)
            # Append Error to error_dict
            self.__class__._append_error(self.symbol, error_msg)
            print(error_msg)


    def _routine_request_full_course(self):
        """ Get all historical course data with multiple requests for a symbol
        Because only 2000 data points can be requested per api call, it must be repeated x times for all data
        """
        print('<Full>')
        to_ts = None
        beginning_reached = False     # True, if first datapoint in df['volumefrom'] is 0, which means no data
        while True:
            # Download 2000 data points
            df = API_request_course(self.symbol, to_ts)

            # Cut data, if the first course data df['volumefrom'] is 0
            if df['volumefrom'].iloc[0] == 0: # first date is 0, when no historical course data is available
                beginning_reached = True
                # Search for the first trading day != 0 and delete every date before
                first_non_zero_index = df[df['volumefrom'] != 0].index.min()
                df = df.loc[first_non_zero_index:]
                #print(f'Cut {symbol} - {df_i.index.min().strftime('%Y-%m-%d')}, {len(df_i)}')

            # Combine (merge) all data into one single df
            if df.empty:
                self.df = df
            else:
                self.df = pd.concat([df, self.df], axis=0)

            if beginning_reached: # if first datapoint in df['volumefrom'] was 0, all data is fetched
                return

            # Calculate new cycle for the next 2000 data points
            to_ts = df['time'].iloc[0] - 60 * 60 * 24


    def _routine_update_available_course(self, file_path):
        """ Update the historical course data for a symbol
            This symbol has already been downloaded in the past and now only the days that are missing in the df are requested
        :param file_path: path to the symbol df containing historical course data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File "{file_path}" does not exist')

        # load already existing df from file_path
        df_existing = load_pandas_from_file_path(file_path)
        #print(df_existing)
        # Calculate amount of days (diff) to request the missing data
        n = (pd.Timestamp.today() - df_existing.index[-1]).days - 1
        if n == -1:                     # last_date = today -> no update needed
            print('<Already up to date>')
            return
        elif n == 0:                    # special case, 1 day is missing, that means to_ts must be None
            n = None
        # Download new data
        print('<Update>')
        df = API_request_course(self.symbol, None, n)
        #print(df)
        # Concat old with new data
        self.df = pd.concat([df_existing, df], axis=0)


def _load_symbols_from_yaml():
    """ Load defined symbols from yaml
    :return: list of symbols
    """
    # Load yaml with symbols
    file_name = 'cc_symbols_selected.yaml' # file in same dir
    file_path = Path(__file__).parent / file_name
    with file_path.open('r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get('active')

def _load_symbols_from_api_csv(order=0, n=None):
    """
    :param n: amount of symbols
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
    #df = df[df['ASSET_TYPE'] == 'BLOCKCHAIN']                  # e.g. only BLOCKCHAIN (or TOKEN, INDEX, ...)
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



if __name__ == "__main__":
    """ # Explanation
    There are 2 sources where it is defined which symbols are downloaded:
      - from yaml: self-defined symbols in the file cc_symbols_selected.yaml
      - from api: a list of all available symbols at Cryptocompare. These can be downloaded via the file cc_api_load_symbols.py
        - Parameters: 
          - amount of symbols to request
          - order (file, newest, oldest)

        # Instructions
    - file cc_symbols_api.csv available (if not, then run the file cc_api_load_symbols.py)
    - set source
    - set order and n, if source = api
    - (if existing symbols should be requested completely new (overwrite) and should not only be updated: set self.allow_update = False)
    """

    source = 'yaml' # [yaml, api]

    match source:
        case 'yaml':        # self-defined coins in the yaml file
            symbols = _load_symbols_from_yaml()
        case 'api':         # symbols from crypto compare saved in a csv
            order = 0   # [0 - default, 1 - newest, 2 - oldest]
            n = 20      # amount symbols for api calls (None if download all)
            symbols = _load_symbols_from_api_csv(order, n)
        case _:
            raise ValueError(f'Wrong source: {source}')

    # Storage location
    folder_path = get_path('course_cc') / source

    # Download symbols from list
    for index, symbol in enumerate(symbols):
        # Print
        print(f'\r[{index + 1}/{len(symbols)}] - {symbol}')
        # Download each symbol
        dm = DownloadManagerCC(symbol, folder_path)
        dm.run()
        print()

    # Error Log
    DownloadManagerCC.show_errors(source) # print and save Errors




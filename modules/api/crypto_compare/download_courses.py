""" # Aim
Download historical price data from CryptoCompare:

Input:
- list of symbols (e.g. [BTC, ETH, ADA, ...])
Output:
- downloaded courses in one folder
"""

import requests
import json
import re

from modules.file_handler import *
from modules.error_handling import ErrorHandling


# Errors occur when downloading some symbols and should be ignored
ACCEPTED_ERRORS_LIST = [
    'CCCAGG market does not exist for this coin pair',  # Coin par is invalid (symbol to USD)
    'limit is smaller than min value.'                  # if limit = 0
]
ACCEPTED_ERRORS = {}


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
        raise Exception(f"{data['Message']}")

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

    def __init__(self, symbol:str, error_handling):
        self.symbol = symbol                                     # symbol
        self.error_handling = error_handling                     # Error handling

        self.folder_path = get_path('course_cc') / 'download'    # folder to save all symbols
        self.allow_update = True                                 # bool, whether updates are allowed if file with old data exists (if False, always full download)

        # Initialize variables, value assigned at runtime
        self.df = pd.DataFrame()                                 # requested data (summarized if multiple requests needed)


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
            # Append error (with symbol) to dict, if error in ACCEPTED_ERRORS_LIST
            for accepted_error in ACCEPTED_ERRORS_LIST:
                if accepted_error in str(e):
                    if accepted_error in ACCEPTED_ERRORS:
                        ACCEPTED_ERRORS[accepted_error].append(self.symbol)
                    else:
                        ACCEPTED_ERRORS[accepted_error] = []
                    return
            # Call error handler, if error_msg is not in ACCEPTED_ERRORS
            self.error_handling.log_error(e)


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



def main_routine_download_course_list_cc(symbols:list) -> None:
    # Error handling
    error_handling = ErrorHandling()

    # Download symbols from list
    print(f'Request: {symbols}')
    print(f'Start downloading ...', '\n')
    for index, symbol in enumerate(symbols):
        # Print
        print(f'\r[{index + 1}/{len(symbols)}] - {symbol}')
        # Download each symbol
        dm = DownloadManagerCC(symbol, error_handling)
        dm.run()
        print()

    # Print known errors
    output = json.dumps(ACCEPTED_ERRORS, indent=4)
    output = re.sub(r'",\s+', '", ', output)  # https://stackoverflow.com/questions/48969984/python-json-dump-how-to-make-inner-array-in-one-line
    print(output)
import requests

from modules.file_handler import *


def request_symbols():
    """ Download df with all offered coins (symbols) and the corresponding information from CryptoCompare
    :return: df with all symbols (and information to each symbol)
    """
    # API: https://developers.cryptocompare.com/documentation/data-api/asset_v1_summary_list
    url_base = 'https://data-api.ccdata.io'
    url_adress = '/asset/v1/summary/list?asset_lookup_priority=SYMBOL'
    url = url_base + url_adress

    # Make the API request
    response = requests.get(url)
    data = response.json()

    amount_assets = data['Data']['STATS']['TOTAL_ASSETS']
    print(f'Asset amount: {amount_assets}')

    df = pd.DataFrame(data['Data']['LIST'])
    return df


def routine_download_symbols():
    """ Download and save df with all symbols
    save file: 'cc_symbols_api.csv' to ..\data\course\crypto_compare
    """
    # Download symbols data from cryptocompare
    df = request_symbols()
    df = df[['ID','SYMBOL','ASSET_TYPE','NAME','LAUNCH_DATE']]
    print(df)

    # Save data to a CSV file
    name = 'cc_symbols_api'
    folder = get_path('course_cc')
    save_pandas_to_file(df, folder, name)


if __name__ == "__main__":
    routine_download_symbols()

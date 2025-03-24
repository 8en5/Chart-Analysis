
import pandas as pd

from modules.file_handler import *
from modules.utils import *


def load_symbols_csv():
    folder_path = get_path('cc')
    file_name = 'cc_symbols_api.csv'
    file_path = folder_path / file_name

    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['LAUNCH_DATE'], unit='s')
    #df = df.set_index('date', drop=True)
    return df


def newest_symbols(n=10):
    df_newest = df.nlargest(n, 'date')
    pandas_print_all()
    print(df_newest)



if __name__ == "__main__":
    df = load_symbols_csv()
    df = df.sort_values(by='date')
    print(df)

    newest_symbols(20)
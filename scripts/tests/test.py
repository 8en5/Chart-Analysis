import pandas as pd
import numpy as np

from modules.file_handler import get_path, load_pandas_from_file_path
from modules.strategy.indicator_signals import func_df_signals_from_indicator

def get_df_from_list(list_data, col='close'):
    """ Convert a list into a df with date as index
    :param list_data: list[int]
    :param col: name
    :return: df[index, name]
    """
    # Daily dates with lengeth list_data
    dates = pd.date_range(start="2023-01-01", periods=len(list_data), freq="D")

    # Pandas Frame
    df = pd.DataFrame({
        'date': dates,
        col: list_data
    })

    # Set index
    df.set_index('date', inplace=True)
    #print(df)
    return df


def get_dummy_data_manual():
    close = [10, 10, 1, 2, 4, 3, 6, 8, 5, 4, 3, 4, 8, 12, 10]
    invested = [None, None, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
    df = get_df_from_list(close)
    df['invested'] = invested
    return df


def get_dummy_data_random():
    np.random.seed(40)      # for reproducible results
    close = np.random.randint(1, 20, size=365).tolist()  # 365 random values between 1 and 20
    none_count = np.random.randint(2, 20)  # Number of initial None values
    invested = [None] * none_count + np.random.choice([0, 1], size=365 - none_count).tolist()
    df = get_df_from_list(close)
    df['invested'] = invested
    return df


def get_dummy_data_course(indicator_name='BB', symbol='BTC'):
    indicator_name = indicator_name
    symbol = symbol
    path = get_path('cc') / 'download' / f'{symbol}.csv'
    df = load_pandas_from_file_path(path)
    df = func_df_signals_from_indicator(indicator_name, df)
    df = df.dropna(subset=['invested'])  # remove all rows in the beginning, where df[invested] is None
    df['close_perc'] = df['close'].pct_change(periods=1)
    df = df[['close', 'invested', 'close_perc']]
    return df
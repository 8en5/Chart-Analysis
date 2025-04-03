import matplotlib.pyplot as plt
from scipy.ndimage import extrema

from modules.utils import pandas_print_width, pandas_print_all
from modules.file_handler import load_pandas_from_symbol
from modules.strategy.df_signals_invested import func_df_signals_from_indicator
from modules.params import get_params_from_yaml

from modules.plot import *

#pandas_print_width()
#pandas_print_all()


def min_max_df(df):
    return df.min, df.max


def single_evaluation_states(df):
    periods = [-30, -14, -7, 7, 14, 30, 60, 120, 180]


def evaluate_single_signals(df):
    for index, signal in enumerate(df['signal']):
        if signal in ['buy', 'sell', 'bullish', 'bearish']:
            print(signal)
            exit()


def plot(df):
    fig, ax = plt.subplots(1, 1)
    ax_course_highlight_signals_line(ax, df)
    plt.show()


def main():
    # Load course
    df = load_pandas_from_symbol('ADA')

    # Indicator
    indicator_name = 'MACD'
    params = get_params_from_yaml(indicator_name, 'default')

    # Invested
    df = func_df_signals_from_indicator(indicator_name, df, [20, 30, 20])
    df = df[['close', 'signal']]
    print(df)
    exit()

    # Single evaluation
    #evaluate_single_signals(df[30:-30])
    plot(df)


if __name__ == "__main__":
    main()
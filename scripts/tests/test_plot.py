import matplotlib.pyplot as plt
import pandas_ta as ta

from modules.file_handler import *
from modules.indicators import *

from test import *
from modules.plot import *


def test_plot_all_indicators():
    strategy_names = ['BB', 'MACD', 'RSI', 'SMA']
    for strategy_name in strategy_names:
        print(strategy_name)
        test_plot_indicator(strategy_name)
        print()

def test_plot_indicator(strategy_name):
    symbol = 'BTC'

    # Load course and indicator
    df = load_pandas_from_symbol(symbol)
    df = func_indicator(strategy_name, df)

    # Figure
    fig, ax = plt.subplots(2, 1)
    # Plot 1 (Course)
    ax_course(ax[0], df)
    ax_default_properties(ax[0], symbol)
    # Plot 2 (Indicators)
    func_ax_indicator(strategy_name, ax[1], df)
    ax_default_properties(ax[1], 'Indicator')

    save = True
    show = False
    if save:
        folder_path = get_path() / 'data/indicators'
        save_matplotlib_figure(fig, folder_path, strategy_name)
    if show:
        plt.show()


def test_plot_all_perc():
    freqs = ['D', '3D', 'W', 'ME', 'QE', 'YE']
    for freq in freqs:
        print(freq)
        test_plot_perc(freq)
        print()

def test_plot_perc(freq='ME'):
    symbol = 'BTC'

    # Load course and indicator
    df = load_pandas_from_symbol(symbol)
    df['close_perc'] = df['close'].pct_change(periods=1)
    df = perc_change(df, freq)
    #print(df)

    # Figure
    fig, ax = plt.subplots(3, 1)
    # Plot 1 (Course)
    ax_course(ax[0], df)
    ax_default_properties(ax[0], symbol)
    # Plot 2 (Perc df)
    ax_perc(ax[1], df)
    ax_default_properties(ax[1], 'Indicator')
    # Plot 3 (Perc bar)
    ax_perc_bar(ax[2], df)
    ax_default_properties(ax[2], 'Indicator')

    save = True
    show = False
    if save:
        folder_path = get_path() / 'data/indicators'
        save_matplotlib_figure(fig, folder_path, f'perc_{freq}')
    if show:
        plt.show()


def test_ax_background_colored_evaluation():
    data = [1,2,2,2,4,4,4,5,5]
    df = get_df_from_list(data)
    df['evaluation'] = ''
    df.loc[df.index[1], 'evaluation'] = 'buy'
    df.loc[df.index[3], 'evaluation'] = 'sell'
    df.loc[df.index[5], 'evaluation'] = 'bullish'
    df.loc[df.index[7], 'evaluation'] = 'bearish'
    print(df)

    fig, ax = plt.subplots(1, 1)
    ax_course(ax, df)
    ax_background_colored_signals(ax, df)

    plt.show()




if __name__ == "__main__":

    # Indicator
    #test_plot('BB')
    #test_plot_all_indicators() # Plot all indicators

    # Percentage
    #test_plot_perc()
    test_plot_all_perc()

    # Background colored evaluation
    #test_ax_background_colored_evaluation()





from modules.file_handler import *
from modules.indicators import *

from test import *
from modules.plot import *


def all_indicators():
    indicator_names = ['BB', 'MACD', 'RSI', 'SMA']
    for indicator_name in indicator_names:
        print(indicator_name)
        _plot_indicator(indicator_name)
        print()


def _plot_indicator(indicator_name):
    # Load course and indicator
    df = load_pandas_from_symbol(symbol)
    df = func_indicator(indicator_name, df)

    # Figure
    fig, ax = plt.subplots(2, 1)
    # Plot 1 (Course)
    ax_course(ax[0], df)
    ax_properties(ax[0], symbol)
    # Plot 2 (Indicators)
    func_ax_indicator(indicator_name, ax[1], df)
    ax_properties(ax[1], 'Indicator')

    # Save plot
    save_matplotlib_figure(fig, folder_path, indicator_name)


def all_perc():
    freqs = ['D', '3D', 'W', 'ME', 'QE', 'YE']
    for freq in freqs:
        print(freq)
        _plot_perc(freq)
        print()

def _plot_perc(freq='ME'):
    # Load course and indicator
    df = load_pandas_from_symbol(symbol)
    df['close_perc'] = df['close'].pct_change(periods=1)
    df = perc_change(df, freq)
    #print(df)

    # Figure
    fig, ax = plt.subplots(3, 1)
    # Plot 1 (Course)
    ax_course(ax[0], df)
    ax_properties(ax[0], symbol)
    # Plot 2 (Perc df)
    ax_perc(ax[1], df)
    ax_properties(ax[1], 'Indicator')
    # Plot 3 (Perc bar)
    ax_perc_bar(ax[2], df)
    ax_properties(ax[2], 'Indicator')

    # Save
    save_matplotlib_figure(fig, folder_path, f'perc_{freq}')



if __name__ == "__main__":
    """
    Save all plots of the different indicators to a folder
    """
    symbol = 'BTC'
    folder_path = get_path() / 'data/analyse/all_indicators'

    all_indicators()
    all_perc()
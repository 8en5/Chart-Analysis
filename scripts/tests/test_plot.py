import matplotlib.pyplot as plt
import pandas_ta as ta

from modules.file_handler import *
from modules.indicators import *

from test import *
from modules.plot import *




def test_plot_indicator(indicator_name):
    symbol = 'BTC'

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

    # Show
    plt.show()



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
    ax_properties(ax[0], symbol)
    # Plot 2 (Perc df)
    ax_perc(ax[1], df)
    ax_properties(ax[1], 'Indicator')
    # Plot 3 (Perc bar)
    ax_perc_bar(ax[2], df)
    ax_properties(ax[2], 'Indicator')

    # Show
    plt.show()


if __name__ == "__main__":

    # Indicator
    test_plot_indicator('BB') # ['BB', 'MACD', 'RSI', 'SMA']

    # Percentage
    #test_plot_perc('d') # ['D', '3D', 'W', 'ME', 'QE', 'YE']

    # Background colored evaluation
    #test_ax_background_colored_evaluation()




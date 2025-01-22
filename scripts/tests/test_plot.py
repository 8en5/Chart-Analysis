import matplotlib.pyplot as plt
import pandas_ta as ta

from modules.file_handler import *
from modules.indicators import *

from test import *
from modules.plot import *



def test_plot():
    # Figure
    fig, ax = plt.subplots(2, 1)

    # Plot 1 (Course)
    ax_course(ax[0], df)
    ax_graph_elements(ax[0], symbol)

    # Plot 2 (Indicators)

    #df_BB = ta.bbands(df['close'], length=6, std=2.0)
    #ax_BB(ax[1], df_BB)

    #df_MACD = ta.macd(df['close'], fast=12, slow=26, signal=9)
    #ax_MACD(ax[1], df_MACD)

    #df_RSI = RSI(df,14, 30, 70)
    #ax_RSI(ax[1], df_RSI)

    #df_SMA = SMA(df, 200, 50, 10)
    #ax_SMA(ax[1], df_SMA)

    df_perc = percentage_change(df, 'ME')
    #ax_percentage(ax[1], df_perc)
    #ax_percentage_freq(ax[1], df_perc)

    ax_graph_elements(ax[1], 'Indicator')
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
    ax_background_colored_evaluation(ax, df)

    plt.show()




if __name__ == "__main__":

    symbol = 'BTC'
    df = load_pandas_from_symbol(symbol)

    # Test
    #test_plot()
    test_ax_background_colored_evaluation()




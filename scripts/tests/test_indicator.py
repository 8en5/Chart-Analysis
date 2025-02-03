import matplotlib.pyplot as plt

from test import *
from modules.indicators import *
from modules.plot import *


def test_indicator(indicator:str):
    values = pd.Series(np.random.randint(1, 100, size=300))
    df = get_df_from_list(values)

    func_str = globals()[f'indicator_{indicator}']
    df = func_str(df)
    print(df)
    col = get_indicator_col_names(df, indicator)
    print(col)


def test_perc():
    #values = np.random.choice([1, 2], size=21)
    values = [1, 1,2,3,4,5,6,7, 2,2,2,2,3,3,3]
    df_test = get_df_from_list(values)
    print(df_test)

    fig, ax = plt.subplots(1, 1)
    df_test = perc_change(df_test, '3D')
    print(df_test)

    ax_percentage_freq(ax, df_test)
    ax_graph_elements(ax)
    plt.show()


def test_col_names():
    values = pd.Series(np.random.randint(1, 100, size=30))
    df = get_df_from_list(values)
    df = indicator_RSI(df)
    col_rsi = get_indicator_col_names(df, 'RSI')
    print(col_rsi)


if __name__ == "__main__":

    test_indicator('BB')

    #test_percentage()

    #test_col_names()
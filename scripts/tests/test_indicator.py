import matplotlib.pyplot as plt

from test import *
from modules.indicators import *
from modules.plot import *


def test_indicator(indicator_name:str):
    values = pd.Series(np.random.randint(1, 100, size=200))
    df = get_df_from_list(values)

    pandas_print_all()
    df = func_indicator(indicator_name, df)
    print(df)
    col = get_indicator_col_names(df, indicator_name)
    print(col)

    # Leading None for every column
    print()
    leading_nans = df.apply(lambda col: col.isna().cumprod().sum())
    print(leading_nans)


def test_col_names(indicator_name):
    values = pd.Series(np.random.randint(1, 100, size=30))
    df = get_df_from_list(values)
    df = func_indicator(indicator_name, df)
    col_rsi = get_indicator_col_names(df, indicator_name)
    print(col_rsi)


def test_perc():
    #values = np.random.choice([1, 2], size=21)
    values = [1, 1,2,3,4,5,6,7, 2,2,2,2,3,3,3]
    df_test = get_df_from_list(values)
    print(df_test)

    fig, ax = plt.subplots(1, 1)
    df_test = perc_change(df_test, '3D')
    print(df_test)

    ax_perc_bar(ax, df_test)
    ax_default_properties(ax)
    plt.show()





if __name__ == "__main__":
    indicator_names = ['BB', 'MACD', 'RSI']

    test_indicator('MACD')

    #test_percentage()

    #test_col_names()
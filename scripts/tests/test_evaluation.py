
from test import *
from modules.evaluation import *


def test_zero_crossing():
    data = [2, 1, -1, -1, -2, 3, 5, 4, -4, 0]
    df = get_df_from_list(data)

    df, cols = zero_crossing(df,'close')
    print(df)


def test_calculate_crossings():
    data1 = [2, 3, 1, 0, -1, -1, 0, 2, 3, 3]
    data2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    df = get_df_from_list(data1, '1')
    df['2'] = data2

    df, cols = calculate_crossings(df, '1', '2')
    print(df)



if __name__ == "__main__":

    #test_zero_crossing()

    test_calculate_crossings()

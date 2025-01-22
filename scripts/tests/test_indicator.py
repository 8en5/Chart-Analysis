import matplotlib.pyplot as plt

from test import *
from modules.indicators import *
from modules.plot import *


def test_percentage():
    #values = np.random.choice([1, 2], size=21)
    values = [1, 1,2,3,4,5,6,7, 2,2,2,2,3,3,3]
    df_test = get_df_from_list(values)
    print(df_test)

    fig, ax = plt.subplots(1, 1)
    df_test = percentage_change(df_test, '3D')
    print(df_test)

    ax_percentage_freq(ax, df_test)
    ax_graph_elements(ax)
    plt.show()


if __name__ == "__main__":

    test_percentage()
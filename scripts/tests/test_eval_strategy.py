import matplotlib.pyplot as plt

from modules.plot import *
from test import *
from modules.strategy.eval_strategy import *



def test_eval_strategy():
    # Dummy data
    close = [1, 2, 4, 3, 6, 8, 5, 4, 3, 4, 8, 12, 10]
    invested = [0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
    df = get_df_from_list(close)
    df['invested'] = invested


    # Backtesting
    evaluate_strategy(df)
    exit()


    # Plot
    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    ax_background_colored_signals(ax, df)  # Evaluation In, Out
    ax_course(ax, df)  # Course
    ax_graph_elements(ax, 'Test')  # Labels
    plt.show()



if __name__ == "__main__":

    test_eval_strategy()
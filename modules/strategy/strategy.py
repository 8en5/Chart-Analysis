import matplotlib.pyplot as plt

from modules.plot import *
from modules.strategy.indicator_signals import *
from modules.strategy.evaluate_invested import evaluate_invested


def get_df_strategy(course_path, indicator_name, params=None):

    # Load df
    df = load_pandas_from_file_path(course_path)
    df = df[['close']]

    # df[<indicators>, signal] - Calculate indicators
    df = func_df_signals_from_indicator(indicator_name, df, params)

    # df[invested] - Calculate invested
    df = df_invested_from_signal(df)

    # df[close_perc] - Calculate daily perc change from course
    df = df_close_perc(df)

    # df[group_invested] - Group invested
    df = df_group_invested(df)

    return df


def get_dict_evaluation(df):
    result_dict = evaluate_invested(df)
    return result_dict





if __name__ == "__main__":
    # Testing
    from modules.course import get_courses_paths
    c_p = get_courses_paths('ADA')

    pandas_print_all()
    df = get_df_strategy(c_p[0], 'MACD')

    fig, ax = plt.subplots(1, 1, sharex=True)
    ax_course_highlight_invested(ax, df, 'rect')
    plt.show()


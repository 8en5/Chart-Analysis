import matplotlib.pyplot as plt
from pathlib import Path

from modules.utils import pandas_print_width, pandas_print_all
from modules.file_handler import load_pandas_from_file_path
from modules.plot import fig_signals
from modules.strategy.df_signals_invested import func_df_signals_from_indicator
from modules.strategy.evaluate_signals import evaluate_signals


def indicator_signals(indicator_name, course_path, params=None, offset:int=0,
                       save_plot=False, show_plot=False, base_folder:Path=None) -> None:
    """ [strategy, indicator, signals] Load and evaluate strategy (1x param for 1x course)
    :param indicator_name: indicator name
    :param course_path: course path
    :param params: 1x params (as dict, list or None)
    :param offset: offset df
    :param save_plot: save plot
    :param show_plot: show plot
    :param base_folder: base folder
    :return: None
    """
    # 1. Calculate full df
    # Load course
    df = load_pandas_from_file_path(course_path)
    df = df[['close']]
    # df[<indicators>, signal] - Calculate indicators
    df = func_df_signals_from_indicator(indicator_name, df, params)
    # cut offset for standardization (each parameter has a different leading time until they deliver signals)
    df = df.iloc[offset:]
    #print(df)
    #exit()


    # 2. Calculate evaluation
    evaluate_signals(df)


    # 3. Visualize
    show_plot = True
    if show_plot:
        fig = fig_signals(df, 'Title')
        plt.show()




if __name__ == "__main__":
    # Testing
    from modules.course import get_courses_paths
    pandas_print_all()
    indicator = 'MACD'
    param = None # [10, 20, 10]
    course_path = get_courses_paths('ADA')[0]
    indicator_signals(indicator, course_path, params=param,
                       save_plot=False, show_plot=True, offset=0)
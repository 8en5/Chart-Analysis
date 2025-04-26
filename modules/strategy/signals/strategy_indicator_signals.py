import matplotlib.pyplot as plt
from pathlib import Path

from modules.utils import pandas_print_width, json_dump_nicely
from modules.file_handler import load_pandas_from_file_path
from modules.plot import fig_signals_simple, fig_signals_indicator, save_fig
from modules.strategy.df_signals_invested import func_df_signals_from_indicator
from modules.strategy.signals.evaluate_signals import *
from modules.strategy.utils_study import *


def indicator_signals(indicator_name, course_path, params=None, offset:int=0,
                       save_plot=False, show_plot=False, base_folder:Path=None, signal_type='all') -> dict|None:
    """ [strategy, indicator, signals] Load and evaluate strategy (1x param for 1x course)
    :param indicator_name: indicator name
    :param course_path: course path
    :param params: 1x params (as dict, list or None)
    :param offset: offset df
    :param save_plot: save plot
    :param show_plot: show plot
    :param base_folder: base folder
    :param signal_type: for plotting [all, buy, sell]
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
    #df = df[0:200]
    result_dict_returns = evaluate_signals(df)
    if not result_dict_returns:
        return None
    #print(json_dump_nicely(result_dict_returns))
    result_dict_states = calc_states_from_dict(result_dict_returns)
    #print_result_dict_as_df(result_dict_states)


    # 3. Visualize
    #save_plot = True # debug
    #show_plot = False # debug
    if show_plot or save_plot:
        #signal_type = 'all'
        # Figure 1
        plot_type = 'indicator'  # simple, indicator
        if plot_type == 'simple':
            # 1x1 fig - course with evaluation
            fig1 = fig_signals_simple(df, indicator_name, signal_type)
        elif plot_type == 'indicator':
            # 2x1 fig - course with evaluation + indicator
            fig1 = fig_signals_indicator(df, indicator_name, title1=course_path.stem,
                                         title2=f'{indicator_name}: {params}', signal_type=signal_type)
        else:
            raise ValueError(f'Wrong plot type: {plot_type}')
        # Figure 2
        fig2 = fig_signals_evaluation(result_dict_states, signal_type)
        if save_plot:
            if not base_folder:
                base_folder = get_path() / f'data/analyse/visualize/signals'
            file_path1 = calc_file_path(indicator_name, course_path.stem, params, index=1, base_folder=base_folder)
            save_fig(fig1, file_path1)
            file_path2 = calc_file_path(indicator_name, course_path.stem, params, index=2, base_folder=base_folder)
            save_fig(fig2, file_path2)
            plt.close('all')  # close figure, else it is still in memory
        if show_plot:
            plt.show()


    # Return result_dict
    return result_dict_returns



if __name__ == "__main__":
    # Testing
    from modules.course import get_courses_paths
    #pandas_print_all()
    pandas_print_width()
    indicator = 'MACD'
    param = [9, 27, 41]
    course_path = get_courses_paths('SOL')[0]
    indicator_signals(indicator, course_path, params=param,
                      save_plot=False, show_plot=True, offset=0,
                      signal_type='sell')
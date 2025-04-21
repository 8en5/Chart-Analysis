from modules.plot import *
from modules.strategy.df_signals_invested import *
from modules.strategy.invested.evaluate_invested import evaluate_invested, evaluate_invested_multiple_cycles
from modules.strategy.utils_study import *


def indicator_invested(indicator_name, course_path, params=None, offset:int=0,
                       save_plot=False, show_plot=False, base_folder:Path=None) -> dict:
    """ [strategy, indicator, invested] Load and evaluate strategy (1x param for 1x course)
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
    # df[invested] - Calculate invested
    df = df_invested_from_signal(df)
    # df[close_perc] - Calculate daily perc change from course
    df = df_close_perc(df)
    # df[group_invested] - Group invested
    df = df_group_invested(df)
    #print(df)
    #exit()


    # 2. Calculate evaluation
    result_dict_all = evaluate_invested(df)
    result_dict_intervals, df_summary = evaluate_invested_multiple_cycles(df)
    #print(json_round_dict(result_dict_all))
    #print(json_round_dict(result_dict_intervals))
    #print(df_summary)
    #exit()


    # 3. Visualize
    df = add_one_invested_after_selling(df) # only for visualization
    #show_plot = True # debug
    #save_plot = True # debug
    study_type = 'params' # [params, symbols]
    if show_plot or save_plot:
        # result_dict_all
        plot_invested(df, indicator_name, course_path, params, study_type, result_dict_all,
             index=-1, save_plot=save_plot, show_plot=show_plot, base_folder=base_folder)
        # df_summary
        for row in df_summary.itertuples(index=True):
            df_i = df.iloc[int(row.start):int(row.end)].copy()
            row_dict = row._asdict()
            result_dict = {k: v for k, v in row_dict.items() if k not in ['start', 'end', 'Index']}
            plot_invested(df_i, indicator_name, course_path, params, study_type, result_dict,
                 index=row.Index, save_plot=save_plot, show_plot=show_plot, base_folder=base_folder)


    # 4. Prepare evaluation information
    # sorting criteria
    sorting_criteria = 'all' # [all, intervals]
    if sorting_criteria == 'all':
        sorting = result_dict_all['S'] ** 0.5 # square root, otherwise very rising courses will have too great influence
    elif sorting_criteria == 'intervals':
        sorting = result_dict_intervals['S']
    else:
        raise ValueError(f'Wrong key: {sorting_criteria}')
    # All results in one dict
    result_dict = {
        'sorting': sorting,                 # the study will be sorted according to this value
        'all': result_dict_all,             # result_dict over the entire period
        'intervals': result_dict_intervals  # result_dict as mean values over multiple cycles
    }
    result_dict = json_round_dict(result_dict) # round
    #print(result_dict)
    #exit()
    return result_dict


#---------------------- Visualize ----------------------#

def plot_invested(df, indicator_name, course_path, params, study_type, result_dict,
         index=-1, save_plot=False, show_plot=False, base_folder:Path=None):
    # Figure
    plot_type = 'indicator'  # simple, indicator
    evaluation_dict_str = _calc_evaluation_to_str(result_dict)
    if plot_type == 'simple':
        # 1x1 fig - course with evaluation
        fig = fig_invested_simple(df, title=evaluation_dict_str)
    elif plot_type == 'indicator':
        # 2x1 fig - course with evaluation + indicator
        fig = fig_invested_indicator(df, indicator_name, title1=course_path.stem, title2=f'{indicator_name}: {params}',
                                     suptitle=evaluation_dict_str)
    else:
        raise ValueError(f'Wrong plot type: {plot_type}')

    # Save or show plot
    if save_plot:
        if not base_folder:
            base_folder = get_path() / f'data/analyse/visualize/invested'
        # file path [param/symbol -> data/analyse/visualize/... , study -> data/study/Study_newest/...]
        file_path = calc_file_path(indicator_name, course_path.stem, params, study_type, index, base_folder)
        save_fig(fig, file_path)
        plt.close() # close figure, else it is still in memory ("Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory"
    if show_plot:
        plt.show()



def _calc_evaluation_to_str(evaluation_dict) -> str:
    """ [fig] Convert evaluation dict to str
    :param evaluation_dict: evaluation dict
    :return: evaluation str

    Input:  {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    Output: 'S: 12.53 | BaH: 12.27 | diff: 0.25
    """
    evaluation_dict_str= f"S = {evaluation_dict['S']:.2f} | BaH = {evaluation_dict['BaH']:.2f} | Diff = {evaluation_dict['diff']:.2f}"
    return evaluation_dict_str




if __name__ == "__main__":
    # Testing
    from modules.course import get_courses_paths
    pandas_print_all()
    indicator = 'BB'
    course_path = get_courses_paths('ADA')[0]
    param = None  # [10, 20, 10]
    indicator_invested(indicator, course_path, params=param,
                       save_plot=False, show_plot=True, offset=0)


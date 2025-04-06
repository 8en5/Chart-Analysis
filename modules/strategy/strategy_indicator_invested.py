import matplotlib.pyplot as plt

from modules.plot import *
from modules.strategy.df_signals_invested import *
from modules.strategy.evaluate_invested import evaluate_invested, evaluate_invested_multiple_cycles


def indicator_invested(indicator_name, course_path, params=None, offset:int=0,
                       save_plot=False, show_plot=False, base_folder:Path=None):

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
        plot(df, indicator_name, course_path, params, study_type, result_dict_all,
             index=-1, save_plot=save_plot, show_plot=show_plot, base_folder=base_folder)
        # df_summary
        for row in df_summary.itertuples(index=True):
            df_i = df.iloc[int(row.start):int(row.end)].copy()
            row_dict = row._asdict()
            result_dict = {k: v for k, v in row_dict.items() if k not in ['start', 'end', 'Index']}
            plot(df_i, indicator_name, course_path, params, study_type, result_dict,
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

def plot(df, indicator_name, course_path, params, study_type, result_dict,
         index=-1, save_plot=False, show_plot=False, base_folder:Path=None):
    # Figure
    plot_type = 'default'  # default, indicator
    evaluation_dict_str = _calc_evaluation_to_str(result_dict)
    if plot_type == 'default':
        # 1x1 fig - course with evaluation
        fig = fig_invested_default(df, title=evaluation_dict_str)
    elif plot_type == 'indicator':
        # 2x1 fig - course with evaluation + indicator
        fig = fig_invested_indicator(df, indicator_name, title1=course_path.stem, title2=f'{indicator_name}: {params}',
                                     suptitle=evaluation_dict_str)
    else:
        raise ValueError(f'Wrong plot type: {plot_type}')

    # Save or show plot
    if save_plot:
        # file path [param/symbol -> data/analyse/visualize/... , study -> data/study/Study_newest/...]
        file_path = _calc_file_path(indicator_name, course_path.stem, params, study_type, index, base_folder)
        save_fig(fig, file_path)
        plt.close() # close figure, else it is still in memory ("Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory"
    if show_plot:
        plt.show()


def _calc_file_path(indicator_name:str, course:str, params:dict|list, study_type='params',
                    index=-1, base_folder:Path=None) -> Path:
    """ [fig] Calculate file path for the plot
    Aim: Targeted saving of the different variants

    :param indicator_name: indicator name
    :param course: symbol (course)
    :param params: params (1x dict or list)
    :param study_type: [params, symbols]
    :return: path to save the plot
    """
    params_str = _calc_params_to_str(params) # params as string
    suffix = ''
    if index >= 0:
        suffix = f'_{index}'
    # Calculate folder path
    if not base_folder:
        base_folder = get_path() / f'data/analyse/visualize'
        if study_type == 'params': # params oriented (for one param there are many symbols)
            file_path = base_folder / f'{study_type}/{indicator_name}/{params_str}/{course}{suffix}.png'
        elif study_type == 'symbols': # symbols oriented (for one symbol there are many params
            file_path = base_folder / f'{study_type}/{indicator_name}/{course}/{params_str}{suffix}.png'
        else:
            raise ValueError(f'study_type must be [params, symbols, study]: {study_type}')
    else: # Study
        file_path = base_folder / f'{params_str}/{course}{suffix}.png'

    return file_path


def _calc_params_to_str(params:dict|list) -> str:
    """ [fig] Convert params dict to str (for folder name)
    :param params: params dict
    :return: params str

    Input:  {'m_fast': 14, 'm_slow': 30, 'm_signal': 70} / [14, 30, 70]
    Output: '14_30_70'
    """
    # Check
    if isinstance(params, dict):
        params_str = '_'.join(str(value) for value in params.values())
    elif isinstance(params, list):
        params_str = '_'.join(str(value) for value in params)
    elif not params:
        params_str = 'None'
    else:
        raise TypeError(f'parameter is not a dict: {params}')
    return params_str


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
    indicator_invested('MACD', get_courses_paths('SOL')[0], params=None,
                       save_plot=False, show_plot=True, offset=0)


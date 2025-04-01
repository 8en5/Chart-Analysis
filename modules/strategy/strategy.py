import matplotlib.pyplot as plt
from matplotlib.pyplot import title

from modules.plot import *
from modules.strategy.indicator_signals import *
from modules.strategy.evaluate_invested import evaluate_invested


def strategy(course_path, indicator_name, params=None,
             save_plot=False, study_type='params'):

    # 1. Calculate full df
    # Load course
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


    # 2. Calculate evaluation
    result_dict = evaluate_invested(df)


    # 3. Visualize
    show_plot = True # debug
    if show_plot or save_plot:
        # Figure
        evaluation_dict_str = _calc_evaluation_to_str(result_dict)
        fig = fig_invested_default(df, title=evaluation_dict_str)
        #fig = fig_invested_indicator(df, indicator_name, title1=course_path.stem, title2=f'{indicator_name}: {params}', suptitle=evaluation_dict_str)
        # Save or plot
        if save_plot:
            # file path [default - data/analyse/visualize/... , study - data/study/Study_newest/...]
            file_path = _calc_file_path(indicator_name, course_path.stem, params, study_type)
            save_fig_default(fig, file_path)
        if show_plot:
            plt.show()

    # Return evaluation for the meta study
    return result_dict



#---------------------- Visualize ----------------------#


def _calc_file_path(indicator_name:str, course:str, params:dict|list, study_type='params') -> Path:
    """ [fig] Calculate file path for the plot
    Aim: Targeted saving of the different variants

    :param indicator_name: indicator name
    :param course: symbol (course)
    :param params: params (1x dict or list)
    :param study_type: [params, symbols]
    :return: path to save the plot
    """
    params_str = _calc_params_to_str(params) # params as string
    # Calculate folder path
    if study_type == 'params': # params oriented (for one param there are many symbols)
        file_path = get_path() / f'data/analyse/visualize/{study_type}/{indicator_name}/{params_str}/{course}.png'
    elif study_type == 'symbols': # symbols oriented (for one symbol there are many params
        file_path = get_path() / f'data/analyse/visualize/{study_type}/{indicator_name}/{course}/{params_str}.png'
    elif study_type == 'study': # best results from param study
        """ Implementation note
        Folder needs to be in the actual running Study and then in the folder {indicator_name}_{course_selection_key}
        Problem: in this function there is no information about the course_selection_key
                (and I don't want to pass the information because I pass the course_paths)
        Current implementation: The folder path is calculated over the 2x last created folders in a directory
                1) 'Study' and then to the 2) 'param_study'
        This is not robust, quick and dirty solution 
        """
        folder_study = get_last_created_folder_in_dir('study')          # latest Study
        folder_indicator = get_last_created_folder_in_dir(folder_study) # latest param_study (indicator with course_selection_key) in this Study
        file_path = folder_indicator / f'{params_str}/{course}.png'
    else:
        raise ValueError(f'study_type must be [params, symbols, study]: {study_type}')
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
    df_test = strategy(get_courses_paths('ADA')[0], 'MACD',
                  save_plot=False, study_type='params')



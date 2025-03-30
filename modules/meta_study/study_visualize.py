""" [fig] Visualize strategies - plot and save/show
Manager, to study different variants

Input: indicator_name, source_courses, source_params, study_type
Output: [fig] Plot (save/show) that visualizes the strategy
"""

from modules.file_handler import *
from modules.course import get_courses_paths
from modules.params import get_all_params_variations_from_yaml
from modules.plot import fig_type1_default, fig_type2_indicator, save_fig
from modules.strategy.evaluate_invested import evaluate_invested_multiple_cycles
from modules.strategy.indicator_signals import func_get_signals_from_indicator


#---------------------- Manger for Visualization ----------------------#

def manager_visualize_strategies(indicator_name, source_courses, source_params, study_type='params'):
    """ [Loop fig] Manager to plot and save (visualize) strategies
    :param indicator_name: indicator name
    :param source_courses: multiple sources possible: course_selection_key / list symbol_names
    :param source_params: different sources possible - key_course_selection / list_params_variations / None (default key_course_selection)
    :param study_type: folder structure [*params, *symbols | *study]
    """
    # Prepare variables
    # Symbols
    courses_paths = get_courses_paths(source_courses)
    # Param combinations
    if isinstance(source_params, str):  # key from yaml
        params_variations = get_all_params_variations_from_yaml(indicator_name, source_params)
    elif isinstance(source_params, list):  # already a list of params_variations
        params_variations = source_params
    elif isinstance(source_params, dict) or source_params is None:  # default params
        params_variations = get_all_params_variations_from_yaml(indicator_name, 'default')
    else:
        raise ValueError(f'Wrong instance (not [str, list, None] of source_params: {source_params}')


    # Loop over symbols and params
    if study_type in ['params', 'study']:
        # params oriented -> one param with many symbols
        i = 1
        l_p = len(params_variations)
        l_s = len(courses_paths)
        for i_p, params in enumerate(params_variations):
            for i_s, symbol_path in enumerate(courses_paths):
                print(f'{i}/{l_s * l_p}: \t\t {i_p + 1}/{l_p} {params} \t\t {i_s + 1}/{l_s}: {symbol_path.stem}')
                routine_visualize_strategy(indicator_name, symbol_path, params, study_type)
                i += 1
                print()
    elif study_type == 'symbols':
        # symbols oriented -> one symbol with many params
        i = 1
        l_s = len(courses_paths)
        l_p = len(params_variations)
        for i_s, symbol_path in enumerate(courses_paths):
            for i_p, params in enumerate(params_variations):
                print(f'{i}/{l_s * l_p}: \t\t {i_s + 1}/{l_s}: {symbol_path.stem} \t\t {i_p + 1}/{l_p} {params}')
                routine_visualize_strategy(indicator_name, symbol_path, params, study_type)
                i += 1
                print()
    else:
        raise ValueError(f'study_type must be [params, symbols]: {study_type}')



def routine_visualize_strategy(indicator_name:str, symbol_path:Path, params:dict, study_type='params') -> None:
    """ [fig] Main routine for the visualization study
    :param indicator_name: indicator name
    :param symbol_path: path to symbol
    :param params: 1x params for one indicator
    :param study_type: [*params, *symbols | *study]
    :return: None
    """
    # full df - df[close, <indicators>, signal, invested]
    df = _calc_indicator_and_invested(symbol_path, indicator_name, params)
    # evaluation - {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    evaluation_dict = _calc_evaluation(df)
    # file path [default - data/analyse/visualize/... , study - data/study/Study_newest/...]
    file_path = _calc_file_path(indicator_name, symbol_path.stem, params, study_type)
    # title
    evaluation_dict_str = _calc_evaluation_to_str(evaluation_dict)

    # Plot
    save_plot = True
    show_plot = False
    fig = fig_type2_indicator(df, indicator_name, symbol_path.stem, f'{indicator_name}: {params}', evaluation_dict_str)
    #fig = plot_type1_default(df, f'{evaluation_dict_str}\n{symbol_path.stem}\n{params}')
    if save_plot:
        save_fig(fig, file_path)
    if show_plot:
        plt.show()



def _calc_indicator_and_invested(symbol_path, indicator_name, params) -> pd.DataFrame:
    """ [fig] Calculate full df[close, <indicators>, signal, invested]
    :param symbol_path: path to symbol
    :param indicator_name: indicator name
    :param params: 1x params for the indicator
    :return: df[close, <indicators>, signal, invested]
    """
    # Load symbol - df[close]
    df = load_pandas_from_file_path(symbol_path)[['close']]
    # Calculate signals and invested - df[<indicators>, signal, invested]
    df = func_get_signals_from_indicator(indicator_name, df, params)
    # print(df)
    return df


def _calc_evaluation(df) -> dict:
    """ [fig] Calculate evaluation
    :param df: df[invested]
    :return: dict evaluation - e.g. {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    """
    evaluation_dict = evaluate_invested_multiple_cycles(df)
    return evaluation_dict


def _calc_params_to_str(params) -> str:
    """ [fig] Convert params dict to str (for folder name)
    :param params: params dict
    :return: params str

    Input:  {'m_fast': 14, 'm_slow': 30, 'm_signal': 70}
    Output: '14_30_70'
    """
    # Check
    if not isinstance(params, dict):
        raise TypeError(f'parameter is not a dict: {params}')
    # Calculate string - e.g. '5_1.5'
    params_str = '_'.join(str(value) for value in params.values())
    return params_str


def _calc_file_path(indicator_name:str, course:str, params:dict, study_type='params') -> Path:
    """ [fig] Calculate file path for the plot
    Aim: Targeted saving of the different variants

    :param indicator_name: indicator name
    :param course: symbol (course)
    :param params: params (1x dict)
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
    manager_visualize_strategies('MACD', 'default', 'visualize', study_type='symbols')

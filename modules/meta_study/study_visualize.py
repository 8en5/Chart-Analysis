""" [fig] Visualize strategies - plot and save/show
Manager, to study different variants

Input: indicator_name, source_courses, source_params, study_type
Output: [fig] Plot (save/show) that visualizes the strategy
"""

from modules.file_handler import *
from modules.course import get_courses_paths
from modules.params import get_all_params_variations_from_yaml
from modules.plot import fig_invested_default, fig_invested_indicator, save_fig
from modules.strategy.evaluate_invested import evaluate_invested_multiple_cycles
from modules.strategy.df_signals_invested import func_df_signals_from_indicator


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
    fig = fig_invested_indicator(df, indicator_name, symbol_path.stem, f'{indicator_name}: {params}', evaluation_dict_str)
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
    df = func_df_signals_from_indicator(indicator_name, df, params)
    # print(df)
    return df


def _calc_evaluation(df) -> dict:
    """ [fig] Calculate evaluation
    :param df: df[invested]
    :return: dict evaluation - e.g. {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    """
    evaluation_dict = evaluate_invested_multiple_cycles(df)
    return evaluation_dict






if __name__ == "__main__":
    # Testing
    manager_visualize_strategies('MACD', 'default', 'visualize', study_type='symbols')

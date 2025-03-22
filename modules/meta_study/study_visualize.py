""" [fig] Visualize strategies - plot and save/show
Manager, to study different variants

Input: indicator_name, source_symbols, source_params, study_type
Output: [fig] Plot (save/show) that visualizes the strategy
"""

from modules.file_handler import *
from modules.course import get_symbol_paths
from modules.params import get_all_params_combinations_from_yaml
from modules.plot import fig_type1_default, fig_type2_indicator, save_fig
from modules.strategy.evaluate_invested import get_evaluation_invested_statistics
from modules.strategy.strategy_invested import func_get_invested_from_indicator


#---------------------- Manger for Visualization ----------------------#

def manager_visualize_strategy(indicator_name, source_symbols, source_params, study_type='params'):
    """ [Loop fig] Manager to plot and save (visualize) strategies
    :param indicator_name: indicator name
    :param source_symbols: multiple sources possible: course_selection_key / list symbol_names
    :param source_params: different sources possible - key_course_selection / list_params_combinations / None (default key_course_selection)
    :param study_type: for folder structure - params/symbols or symbols/params
    """
    # Prepare variables
    # Symbols
    symbol_paths = get_symbol_paths(source_symbols)
    # Param combinations
    if isinstance(source_params, str):  # key from yaml
        params_combinations = get_all_params_combinations_from_yaml(indicator_name, source_params)
    elif isinstance(source_params, list):  # already a list of params_combinations
        params_combinations = source_params
    elif source_params is None:  # default params
        params_combinations = get_all_params_combinations_from_yaml(indicator_name, 'default')
    else:
        raise ValueError(f'Wrong instance (not [str, list, None] of source_params: {source_params}')


    # Loop over symbols and params
    if study_type == 'params':
        # params oriented -> one param with many symbols
        i = 1
        l_p = len(params_combinations)
        l_s = len(symbol_paths)
        for i_p, params in enumerate(params_combinations):
            for i_s, symbol_path in enumerate(symbol_paths):
                print(f'{i}/{l_s * l_p}: \t\t {i_p + 1}/{l_p} {params} \t\t {i_s + 1}/{l_s}: {symbol_path.stem}')
                routine_visualize_strategy(symbol_path, indicator_name, params, study_type)
                i += 1
                print()
    elif study_type == 'symbols':
        # symbols oriented -> one symbol with many params
        i = 1
        l_s = len(symbol_paths)
        l_p = len(params_combinations)
        for i_s, symbol_path in enumerate(symbol_paths):
            for i_p, params in enumerate(params_combinations):
                print(f'{i}/{l_s * l_p}: \t\t {i_s + 1}/{l_s}: {symbol_path.stem} \t\t {i_p + 1}/{l_p} {params}')
                routine_visualize_strategy(symbol_path, indicator_name, params, study_type)
                i += 1
                print()
    else:
        raise ValueError(f'study_type must be [params, symbols]: {study_type}')



def routine_visualize_strategy(symbol_path:Path, indicator_name:str, params:dict, study_type='params') -> None:
    """ [fig] Main routine for the visualization study
    :param symbol_path: path to symbol
    :param indicator_name: indicator name
    :param params: 1x params for one indicator
    :param study_type: [params, symbols]
    :return: None
    """
    # full df - df[close, <indicators>, signal, invested]
    df = _calc_indicator_and_invested(symbol_path, indicator_name, params)
    # evaluation - {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    evaluation_dict = _calc_evaluation(df)
    # file path - data/analyse/visualize/...
    file_path = _calc_file_path(indicator_name, symbol_path.stem, params, study_type)
    # title
    evaluation_dict_str = _calc_evaluation_to_str(evaluation_dict)

    # Plot
    save_plot = True
    show_plot = False
    fig = fig_type2_indicator(df, indicator_name, symbol_path.stem, params, evaluation_dict_str)
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
    df = func_get_invested_from_indicator(indicator_name, df, params)
    # print(df)
    return df


def _calc_evaluation(df) -> dict:
    """ [fig] Calculate evaluation
    :param df: df[invested]
    :return: dict evaluation - e.g. {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    """
    evaluation_dict = get_evaluation_invested_statistics(df)
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


def _calc_file_path(indicator_name, symbol, params, study_type='params') -> Path:
    """ [fig] Calculate file path for the plot
    Aim: Centralized storage that creates a collection across different test runs

    :param indicator_name: indicator name
    :param symbol: symbol (course)
    :param params: params (1x dict)
    :param study_type: [params, symbols]
    :return: path to save the plot
    """
    params_str = _calc_params_to_str(params) # params as string
    # Calculate folder path
    if study_type == 'params': # params oriented (for one param there are many symbols)
        file_path = get_path() / f'data/analyse/visualize/{study_type}/{indicator_name}/{params_str}/{symbol}.png'
    elif study_type == 'symbols': # symbols oriented (for one symbol there are many params
        file_path = get_path() / f'data/analyse/visualize/{study_type}/{indicator_name}/{symbol}/{params_str}.png'
    else:
        raise ValueError(f'study_type must be [params, symbols]: {study_type}')
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
    manager_visualize_strategy('MACD', 'default', 'visualize', study_type='symbols')

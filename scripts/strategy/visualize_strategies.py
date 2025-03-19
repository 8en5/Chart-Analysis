
from modules.strategy.strategy_invested import *
from modules.file_handler import *
from modules.params import *
from modules.strategy.strategy_visualize import VisualizeStrategy
from modules.strategy.evaluate_invested import get_evaluation_statistics


def _calc_folder_path(indicator_name, source, symbol, param_study):
    base_folder_path = get_path('ws') / 'data/analyse/visualize' / indicator_name
    if param_study:
        folder_path = base_folder_path / 'parameter_study' / symbol
    else:
        folder_path = base_folder_path / 'symbols' / source
    return folder_path

def _calc_file_name(index, symbol, params):
    # Set file name - '{counter}_{symbol}_param1-value1_param2-value2'
    file_name = f'{index}_{symbol}'  # # 1_ETH
    if params is not None:
        for key, value in params.items():  # e.g. '1_ETH_bb_l-5_bb_std-1.5'
            file_name += f'_{key}-{value}'
    return file_name

def _calc_title_from_evaluation(result):
    return f"S = {result['stage_strategy_mean']:.2f} | Diff_BaH = {result['stage_diff_benchmark_mean']:.2f}"


if __name__ == "__main__":
    """ # Explanation
    There are 4 different main logics based on the two bools param_study and loop_symbols
    
        # Instructions
    - set strategy name
    - set run_type (if symbol study and/or param study)
    - set folder_path from where the historical course data is loaded
    - call VisualizeStrategy.init(**kwargs) to set the needed parameters
        - show plot / save plot / plot type [1-default, 2-indicator, 3-specific] - to control the output
        - strategy name / symbol / params - for calculating the file name
    """

    indicator_name = 'BB'                                   # MACD, BB, RSI
    run_type = 3                                            # Program flow [1-4]
    source = 'yaml'                                         # [yaml, api]


    folder_path_course = get_path('cc') / source     # load symbols in this folder

    match run_type:
        case 1: # [F,F] plot one symbol with default params (for testing or specific analysis)
            param_study = False
            symbol_study = False
            print(f'<{run_type}> - plot one symbol with default params (for testing)')
        case 2: # [T,F] param study for one symbol (for testing the parameter study)
            param_study = True
            symbol_study = False
            print(f'<{run_type}> - param study for one symbol')
        case 3: # [F,T] loop symbols with default params (strategy with 1x specific params applied to all symbols)
            param_study = False
            symbol_study = True
            print(f'<{run_type}> - loop symbols with default params')
        case 4: # [T,T] loop symbols with param study (parameter study for all multiple courses)
            param_study = True
            symbol_study = True
            print(f'<{run_type}> - loop symbols with param study')
        case _:
            raise ValueError(f'run_type [1-4]: {run_type}')


    # Symbol study
    if symbol_study:
        # Symbol study (all symbols in folder)
        symbol_study_file_paths = list_file_paths_in_folder(folder_path_course, '.csv')
    else:
        # Default symbol
        default_symbol = 'BTC'
        symbol_study_file_paths = [folder_path_course / f'{default_symbol}.csv']

    # Params study
    if param_study:
        # Param study (get all param combinations from strategy name
        params_study = get_all_combinations_from_params_study(indicator_name, 'visualize')
    else:
        params_study = [None]

    #print(symbol_study_file_paths)
    #print(params_study)

    # Stop, if there are too many variations
    total_combinations = len(symbol_study_file_paths)*len(params_study)
    if total_combinations > 100:
        raise AssertionError(f'Over 100 symbols: "{total_combinations}" (Should there really be so many graphics created?)')

    # Loop over symbols and params
    i = 1
    l_s = len(symbol_study_file_paths)
    l_p = len(params_study)
    for i_s, symbol_file_path in enumerate(symbol_study_file_paths):
        symbol = symbol_file_path.stem
        for i_p, params in enumerate(params_study):
            print(f'{i}/{l_s * l_p}: \t\t {i_s+1}/{l_s}: {symbol} \t\t {i_p+1}/{l_p} {params}')

            # Run routine
            df = load_pandas_from_file_path(symbol_file_path)
            df = func_get_invested_from_indicator(indicator_name, df[['close']], params)
            evaluation = get_evaluation_statistics(df)
            vs = VisualizeStrategy(df)
            vs.init(indicator_name=indicator_name, plot_type=2)
            vs.init(folder_path=_calc_folder_path(indicator_name, source, symbol, param_study), filename=_calc_file_name(i, symbol, params))
            vs.init(title=_calc_title_from_evaluation(evaluation))
            #vs.init(show_plot=True, save_plot=False)       # init for show and no save
            vs.run()

            # Next cycle
            i += 1
            print()

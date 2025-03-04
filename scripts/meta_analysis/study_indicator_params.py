
# 4 lines of code, to run this file in a separate cmd over a bat script
import sys
from pathlib import Path
ws_dir = (Path(__file__).parent / "../..").resolve()  # Workspace
sys.path.insert(0, str(ws_dir))                # add ws to sys-path to run py-file in separate cmd

import pandas as pd
import numpy as np
from scipy.optimize import minimize

from modules.file_handler import *
from modules.strategy.manual_strategies import *
from modules.strategy.evaluate_strategy import get_evaluation_statistics


#---------------------- Evaluate Param over multiple courses ----------------------#




def _save_results(summary_dict, folder_path, file_name):
    # Summaries all results in one df
    df = pd.DataFrame(summary_dict)
    # Sort dict
    df_sorted = df.sort_values(by='stage_strategy_mean', ascending=False)
    # Save result to file
    save_pandas_to_file(df_sorted, folder_path, file_name, 'txt')


#---------------------- Study 1 - Brute Force ----------------------#

def study_brute_force():
    #strategy_name = strategy_name
    params_study = get_all_combinations_from_params_study(strategy_name, 'brute_force')

    # Location results
    folder_path = get_path() / 'data/analyse/study_indicator_params' / strategy_name
    file_name = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Run study
    summary_dict = {}
    for index, params in enumerate(params_study):
        try:
            result = eval_param_with_symbol_study(strategy_name, params)
            result['params'] = params
            print(
                f'{index + 1}/{len(params_study)}: {params} \t\t'
                f'S: {result['stage_strategy_mean']:.2f} \t\t'
                f'diff: {result['stage_diff_benchmark_mean']:.2f}'
            )
            # Append all results in one dict
            for key, value in result.items():
                if key not in summary_dict:
                    summary_dict[key] = []
                summary_dict[key].append(value)
            # Save intermediate results
            if index % 50 == 0:
                _save_results(summary_dict, folder_path, file_name)
        except Exception as e:
            print(f'Error occurred, currently no error handling - param: {params}')
            print(str(e))

    # Summaries all results
    df = pd.DataFrame(summary_dict)
    print(df)
    _save_results(summary_dict, folder_path, file_name)



#---------------------- Study 2 - Optimization algorithms ----------------------#

def _cost_function(p:list):
    params = convert_params_list_in_dict(p)
    cost = eval_param_with_symbol_study(strategy_name, params)['stage_diff_benchmark_mean'] # cost function = diff to benchmark
    # Print
    p = [round(float(x), 2) for x in p]
    print(f'{p} \t\t {cost:.2f}')
    return -cost


def convert_params_list_in_dict(values:list):
    """ Convert param list (from optimization) to dict (for study)
    :param values: list of params
    :return: dict of params

    Input: e.g. MACD
        [12. 26. 90.]
    Output:
        {'m_fast': np.float64(12.0), 'm_slow': np.float64(26.0), 'm_signal': np.float64(90.0)}
    """
    # Get keys from another dict
    keys = params_study_dict[strategy_name]['brute_force'].keys()
    if len(keys) != len(values):
        raise ValueError(f'list {values} and dict {keys} have different lengths')
    params = dict(zip(keys, values))
    return params


def optimization(method, initial_params):
    # Optimization with an optimization algorithm
    result = minimize(_cost_function, initial_params, method=method)

    # Result
    optimal_params = result.x
    minimum_value = result.fun
    print("Optimum parameter:", optimal_params)
    print("Minimal cost function:", minimum_value)

    return f'{optimal_params} \t\t {minimum_value}'


def study_optimization():
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
    method = 'Nelder-Mead'

    # Save results
    folder_path = get_path() / 'data/analyse/optimization' / strategy_name
    file_name = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
    create_dir(folder_path)
    file_path = folder_path / f'{file_name}.txt'

    # Multiple starting points for the optimization
    list_initial_params = get_all_combinations_from_params_study(strategy_name, 'optimization')


    for index, initial_params in enumerate(list_initial_params):

        initial_params = {
            'm_fast': 12,
            'm_slow': 26,
            'm_signal': 90 # 9
        }

        log = f'{index+1}/{len(list_initial_params)}: {initial_params}'
        with open(file_path, "a") as file:
            file.write(log + '\n')
        print(log)

        # Change dict to np.array for optimization algorithm
        initial_params = np.array(list(initial_params.values()))

        # Optimization
        log = optimization(method, initial_params)
        with open(file_path, "a") as file:
            file.write(log + '\n\n')
        print(log, '\n')

        exit()


if __name__ == "__main__":
    strategy_name = 'MACD'

    #study_brute_force()
    study_optimization()
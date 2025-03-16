import pandas as pd
import json

from modules.file_handler import get_path
from modules.meta_study.eval_indicator_param import BruteForce


def study_brute_force():
    strategy_names = ['MACD', 'BB', 'RSI']
    course_selection_keys = ['default']
    file_path = get_path() / 'data' / f'running_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'

    # Real-time metadata of the study
    meta_dict = {
        'meta': {
            'start': pd.Timestamp.now().strftime("%Y/%m/%d %H:%M:%S"),
            'time_estimated [h]': 0,
            'end': '',
            'time_real [h]': ''
        },
        'study': {
            #'indicator/course_selection': {
             #   'time_per_step [s]': '',
             #   'total_combinations': '',
             #   'time_estimated [h]': '',
             #   'start': '',
             #   'end': '',
             #   'time_real [h]': ''
            #}
        }
    }

    # Calculate the estimated study time
    n_test_samples = 9
    for strategy_name in strategy_names:
        for course_selection_key in course_selection_keys:
            print(f'Test: {strategy_name} - {course_selection_key }')
            bf = BruteForce(strategy_name, course_selection_key, False) # no saving
            time_one_iteration = bf.test_time_per_iteration(n_test_samples) / n_test_samples
            time_estimated = time_one_iteration * len(bf.params_variations) / 3600
            meta_dict['study'][f'{strategy_name}/{course_selection_key}'] = {
                'time_one_iteration [s]': time_one_iteration,
                'total_combinations': len(bf.params_variations),
                'time_estimated [h]': time_estimated,
                'start': '',
                'end': '',
                'time_real [h]': ''
            }
            meta_dict['meta']['time_estimated [h]'] += time_estimated

    with open(file_path, 'w') as file:
        file.write(json.dumps(meta_dict, indent=4))

    # Run study
    for strategy_name in strategy_names:
        for course_selection_key in course_selection_keys:
            d = meta_dict['study'][f'{strategy_name}/{course_selection_key}']
            d['start'] = pd.Timestamp.now().strftime("%Y/%m/%d %H:%M:%S")
            bf = BruteForce(strategy_name, course_selection_key, True)
            bf.run()
            d['end'] = pd.Timestamp.now().strftime("%Y/%m/%d %H:%M:%S")
            d['time_real [h]'] = (pd.to_datetime(d['end'],format="%Y/%m/%d %H:%M:%S") - pd.to_datetime(d['start'],format="%Y/%m/%d %H:%M:%S")).total_seconds() / 3600

            with open(file_path, 'w') as file:
                file.write(json.dumps(meta_dict, indent=4))

    # Finish
    meta_dict['meta']['end'] = pd.Timestamp.now().strftime("%Y/%m/%d %H:%M:%S")
    meta_dict['meta']['time_real [h]'] = str((pd.to_datetime(meta_dict['meta']['end'], format="%Y/%m/%d %H:%M:%S") - pd.to_datetime(meta_dict['meta']['start'], format="%Y/%m/%d %H:%M:%S")).total_seconds() / 3600)
    with open(file_path, 'w') as file:
        file.write(json.dumps(meta_dict, indent=4))

#---------------------- Study 2 - Optimization algorithms ----------------------#

'''
from scipy.optimize import minimize

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
'''

if __name__ == "__main__":
    study_brute_force()
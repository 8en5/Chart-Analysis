
# 4 lines of code, to run this file in a separate cmd over a bat script
import sys
from pathlib import Path
ws_dir = (Path(__file__).parent / '../..').resolve()  # Workspace
sys.path.insert(0, str(ws_dir))                # add ws to sys-path to run py-file in separate cmd

from modules.meta_study.eval_indicator_param import BruteForce



def study_brute_force():
    strategy_names = ['MACD']
    course_selection_keys = ['default']

    BruteForce('MACD', 'default', True)




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
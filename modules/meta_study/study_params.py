
import pandas as pd
from collections import defaultdict

from modules.file_handler import *
from modules.params import *
from modules.course import get_courses_paths
from modules.error_handling import log_error
from modules.strategy.strategy_invested import *
from modules.strategy.evaluate_invested import get_evaluation_invested_statistics
from modules.meta_study.study_visualize import manager_visualize_strategies


def eval_param_with_symbol_study(indicator_name, params:dict, course_paths):
    """ [eval, 1x param, multiple symbols] Evaluate one param variation of an indicator over multiple courses
    Calculate 'EvaluateStrategy' (= Evaluation of one param variation with one symbol) over multiple courses (defined in
      stages). Then summarize the results over the multiple courses and calculate mean and std as meta result
      for this param variation

    :param indicator_name: strategy name
    :param params: 1x params dict of one indicator
    :param course_paths: list paths of the selected courses for the evaluation
    :return: dict meta result - mean and std as summary over multiple courses (from the most important values)

    Input:
        indicator_name + params -> One param variation (for the indicator)
    Process:
        calculate basic evaluation over multiple courses (depending on stage) and summarize them
        e.g.: Buy_and_Hold, Strategy_with_fee, diff_benchmark
    Output:
        Mean and std across multiple courses from the individual evaluations
        e.g.: Buy_and_Hold_mean, Buy_and_Hold_std, diff_benchmark_mean, diff_benchmark_std
    """
    # Constants
    offset = 400            # cut data from df so that all parameter variations start with the same day (each param has a different startup time before they deliver signals)
    minimum_length = 600    # min data length for the study

    # Loop over all symbols and calculate meta evaluation
    summary_dict = {}
    for index, symbol_file_path in enumerate(course_paths):
        #print(f'{index + 1}/{len(symbol_study_file_paths)}: {symbol_file_path.stem}')
        df = load_pandas_from_file_path(symbol_file_path)[['close']]
        df = func_get_invested_from_indicator(indicator_name, df, params)
        df = df[['close', 'invested']] # Cut df to the minimal relevant data
        if len(df) < minimum_length:
            raise AssertionError(f'The data of the course "{symbol_file_path.stem}" is too short: "{len(df)}". Remove it from the analysis')
        df = df.iloc[offset:] # offset for standardization - each parameter has a different startup time until signals are generated
        if df['invested'].isna().any(): # Observation, if there are any None values in df[invested]
            # if there are None Values in df[invested] this means, that there are no signals -> increase offset
            raise AssertionError(f'Warning for param {params}: Check offset, there should be no None vales in df[invested]: {df}')
        result = get_evaluation_invested_statistics(df)
        # Append all results in one dict
        for key, value in result.items():
            if key not in summary_dict:
                summary_dict[key] = []
            summary_dict[key].append(value)
        # Clean up memory
        del df # delete

    # Summarize evaluation
    """ e.g. for [ADA, BTC, ETH, LINK]
    df_summary = 
                  S       BaH      diff
        0  4.710666  5.545694 -0.835028
        1  4.205323  4.681915 -0.476592
        2  3.307129  6.934328 -3.627199
        3  2.998117  2.767857  0.230259
    """
    df_summary = pd.DataFrame(summary_dict)
    #print(df_summary)

    # Result as dict
    result_dict = df_summary.mean().to_dict()
    min = False # decide manually if min or full evaluation
    if min:
        """result_dict = {'S': 3.81, 'BaH': 4.98, 'diff': -1.18}"""
        #print(json_round_dict(result_dict))
    else:
        # Insert course names (first column)
        course_names = get_names_from_paths(course_paths)
        df_summary.insert(0, 'symbol', pd.Series(course_names))
        result_dict_extra = {
            'params': params,
            'courses': df_summary.set_index('symbol').to_dict(orient='index')
        }
        result_dict.update(result_dict_extra)
        """{'S': 3.81, 'BaH': 4.98, 'diff': -1.18, 'params': {'m_fast': 2.0, 'm_slow': 15.0, 'm_signal': 1.0}, 'courses': {'BTC': {'S': 1.0, 'BaH': 5.55, 'diff': -4.55}, 'ETH': {'S': 1.0, 'BaH': 4.68, 'diff': -3.68}, 'ADA': {'S': 1.0, 'BaH': 6.93, 'diff': -5.93}, 'LINK': {'S': 1.0, 'BaH': 2.77, 'diff': -1.77}}}"""
        #print(json_round_dict(result_dict))
    #print(json_dump_nicely(result_dict))
    return result_dict



def study_params_brute_force(indicator_name:str, course_selection_key:str, init=False):
    """ [Meta, param study, loop param_variation] Collect metadata for the study and start routine
    :param indicator_name: indicator name
    :param course_selection_key: key params from yaml
    :param init: init over test samples - if test set is ok, time estimation and metadata
    :return: None
    """
    course_selection_paths = get_courses_paths(course_selection_key)
    param_selection = 'brute_force'     # [brute_force, (visualize, optimization)]
    params_variations = get_all_params_variations_from_yaml(indicator_name, param_selection)

    # Save results
    folder_path_param_study = get_last_created_folder_in_dir('study') / f'{indicator_name}_{course_selection_key}'
    file_name_param_study = f'{indicator_name}_{course_selection_key}_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    file_path = folder_path_param_study / file_name_param_study

    # Init or run
    time_start = pd.Timestamp.now()
    key = f'{indicator_name}_{course_selection_key}'
    if init:
        # Init - test samples to test the functionality and get the time estimation for the project
        test_samples = 100
        print(f'Start init tests for {indicator_name}_{course_selection_key} over {test_samples} samples')
        routine_param_study_brute_force(indicator_name, course_selection_paths, params_variations[0:test_samples], file_path, False)
        time_end = pd.Timestamp.now()
        time_per_iteration = (time_end - time_start).total_seconds() / test_samples
        # Meta dict
        meta_dict = {
            'meta': {
                'params': get_params_from_yaml(indicator_name, param_selection),
                'total_param_combinations': len(params_variations),
                'courses': get_names_from_paths(course_selection_paths),
            },
            'pre_study_estimation': {
                f'time_test_samples_{test_samples} [s]': (time_end - time_start).total_seconds(),
                'time_per_iteration [s]': time_per_iteration,
                'estimated_time [h]': time_per_iteration * len(params_variations) / 3600
            }
        }
    else:
        # Run real study
        print(f'Start real study for {indicator_name}_{course_selection_key} over {len(params_variations)} samples')
        time_end = pd.Timestamp.now()
        time_per_iteration = (time_end - time_start).total_seconds() / len(params_variations)
        routine_param_study_brute_force(indicator_name, course_selection_paths, params_variations, file_path, True)
        # Meta dict
        meta_dict = {
            'real_study': {
                'time_real [h]': (time_end - time_start).total_seconds() / 3600,
                'time_per_iteration [s]': time_per_iteration,
                'start': time_start.strftime('%Y/%m/%d %H:%M:%S'),
                'end': time_end.strftime('%Y/%m/%d %H:%M:%S'),
            }
        }
    return key, meta_dict


def routine_param_study_brute_force(indicator_name:str, course_selection_paths:list[Path], params_variations:list[dict], file_path:[Path], save:[bool]) -> None:
    """ [param study, loop param_variation] Start routine for the param study
    :param indicator_name: indicator name
    :param course_selection_paths: list of the course paths (symbol paths)
    :param params_variations: list of dicts of params
    :param file_path: file path for the results
    :param save: whether results should be saved
    :return: None
    """
    #params_variations = params_variations[0:10]    # Testing - cut to min data
    # Run study
    summary_dict = defaultdict(list)
    for index, params in enumerate(params_variations):
        try:
            # Calculate param evaluation over multiple courses
            result_dict = eval_param_with_symbol_study(indicator_name, params, course_selection_paths)
            print(
                f'{index + 1}/{len(params_variations)}: \t\t'  # index
                f'{json_round_dict(result_dict)}' # print result dict in one line ->    1/11776: [1.04, 5.06, -4.02, {'rsi_l': 5.0, 'bl': 10.0, 'bu': 50.0}]
            )
            # Append all results in one dict as list
            for key, value in result_dict.items():
                summary_dict[key].append(value)

            # Save intermediate results and delete summary_dict
            if save and index % 500 == 0:
                save_summary_dict(summary_dict, file_path)
        except Exception as e:
            print(f'Error occurred for param: {params}')
            log_error(e, True, get_last_created_folder_in_dir('study'))

    # Finish
    if save:
        # Save summary
        save_summary_dict(summary_dict, file_path)

        # Visualize best parameters
        visualize_summary_dict(indicator_name, course_selection_paths, summary_dict)


def save_summary_dict(summary_dict:dict, file_path:Path) -> None:
    """ [file save] Save intermediate result
    summary_dict -> convert to df -> sort df -> save df to file

    :param summary_dict: evaluation results (over multiple symbols)
    :param file_path: storage location
    :return: None
    """
    # Round to 2 decimals
    summary_dict = json_round_dict(summary_dict)
    # Summaries all results in one df
    df = pd.DataFrame(summary_dict)
    # Sort dict
    df_sorted = df.sort_values(by='S', ascending=False)
    # Save result to file
    save_pandas_to_file(df_sorted, file_path.parent, file_path.stem)


def visualize_summary_dict(indicator_name, course_selection_paths, summary_dict):
    """ Plot the best n params from the param study
    :param indicator_name: indicator name
    :param course_selection_paths: paths of the course selection
    :param summary_dict: {'S': 3.81, 'BaH': 4.98, 'diff': -1.18, 'params': {'p_1': 10, 'p_2': 20}, 'courses': {'BTC': {'S': 4.71, 'BaH': 5.55, 'diff': -0.84}, ...}
    :return:
    """
    # TODO: Wenn Strategie 100% investiert ist, dann überspringen
    n = 5
    # Sort dict
    df = pd.DataFrame(summary_dict)
    df_sorted = df.sort_values(by='S', ascending=False)
    # Take the best n results
    list_params = df_sorted['params'].head(n).tolist()
    print(f'Start visualizing the best {n} params for the indicator {indicator_name}: {list_params}')
    manager_visualize_strategies(indicator_name, course_selection_paths, list_params, study_type='study')


if __name__ == "__main__":
    # Testing
    study_params_brute_force('MACD', 'default', False)
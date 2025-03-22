
import pandas as pd
from collections import defaultdict

from modules.file_handler import *
from modules.strategy.strategy_invested import *
from modules.strategy.evaluate_invested import get_evaluation_invested_statistics
from modules.params import *
from modules.course import get_courses_paths
from modules.error_handling import log_error


def eval_param_with_symbol_study(indicator_name, params:dict, symbols_paths):
    """ Evaluate one param variation of an indicator over multiple courses
    Calculate 'EvaluateStrategy' (= Evaluation of one param variation with one symbol) over multiple courses (defined in
      stages). Then summarize the results over the multiple courses and calculate mean and std as meta result
      for this param variation

    :param indicator_name: strategy name
    :param params: dict of the one specific param variation of the indicator
    :param symbols_paths: list paths of the selected courses for the evaluation
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
    for index, symbol_file_path in enumerate(symbols_paths):
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

    # Summarize evaluation
    df_summary = pd.DataFrame(summary_dict)
    #print(df_summary)

    # Result as dict
    result_dict = df_summary.mean().to_dict()
    return result_dict



def study_params_brute_force(indicator_name, course_selection_key, init=False):
    """ [param study]
    :param indicator_name: indicator name
    :param course_selection_key: key params from yaml
    :param init: init over test samples - 1) if test set is ok, 2) estimate time, 3) metadata
    :return: None
    """
    course_selection_paths = get_courses_paths(course_selection_key)
    param_selection = 'brute_force'     # [visualize, brute_force, optimization]
    params_variations = get_all_params_combinations_from_yaml(indicator_name, param_selection)

    # Save results
    folder_path_param_study = get_last_created_folder_in_dir('study') / f'{indicator_name}_{course_selection_key}'
    file_name_param_study = f'{indicator_name}_{course_selection_key}_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    file_path = folder_path_param_study / file_name_param_study

    # Init or run
    time_start = pd.Timestamp.now()
    key = f'{indicator_name}_{course_selection_key}'
    if init:
        # Init - test samples to test the functionality and get the time estimation for the project
        test_samples = 2
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
        routine_param_study_brute_force(indicator_name, course_selection_paths, params_variations[0:3], file_path, True)
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


def routine_param_study_brute_force(indicator_name, course_selection_paths, params_variations, file_path, save):
    # Run study
    summary_dict = defaultdict(list)
    for index, params in enumerate(params_variations):
        try:
            # Calculate param evaluation over multiple courses
            result = eval_param_with_symbol_study(indicator_name, params, course_selection_paths)
            result['params'] = params
            print(
                f'{index + 1}/{len(params_variations)}: \t\t'  # index
                f'{[round(v, 2) if isinstance(v, (int, float)) else v for v in result.values()]}' # print result dict in one line ->    1/11776: [1.04, 5.06, -4.02, {'rsi_l': 5.0, 'bl': 10.0, 'bu': 50.0}]
            )
            # Append all results in one dict as list
            for key, value in result.items():
                summary_dict[key].append(value)

            # Save intermediate results and delete summary_dict
            if save and index % 500 == 0:
                save_summary_dict(summary_dict, file_path)
        except Exception as e:
            print(f'Error occurred for param: {params}')
            log_error(e, True)

    # Finish
    if save:
        save_summary_dict(summary_dict, file_path)
    del summary_dict # delete


def save_summary_dict(summary_dict, file_path) -> None:
    """ [file save] Save intermediate result
    summary_dict -> convert to df -> sort df -> save df to file

    :param summary_dict: evaluation results (over multiple symbols)
    :param file_path: storage location
    :return: None
    """
    # Summaries all results in one df
    df = pd.DataFrame(summary_dict)
    # Sort dict
    df_sorted = df.sort_values(by='S', ascending=False)
    # Save result to file
    save_pandas_to_file(df_sorted, file_path.parent, file_path.stem)

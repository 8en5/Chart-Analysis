
from typing import Any
import pandas as pd
from pathlib import Path

from modules.utils import pandas_print_width, json_round_dict
from modules.file_handler import get_path, save_pandas_to_file
from modules.course import get_courses_paths
from modules.params import get_params_variation
from modules.error_handling import log_error
from modules.strategy.strategy_indicator_invested import indicator_invested


def manager_study_indicator_invested(indicator_name:str, source_courses:Any='default', source_params:Any='default',
                                     save_evaluation=False, save_plot=False, base_folder:Path=None) -> None:
    """ [Loop fig] Manager to plot and save (visualize) strategies
    :param indicator_name: indicator name
    :param source_courses: multiple sources possible: course_selection_key / list symbol_names / list symbol paths
    :param source_params: different sources possible - key_course_selection / list_params_variations / None (default key_course_selection) / 1x as dict / 1x as list
    :param save_evaluation: save evaluation results and visualize the best parameters
    :param save_plot: plot all parameters
    :param base_folder: base folder for the output
    """
    # Prepare variables (from different sources to one format)
    courses_paths = get_courses_paths(source_courses) # list of course paths for the study
    params_variations = get_params_variation(indicator_name, source_params) # list of param variations
    #print('courses_paths:', courses_paths)
    #print('params_variations:', params_variations)


    # Storage location for the results
    if not base_folder:
        base_folder = get_path() / f'data/study/_Temp'
    if isinstance(source_courses, str):
        folder_path_param_study = base_folder / f'{indicator_name}_{source_courses}'
        file_name_param_study = f'{indicator_name}_{source_courses}_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    else:
        folder_path_param_study = base_folder / f'{indicator_name}'
        file_name_param_study = f'{indicator_name}_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    file_path_param_study = folder_path_param_study / file_name_param_study


    # Run study over all params
    list_results = []
    for index, params in enumerate(params_variations):
        try:
            result = eval_indicator_invested_with_multiple_symbols(indicator_name, courses_paths, params, save_plot, folder_path_param_study)
            result = json_round_dict(result)
            print(
                f'{index + 1}/{len(params_variations)}: \t\t'  # index
                f"sorting: {result['sorting']}, params: {result['params']}"
            )
            list_results.append(result)

            # Save intermediate results
            if save_evaluation and index % 500 == 0:
                save_evaluation_results(list_results, file_path_param_study)

            """ Flatten result (of one param over multiple courses)
            df = pd.json_normalize(result['list_results'], sep='_')
            print(df)
            exit()
            """
        except Exception as e:
            print(f'Error occurred for param: {params}')
            log_error(e, True, folder_path_param_study)


    # Finish
    if save_evaluation:
        # Save all evaluations
        save_evaluation_results(list_results, file_path_param_study)
        if not save_plot: # if save_plot then all parameters are already saved
            # Plot the best params (call this currently running function again)
            n = 2
            list_params = get_best_params(list_results, n)
            print(f'Start visualizing the best {n} params for the indicator {indicator_name}: {list_params}')
            manager_study_indicator_invested(indicator_name, source_courses, list_params,
                                         save_evaluation=False, save_plot=True, base_folder=base_folder)


def eval_indicator_invested_with_multiple_symbols(
        indicator_name:str, course_paths:list, params: dict|list,
        save_plot=False, base_folder:Path=None) -> dict:
    """ [eval, invested, 1x param, n courses] valuate one param variation of an indicator over multiple courses
    :param indicator_name: indicator name
    :param course_paths: list of course paths
    :param params: 1x params
    :param save_plot: save plot
    :param base_folder: storage base folder
    :return: result dict (evaluation for 1x params over multiple courses)
    """
    OFFSET = 200
    list_results = []
    for index, course_path in enumerate(course_paths):
        #print(f'{index + 1}/{len(course_paths)}: {course_path.stem}')
        result = {
            'course': course_path.stem,
            **indicator_invested(indicator_name, course_path, params=params, offset=OFFSET,
                                 save_plot=save_plot, base_folder=base_folder)
        }
        list_results.append(result)
    #print(list_results)
    #exit()

    df_summary = pd.DataFrame(list_results)
    #print(df_summary)
    #exit()

    result_dict = {
        'sorting': df_summary['sorting'].mean(),  # mean of the sorted value over multiple courses
        'params': params,
        'list_results': list_results
    }
    #print(result_dict)
    #exit()
    return result_dict


def save_evaluation_results(list_results:list, file_path:Path) -> None:
    """ [file save] Save evaluation results (intermediate or full)
    list_results -> convert to df -> sort df -> save df to file

    :param list_results: evaluation results (over multiple symbols)
    :param file_path: file path
    :return: None
    """
    # Summaries all results in one df
    df_summary = pd.DataFrame(list_results)
    # Sort dict
    df_sorted = df_summary.sort_values(by='sorting', ascending=False)
    # Save result to file
    save_pandas_to_file(df_sorted, file_path.parent, file_path.stem)


def get_best_params(list_results:list, n=5):
    """ Return the best n params from study
    :param list_results: evaluation results (over multiple symbols)
    :param n: how many params
    :return: list of the best n params
    """
    # Summaries all results in one df
    df_summary = pd.DataFrame(list_results)
    # Sort dict
    df_sorted = df_summary.sort_values(by='sorting', ascending=False)
    # Return the best n params
    n = min(n, len(df_sorted)) # if n > len(df) then return all params in df
    list_params = df_sorted['params'].head(n).tolist()
    return list_params



if __name__ == "__main__":
    # Testing
    pandas_print_width()

    #manager_study_indicator_invested('MACD', 'default', None)

    manager_study_indicator_invested('MACD', 'default', 'visualize',
                                     save_evaluation=True, save_plot=False, base_folder=None)
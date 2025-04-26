
from typing import Any
import pandas as pd
from pathlib import Path

from modules.utils import pandas_print_width, json_round_dict, json_dump_nicely
from modules.file_handler import get_path, save_pandas_to_file
from modules.course import get_courses_paths
from modules.params import get_params_variation
from modules.error_handling import log_error
from modules.strategy.signals.strategy_indicator_signals import indicator_signals
from modules.strategy.signals.evaluate_signals import *
from modules.plot import save_fig
from modules.strategy.utils_study import calc_file_path


def manager_study_indicator_signals(
        indicator_name:str, source_courses:Any= 'default', source_params:Any= 'default',
        save_evaluation=False, save_plot=False, base_folder:Path=None, signal_type='all') -> None:
    """ [Loop fig] Manager to plot and save (visualize) strategies
    :param indicator_name: indicator name
    :param source_courses: multiple sources possible: course_selection_key / list symbol_names / list symbol paths
    :param source_params: different sources possible - key_course_selection / list_params_variations / None (default key_course_selection) / 1x as dict / 1x as list
    :param save_evaluation: save evaluation results and visualize the best parameters
    :param save_plot: plot all parameters
    :param signal_type: for plotting [all, buy, sell]
    :param base_folder: base folder for the output
    """
    # Prepare variables (from different sources to one format)
    courses_paths = get_courses_paths(source_courses) # list of course paths for the study
    params_variations = get_params_variation(indicator_name, source_params) # list of param variations
    #print('courses_paths:', courses_paths)
    #print('params_variations:', params_variations)


    # Storage location for the results
    if save_evaluation:
        if not base_folder:
            base_folder = get_path('study') / '_Temp' / f'Study_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'

        file_name_param_study = f'{indicator_name}_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        file_path_param_study = base_folder / file_name_param_study
        #print(file_path_param_study)
        #exit()

    # Run study over all params
    list_results = []
    for index, params in enumerate(params_variations):
        try:
            result = eval_indicator_signals_with_multiple_courses(indicator_name, courses_paths, params, save_plot, base_folder, signal_type)
            result = json_round_dict(result) # Warning - convert int key to str key (2 -> '2')
            print(
                f'{index + 1}/{len(params_variations)}: \t\t'  # index
                f'{result}'
            )
            list_results.append(result)

            # Save intermediate results
            if save_evaluation and index % 500 == 0:
                save_evaluation_results(list_results, file_path_param_study)

        except Exception as e:
            print(f'Error occurred for param: {params}')
            log_error(e, True, base_folder)

    # Finish
    if save_evaluation:
        # Save all evaluations
        save_evaluation_results(list_results, file_path_param_study)
        if not save_plot: # if save_plot then all parameters are already saved
            # Plot the best params (call this currently running function again)
            # Summaries all results in one df
            df_summary = pd.DataFrame(list_results)

            keys_signals = ['buy', 'sell']
            keys_times = list_results[0]['result_dict_states']['buy'].keys() # ['2', '5', '10', '30', '60', '120']
            keys_metric = ['return_mean', 'increase_perc']

            for signal in keys_signals:
                for time in keys_times:
                    for metric in keys_metric:
                        list_params = get_best_params(df_summary, signal, time, metric, 1)
                        folder = base_folder / signal / f'{time}_{metric}'
                        print(f'The best params for {signal}-{time}-{metric} is: {list_params}')
                        manager_study_indicator_signals(indicator_name, source_courses, list_params,
                                                        save_evaluation=False, save_plot=True, base_folder=folder,
                                                        signal_type=signal)


def eval_indicator_signals_with_multiple_courses(
        indicator_name:str, course_paths:list, params: dict|list,
        save_plot=False, base_folder:Path=None, signal_type='all') -> dict|None:
    """ [eval, invested, 1x param, n courses] valuate one param variation of an indicator over multiple courses
    :param indicator_name: indicator name
    :param course_paths: list of course paths
    :param params: 1x params
    :param save_plot: save plot
    :param base_folder: storage base folder
    :param signal_type: for plotting [all, buy, sell]
    :return: result dict (evaluation for 1x params over multiple courses)
    """
    OFFSET = 200
    list_results = []
    for index, course_path in enumerate(course_paths):
        #print(f'{index + 1}/{len(course_paths)}: {course_path.stem}')
        """
        result = {
            'course': course_path.stem,
            'list_returns': indicator_signals(indicator_name, course_path, params=params, offset=OFFSET,
                                 save_plot=save_plot, base_folder=base_folder)
        }
        """
        result = indicator_signals(indicator_name, course_path, params=params, offset=OFFSET,
                                   save_plot=save_plot, base_folder=base_folder, signal_type=signal_type)
        #print(result)
        #exit()
        list_results.append(result)

    #print(list_results)
    result_dict_returns = join_multiple_returns(list_results)
    #print(json_dump_nicely(result_dict_returns))

    # States over multiple courses
    result_dict_states = calc_states_from_dict(result_dict_returns)
    #print(json_dump_nicely(result_dict_states))
    #print(print_result_dict_states_as_df(result_dict_states))

    if save_plot:
        fig = fig_signals_evaluation(result_dict_states, signal_type)
        file_path = calc_file_path(indicator_name, '_multiple_courses', params, base_folder=base_folder)
        save_fig(fig, file_path)
        #plt.show()
        plt.close()


    result_dict = {
        'params': params,
        'result_dict_states': result_dict_states
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
    # Save result to file
    save_pandas_to_file(df_summary, file_path.parent, file_path.stem)


def get_best_params(df, signal_type, period, state='return_mean', n=2):
    values = []

    for idx, row in df.iterrows():
        #print(row)
        value = row['result_dict_states'][signal_type][period][state]
        values.append((idx, value))

    # Sort values
    mode = 'max' if signal_type == 'buy' else 'min'
    sorted_vals = sorted(values, key=lambda x: x[1], reverse=(mode == mode))

    # Top-N
    if n < len(df):
        top_n = sorted_vals[:n]
    else:
        top_n = sorted_vals
    top_values = [val for idx, val in top_n]
    top_indices = [idx for idx, val in top_n]
    top_params = [df.loc[idx, 'params'] for idx in top_indices]

    #print(top_values)
    #print(top_indices)
    #print(top_params)
    return top_params




if __name__ == "__main__":
    # Testing
    pandas_print_width()

    #manager_study_indicator_invested('MACD', 'default', None)

    manager_study_indicator_signals('MACD', 'default', 'visualize',
                                    save_evaluation=True, save_plot=False, base_folder=None)

    #manager_study_indicator_signals('BB', 'default', [5, 2.5],
     #                               save_evaluation=True, save_plot=False, base_folder=None)


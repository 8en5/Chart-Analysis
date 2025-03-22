
import pandas as pd

from modules.file_handler import *
from modules.strategy.strategy_invested import *
from modules.strategy.evaluate_invested import get_evaluation_invested_statistics
from modules.params import *
from modules.course import get_symbol_paths
from modules.error_handling import ErrorHandling


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
    offset = 400    # cut data from df so that all parameter variations start with the same day (each param has a different startup time before they deliver signals)

    # Loop over all symbols and calculate meta evaluation
    summary_dict = {}
    for index, symbol_file_path in enumerate(symbols_paths):
        #print(f'{index + 1}/{len(symbol_study_file_paths)}: {symbol_file_path.stem}')
        df = load_pandas_from_file_path(symbol_file_path)[['close']]
        df = func_get_invested_from_indicator(indicator_name, df, params)
        df = df[['close', 'invested']] # Cut df to the minimal relevant data
        if len(df) < 600:
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


class ResultManager:
    def __init__(self, indicator_name, course_selection_key, save=True):
        self.indicator_name = indicator_name
        self.course_selection_paths = get_symbol_paths(course_selection_key)

        param_selection = 'brute_force' # [visualize, brute_force, optimization]
        self.params_variations = get_all_params_combinations_from_yaml(indicator_name, param_selection)
        self.total_tests = len(self.params_variations)

        # Save results
        self.save = save
        self.folder_path = get_path() # overwrite in child
        self.file_name = f'{indicator_name}_{course_selection_key}_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'

        # Meta information for the study
        self.params_dict = get_params_from_yaml(indicator_name, param_selection)
        self.symbols = get_names_from_paths(self.course_selection_paths)
        self.time_start = pd.Timestamp.now()

        # Calculated in child class
        self.summary_dict = {} # overwrite in child

        # Error handling
        self.error_handling = ErrorHandling()


    def save_intermediate_result(self):
        """ Save intermediate result
        summary_dict -> df -> sort -> file
        """
        if not self.save:
            return
        # Summaries all results in one df
        df = pd.DataFrame(self.summary_dict)
        # Sort dict
        df_sorted = df.sort_values(by='S', ascending=False)
        # Save result to file
        save_pandas_to_file(df_sorted, self.folder_path, self.file_name)


    def finish(self):
        """ Save study result (meeta information + the best strategy)
        dict with result -> df -> append to summary file
        """
        # Make result dict (assemble from 3 parts)
          # Save meta information to this study
        result_dict_meta = {
            'indicator_name': self.indicator_name,
        }
          # Add first row (best result) of the study
        df = pd.DataFrame(self.summary_dict)
        df = df.sort_values(by='S', ascending=False)
        result_dict_row = df.iloc[0].to_dict()
          # Add more information to the end
        result_dict_end = {
            'start': self.time_start,
            'end': pd.Timestamp.now(),
            'total_tests': self.total_tests,
            'diff_total [h]': (pd.Timestamp.now() - self.time_start) / np.timedelta64(1, 'h'),
            'diff_test [s]': (pd.Timestamp.now() - self.time_start) / (np.timedelta64(1, 's') * self.total_tests),
            'selected_symbols': self.symbols,
            'params_dict': self.params_dict,
        }
          # Combine all dicts
        result_dict = {**result_dict_meta, **result_dict_row, **result_dict_end}

        # Print result
        print(result_dict)

        # Save to summary file
        if not self.save:
            return
        df = pd.DataFrame([result_dict])
        file = self.folder_path / '_summary.csv'
        print(f'{self.indicator_name} finished - save results to {file} \n')
        if not file.exists():
            df.to_csv(file, mode='w', header=True, float_format='%.3f', index=False)
        else:
            df.to_csv(file, mode='a', header=False, float_format='%.3f', index=False)



class BruteForce(ResultManager):
    def __init__(self, indicator_name, course_selection_key, save):
        super().__init__(indicator_name, course_selection_key, save)

        self.folder_path = get_path() / 'data/analyse/study_indicator_params/brute_force'


    def test_time_per_iteration(self, n) -> float:
        """ Calculates the average calculation time of one iteration
        :param n: number of samples to calculate average iteration time
        :return: average time per iteration
        """
        start = pd.Timestamp.now()
        for index, params in enumerate(self.params_variations[0:n]):
            result = eval_param_with_symbol_study(self.indicator_name, params, self.course_selection_paths)
            result['params'] = params
            print(
                f'Test + iteration time \t\t'
                f'{index + 1}/{len(self.params_variations)}: \t\t'  # index
                f'{[round(v, 2) if isinstance(v, (int, float)) else v for v in result.values()]}' # print result dict in one line ->    1/11776: [1.04, 5.06, -4.02, {'rsi_l': 5.0, 'bl': 10.0, 'bu': 50.0}]
            )
        end = pd.Timestamp.now()
        return (end - start).total_seconds()


    def run(self):
        summary_dict = {}
        for index, params in enumerate(self.params_variations):
            try:
                result = eval_param_with_symbol_study(self.indicator_name, params, self.course_selection_paths)
                result['params'] = params
                print(
                    f'{index + 1}/{len(self.params_variations)}: \t\t'  # index
                    f'{[round(v, 2) if isinstance(v, (int, float)) else v for v in result.values()]}' # print result dict in one line ->    1/11776: [1.04, 5.06, -4.02, {'rsi_l': 5.0, 'bl': 10.0, 'bu': 50.0}]
                )
                # Append all results in one dict
                for key, value in result.items():
                    if key not in summary_dict:
                        summary_dict[key] = []
                    summary_dict[key].append(value)
                # Save intermediate results
                if index % 200 == 0:
                    self.summary_dict = summary_dict
                    self.save_intermediate_result()
            except Exception as e:
                print(f'Error occurred for param: {params}')
                self.error_handling.log_error(e, False)
                exit()

        # Finish
        self.summary_dict = summary_dict
        self.save_intermediate_result()
        self.finish()

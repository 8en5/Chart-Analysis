
import numpy as np

from modules.file_handler import *
from modules.strategy.manual_strategies import get_all_combinations_from_params_study, func_manual_strategy
from modules.strategy.evaluate_strategy import get_evaluation_statistics


def _eval_param_with_symbol_study(strategy_name, params):
    # Loop over all symbols and calculate evaluation
    source = 'yaml'
    folder_path_course = get_path('course_cc') / source  # load symbols in this folder
    symbol_study_file_paths = list_file_paths_in_folder(folder_path_course, '.csv')
    summary_dict = {}
    for index, symbol_file_path in enumerate(symbol_study_file_paths):
        #print(f'{index + 1}/{len(symbol_study_file_paths)}: {symbol_file_path.stem}')
        df = load_pandas_from_file_path(symbol_file_path)
        df = func_manual_strategy(strategy_name, df[['close']], params)
        if df['invested'].isna().all(): # no buy or sell signals for this param - df[invested] is fully None
            continue
        evaluation = get_evaluation_statistics(df[['close', 'invested']])
        # Append all results in one dict
        for key, value in evaluation.items():
            if key not in summary_dict:
                summary_dict[key] = []
            summary_dict[key].append(value)

    # Summarize evaluation
    df_summary = pd.DataFrame(summary_dict)
    #print(df_summary)
    result = {
        'strategy_mean': df_summary['strategy_mean'].mean(),
        'strategy_std': np.sqrt(np.mean(np.square(df_summary['strategy_std']))),
        'diff_benchmark_mean': df_summary['diff_benchmark_mean'].mean(),
        'diff_benchmark_std': np.sqrt(np.mean(np.square(df_summary['diff_benchmark_std']))),
    }
    #print(result)
    return result


if __name__ == "__main__":
    strategy_name = 'BB'
    params_study = get_all_combinations_from_params_study(strategy_name)

    summary_dict = {}
    for index, params in enumerate(params_study):
        result = _eval_param_with_symbol_study(strategy_name, params)
        print(f'{index + 1}/{len(params_study)}: {params} \t {result['strategy_mean']:.2f} \t {result['diff_benchmark_mean']:.2f}')
        # Append all results in one dict
        for key, value in result.items():
            if key not in summary_dict:
                summary_dict[key] = []
            summary_dict[key].append(value)

    df = pd.DataFrame(summary_dict)
    print(df)


from modules.file_handler import *
from modules.strategy.manual_strategies import get_all_combinations_from_params_study, func_manual_strategy
from modules.strategy.evaluate_strategy import get_evaluation_statistics


def _eval_param_with_symbol_study(strategy_name, params):
    # Loop over all symbols and calculate evaluation
    source = 'yaml'
    folder_path_course = get_path('course_cc') / source  # load symbols in this folder
    symbol_study_file_paths = list_file_paths_in_folder(folder_path_course, '.csv')
    means = []
    for index, symbol_file_path in enumerate(symbol_study_file_paths):
        #print(f'{index + 1}/{len(symbol_study_file_paths)}: {symbol_file_path.stem}')
        df = load_pandas_from_file_path(symbol_file_path)
        df = func_manual_strategy(strategy_name, df[['close']], params)
        if df['invested'].isna().all(): # no buy or sell signals for this param - df[invested] is fully None
            continue
        evaluation = get_evaluation_statistics(df[['close', 'invested']])
        means.append(evaluation.loc['mean'])

    # Summarize evaluation
    df_summarize = pd.DataFrame(means)
    mean_overall = df_summarize.mean()
    std_overall = df_summarize.std(ddof=1)
    
    return {'params': params, **mean_overall.add_suffix('_mean').to_dict(), **std_overall.add_suffix('_std').to_dict()}



if __name__ == "__main__":
    strategy_name = 'MACD'
    params_study = get_all_combinations_from_params_study(strategy_name)
    
    summary = []
    for index, params in enumerate(params_study):
        result_one_param = _eval_param_with_symbol_study(strategy_name, params)
        print(f'{index + 1}/{len(params_study)}: {params} \t {result_one_param['Strategy_with_fee_mean']:.2f} \t {result_one_param['diff_benchmark_mean']:.2f}')
        summary.append(result_one_param)

    df = pd.DataFrame(summary)
    print(df)
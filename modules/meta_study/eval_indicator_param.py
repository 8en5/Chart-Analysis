

def eval_param_with_symbol_study(strategy_name, params:dict, symbols_file_paths):
    """ Evaluate one param variation of an indicator over multiple courses
    Calculate 'EvaluateStrategy' (= Evaluation of one param variation with one symbol) over multiple courses (defined in
      stages). Then summarize the results over the multiple courses and calculate mean and std as meta result
      for this param variation

    :param strategy_name: strategy name
    :param params: dict of the one specific param variation of the indicator
    :return: dict meta result - mean and std as summary over multiple courses (from the most important values)

    Input:
        strategy_name + params -> One param variation (for the indicator)
    Process:
        calculate basic evaluation over multiple courses (depending on stage) and summarize them
        e.g.: Buy_and_Hold, Strategy_with_fee, diff_benchmark
    Output:
        Mean and std across multiple courses from the individual evaluations
        e.g.: Buy_and_Hold_mean, Buy_and_Hold_std, diff_benchmark_mean, diff_benchmark_std
    """
    # Constants
    offset = 400    # cut data from df so that all parameter variations start with the same day (each param has a different startup time before they deliver signals)
    source = 'crypto_stage1'

    # Loop over all symbols and calculate meta evaluation
    folder_path_courses = get_path() / 'data/course' / source  # load symbols in this folder
    if not folder_path_courses.exists():
        print(f'Error: Folder "{folder_path_courses}" does not exist')
        sys.exit()
    symbol_study_file_paths = list_file_paths_in_folder(folder_path_courses, '.csv')
    summary_dict = {}
    for index, symbol_file_path in enumerate(symbol_study_file_paths):
        #print(f'{index + 1}/{len(symbol_study_file_paths)}: {symbol_file_path.stem}')
        df = load_pandas_from_file_path(symbol_file_path)
        df = func_manual_strategy(strategy_name, df[['close']], params)
        df = df[['close', 'invested']] # Cut df to the minimal relevant data
        if len(df) < 600:
            raise AssertionError(f'The data of the course "{symbol_file_path.stem}" is too short: "{len(df)}". Remove it from the analysis')
        df = df.iloc[offset:] # offset for standardization - each parameter has a different startup time until signals are generated
        if df['invested'].isna().any(): # Observation, if there are any None values in df[invested]
            # if there are None Values in df[invested] this means, that there are no signals -> increase offset
            raise AssertionError(f'Warning for param {params}: Check offset, there should be no None vales in df[invested]: {df}')
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
        'stage_strategy_mean': df_summary['strategy_mean'].mean(),
        #'stage_strategy_std': np.sqrt(np.mean(np.square(df_summary['strategy_std']))),
        'stage_diff_benchmark_mean': df_summary['diff_benchmark_mean'].mean(),
        #'stage_diff_benchmark_std': np.sqrt(np.mean(np.square(df_summary['diff_benchmark_std']))),
    }
    #print(result)
    return result


class ResultManagerEvalIndicatorParam:
    def __init__(self, strategy_name, source_course_selection, study_info):
        self.strategy_name = strategy_name
        self.source_course_selection = source_course_selection
        self.study_info = study_info



import pandas as pd

from modules.utils import pandas_print_width
pandas_print_width()


def evaluate_signals(df):
    # cut df to relevant columns
    df = df[['close', 'signal']].copy()
    # use numeric index
    df.index = range(len(df))

    eval_dict_signals = {
        'buy': [],
        'sell': []
    }
    for index, row in df.iterrows():
        if row['signal'] in ['buy', 'sell', 'bullish', 'bearish']:
            eval_dict_one_signal = {
                'index': index,
                'close': row['close'],
                **evaluate_signal(index, df)
            }
            if row['signal'] in ['buy', 'bullish']:
                eval_dict_signals['buy'].append(eval_dict_one_signal)
            else:
                eval_dict_signals['sell'].append(eval_dict_one_signal)

    df_buy = pd.json_normalize(eval_dict_signals['buy'])
    print(df_buy)


def evaluate_signal(index, df):
    times = [-30, -14, -7, 7, 14, 30, 60, 120, 180]
    eval_dict_one_signal = {}
    for time in times:
        close = df['close'].loc[index]
        index_time = index + time # e.g. 36+(-14) or 39 +30
        if time < 0:                 # go back
            if index_time >= 0:      # check index not negative
                df_period = df[index_time: index+1].copy()
                eval_dict_one_signal[time] = min_max_perc(close, df_period)
            else:
                eval_dict_one_signal[time] = None
        else:                        # go in the future
            if index_time+1 < len(df): # check index smaller then len(df)
                df_period = df[index: index_time+1].copy()
                eval_dict_one_signal[time] = min_max_perc(close, df_period)
            else:
                eval_dict_one_signal[time] = None
    return eval_dict_one_signal


def min_max_perc(close, df):
    close_min = df['close'].min()
    close_max = df['close'].max()
    return round(close_min / close, 3) , round(close_max / close, 3)



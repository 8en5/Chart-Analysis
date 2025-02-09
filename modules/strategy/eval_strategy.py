"""
            close  invested  trade_occurred  close_perc strategy_status
date
2023-01-01      1         0           False         NaN
2023-01-02      2         1            True    1.000000            out+
2023-01-03      4         1           False    1.000000             in+
2023-01-04      3         0            True   -0.250000             in-
2023-01-05      6         0           False    1.000000            out+
2023-01-06      8         0           False    0.333333            out+
2023-01-07      5         0           False   -0.375000            out-
2023-01-08      4         1            True   -0.200000            out-
2023-01-09      3         1           False   -0.250000             in-
2023-01-10      4         1           False    0.333333             in+
2023-01-11      8         1           False    1.000000             in+
2023-01-12     12         1           False    0.500000             in+
2023-01-13     10         1           False   -0.166667             in-
"""

import numpy as np

from modules.utils import *

pandas_print_width()


def _calc_amount_transactions(df, freq=1) -> int:
    """
    :param df: df['invested']
    :return: amount of transaction per time unit (e.g. transactions/month)
    """
    total = (df['invested'] != df['invested'].shift()).sum() # sum all flank changes
    relative = int(total / freq)     # transactions per freq (e.g. t/month)
    return relative


def _calc_accumulated_perc(df, n=0):
    """ Accumulated return (last accumulated value equals total return)
    :param df: df['invested', 'close_perc']
    :param n: 0 - Buy and Hold | 1 - Strategy without fee | 2 - Strategy with fee
    :return: df['factor', 'accumulate']
    """
    df = df[['close', 'close_perc', 'invested']].copy()

    match n:
        case 0:
            # Buy and Hold
            df['factor'] = 1 + df['close_perc']
        case 1:
            # Strategy without fees
            df['factor'] = 1 + df['close_perc'] * df['invested'].shift(1)
        case 2:
            # Strategy with fees
            FEE = 0.004 # 0.4 %
            df['trade_occurred'] = df['invested'].diff().fillna(0).ne(0)
            df['factor_trading_fee'] = df['trade_occurred'].apply(lambda x: 1-FEE if x else 1)
            df['factor_without_fee'] = 1 + df['close_perc'] * df['invested'].shift(1)
            df['factor'] = df['factor_without_fee'] * df['factor_trading_fee']
        case _:
            raise ValueError(f'n should be between 0-2: {n}')

    df['accumulate'] = df['factor'].cumprod()
    return df


def _get_total_returns(df):
    total_return = {}
    total_return['Buy and Hold'] = _calc_accumulated_perc(df, 0)['accumulate'].iloc[-1]
    total_return['Strategy without fee'] = _calc_accumulated_perc(df, 1)['accumulate'].iloc[-1]
    total_return['Strategy with fee'] = _calc_accumulated_perc(df, 2)['accumulate'].iloc[-1]
    return total_return



def evaluate_strategy(df):
    """
    :param df: df[close, invested]
    :return:
    """
    df = df.copy()

    # Count amount of transaction (changes between in out)
    amount_transactions = _calc_amount_transactions(df)
    #print(amount_transactions, 30)

    # Calculate daily perc change from course
    df['close_perc'] = df['close'].pct_change(periods=1) #* 100

    # Calculate different states based on [in, out] (shift 1, because perc change after investment 1 day later)
    conditions = [
        (df['invested'].shift(1) == 1) & (df['close_perc'] > 0),  # in+ (invested and course rises)
        (df['invested'].shift(1) == 1) & (df['close_perc'] < 0),  # in- (invested and course falls)
        (df['invested'].shift(1) == 0) & (df['close_perc'] > 0),  # out+ (not invested and course rises)
        (df['invested'].shift(1) == 0) & (df['close_perc'] < 0),  # out- (not invested and course falls)
    ]
    values_type = ['in+', 'in-', 'out+', 'out-']
    df['invested_states'] = np.select(conditions, values_type, default='')
    pandas_print_all()
    print(df)
    exit()

    # Calculate the proportions of rising and falling prices
    total_perc_plus = sum(df.loc[df['close_perc'] > 0, 'close_perc'].to_list())
    total_perc_minus = sum(df.loc[df['close_perc'] < 0, 'close_perc'].to_list())

    eval_dict = {}
    for key in values_type:
        eval_dict[key] = {}
        list_perc = df.loc[df['invested_states'] == key, 'close_perc'].to_list() # list all corresponding percentages (from the 4 categories ['in+', 'in-', 'out+', 'out-']
        eval_dict[key]['sum'] = sum(list_perc)                                   # sum

        # Calculate portion (e.g. "invested and rising" / "all rising prices")
        if '+' in key:
            eval_dict[key]['portion'] = eval_dict[key]['sum'] / total_perc_plus * 100
        elif '-' in key:
            eval_dict[key]['portion'] = eval_dict[key]['sum'] / total_perc_minus * 100
        else:
            raise ValueError(f'no + or - in {key}')

    # two important numbers [%]: in and invested & out and not invested
    portions_dict = {key: value["portion"] for key, value in eval_dict.items()}
    print(portions_dict)
    print(_get_total_returns(df))
    exit()



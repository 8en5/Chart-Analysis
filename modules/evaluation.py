
import numpy as np

from modules.indicators import get_period
from modules.utils import pandas_print_all


def get_intervals(data_length):
    """ Calculate intervals with fixed length
    :param data_length: len(df)
    :return: intervals -> [(start1, end1), (start2, end2), ...]

    Input: 1000
    Output: [(0, 350), (250, 600), (500, 850)]
    """
    window_size = 350   # const period days
    overlap = 100       # days overlapping
    intervals = []      # summary of all intervals

    # Return only 1 interval, if length < window_size
    if data_length < window_size:
        return [(0, data_length)]

    # Start iterating
    start = 0
    while start + window_size < data_length:
        intervals.append((start, start + window_size))
        start += (window_size - overlap)
    return intervals



#------------------------- Evaluation -------------------------#
"""
Input: df[close, invested, close_perc]
"""

def calc_amount_transactions(df, period='') -> float:
    """
    :param df: df[invested]
    :param period: [D, 3D, W, ME, QE, YE]
    :return: amount of transaction per period

    Input:
        len(df) = 60 (60 days or 2 months)
        total_transactions = 20
    Output:
        -> 10 transactions / month
        -> 0.3 transactions / day
        -> ca 120 transactions / year
    """
    total_transactions = (df['invested'] != df['invested'].shift()).sum()  # sum all flank changes (0->1 and 1->0)
    if period == '':    # total
        return total_transactions
    freq = get_period(period) # D->1, W->7, M->30, ...
    num_periods = len(df) / freq  # number of periods in len(df) (e.g. len(df)=90 / freq=30 = 3
    return total_transactions / num_periods if num_periods > 0 else 0


def calc_all_investment_states(df) -> dict[str, float]:
    """ Portion [%] of the 4 investment states based on 'invested'
    :param df: df[invested, close_perc]
    :return: dict[in+, in-, out+, out-]

    based on the daily percentage changes in the course and the status of whether you are invested - sum over all 4 areas
    Output: {'in+': 52.73, 'in-': 47.72, 'out+': 42.52, 'out-': 49.49}
        Interpretation:
            - in+: 52.73 % of all increased percentages the strategy is invested        (good - should be high)
            - in-: 47.72 % of all increased percentages the strategy was not invested   (bad - should be low)
            - out+: 42.52 % of all fallen percentages the strategy is invested          (bad - should be low)
            - out-: 42.52 % of all fallen percentages the strategy is not invested      (good - should be high)
    """
    #df = df.copy()
    # Calculate different states based on [in, out]
    """
                       close invested  close_perc invested_states
    date                                                         
    2010-08-29       0.06400        0   -0.009288            out-
    2010-08-30       0.06497        0    0.015156            out+
    2010-08-31       0.06000        0   -0.076497            out-
    2010-09-01       0.06290        1    0.048333             in+
    2010-09-02       0.06340        1    0.007949             in+
    2010-09-03       0.06085        1   -0.040221             in-
    2010-09-04       0.06238        1    0.025144             in+
    """
    conditions = [
        (df['invested'] == 1) & (df['close_perc'] > 0),  # in+ (invested and course rises)
        (df['invested'] == 1) & (df['close_perc'] < 0),  # in- (invested and course falls)
        (df['invested'] == 0) & (df['close_perc'] > 0),  # out+ (not invested and course rises)
        (df['invested'] == 0) & (df['close_perc'] < 0),  # out- (not invested and course falls)
    ]
    values_type = ['in+', 'in-', 'out+', 'out-']
    df['invested_states'] = np.select(conditions, values_type, default='')


    # Calculate the proportions of rising and falling prices
    """
    sum(in+) / +    (ratio in+ to all ricing courses)
    sum(in-) / -    (ratio in- to all fallen courses)
    sum(out+) / +   (ratio out+ to all ricing courses)
    sum(out-) / -   (ratio out- to all fallen courses)
    """
    # sum of all ricing and sum of all fallen courses
    total_perc_plus = sum(df.loc[df['close_perc'] > 0, 'close_perc'].to_list())     # sum of all ricing courses
    total_perc_minus = sum(df.loc[df['close_perc'] < 0, 'close_perc'].to_list())    # sum of all fallen courses
    # calculate ratio
    eval_dict = {}
    for key in values_type: # ['in+', 'in-', 'out+', 'out-']
        eval_dict[key] = {}
        list_perc = df.loc[df['invested_states'] == key, 'close_perc'].to_list()  # list of all percentages respectively from the 4 categories ['in+', 'in-', 'out+', 'out-']
        eval_dict[key]['sum'] = sum(list_perc)  # sum the list
        # Calculate portion (e.g. "invested and rising" / "all rising prices")
        if '+' in key:
            eval_dict[key]['portion'] = eval_dict[key]['sum'] / total_perc_plus * 100
        elif '-' in key:
            eval_dict[key]['portion'] = eval_dict[key]['sum'] / total_perc_minus * 100
        else:
            raise ValueError(f'no + or - in {key}')

    # summarize data in dict {'in+': 52.73, 'in-': 47.72, 'out+': 42.52, 'out-': 49.49}
    return {key: value["portion"] for key, value in eval_dict.items()}


def calc_accumulated_perc(df, n=2):
    """ Accumulated return (last accumulated value equals total return)
    :param df: df['invested', 'close_perc']
    :param n: 0 - Buy and Hold | 1 - Strategy without fee | 2 - Strategy with fee | 3 - Strategy with fee and tax
    :return: df['factor', 'accumulate']
    """
    # Check
    if df['invested'].isna().any(): # if None or NaN in df[invested]
        raise ValueError(f'NaN or None in df[invested] - this will lead to errors in this function (take care of it beforehand)')

    df = df.copy()
    match n:
        case 0:
            # Buy and Hold
            df['factor'] = 1 + df['close_perc']
        case 1:
            # Strategy without fees
            df['factor'] = 1 + df['close_perc'] * df['invested']
        case 2:
            # Strategy with fees
            FEE = 0.004  # 0.4 %
            df['trade_occurred'] = df['invested'].diff().fillna(0).ne(0)
            df['factor_trading_fee'] = df['trade_occurred'].apply(lambda x: 1 - FEE if x else 1)
            df['factor_without_fee'] = 1 + df['close_perc'] * df['invested']
            df['factor'] = df['factor_without_fee'] * df['factor_trading_fee']
        case 3:
            # Strategy with fees and tax
            # TODO: Kapitalertragssteuer - 25% auf alle Gewinne (aber Verluste können gegen gerechnet werden)
            pass
        case _:
            raise ValueError(f'n should be between 0-3: {n}')

    df['accumulate'] = df['factor'].cumprod()
    return df


def calc_total_accumulated_perc(df, n=2) -> float:
    """ Last value of accumulated return
    :param df: see calc_accumulated_perc()
    :param n: see calc_accumulated_perc()
    :return: total return
    """
    # Call calc_accumulated_perc(df, n) and take the last accumulated value - this corresponds to the total return
    return calc_accumulated_perc(df, n)['accumulate'].iloc[-1]
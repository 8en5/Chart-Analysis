
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from modules.utils import get_period, get_intervals, pandas_print_all, json_round_dict
from modules.plot import fig_invested_default, save_fig


def evaluate_invested(df) -> dict[str, any]:
    """ [eval_dict df] Calculate evaluation_dict of one symbol with one param - df[invested]
    :param df: df[close, invested]
    :return: evaluation dict

    Input:    df[invested, close_perc, group_invested]
    Output:
        min: {'S': 12.53, 'BaH': 12.27, 'diff': 0.25, ...}
        all: {'start': Timestamp('2017-10-05 00:00:00'), 'end': Timestamp('2018-09-20 00:00:00'), 'days': 350, 'transactions': 22,
             'in+': 32.728, 'in-': 58.884, 'out+': 67.271, 'out-': 41.115,
             'S': 12.53, 'BaH': 12.27, 'diff': 0.25, ...}
    """

    # Check required columns
    minimal_columns = ['close', 'invested']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')
    # Check invested at least once
    """
    if not (df['invested'] == 1).any():
        print(f'Warning, never invested')
    """
    # df[close_perc]
    if 'close_perc' not in df.columns:
        df['close_perc'] = df['close'].pct_change(periods=1)  # * 100


    # Cut None values in df[invested]
    """
    df[invested] is not allowed to have None values, otherwise calculations in this function will fail.
    - None values are where the indicator does not yet provide any signals
    - Here to run the calculation, all None values re replaced with 0. But then this strategy (1x params of an indicator)
      is not comparable with the other parameters that can already make decisions at this point. Therefore make sure 
      beforehand that all parameters start with the same offset, so there are no None values
    """
    amount_none_values = df['invested'].isnull().sum()
    if amount_none_values > 0:
        print(f'Warning: Cut {amount_none_values}/{len(df)} values from None to 0 where there was no signal')
        df['invested'] = df['invested'].replace({None: 0})
    df.loc[:, 'invested'] = df['invested'].astype(int)  # because there is no None value, the column can be set to int

    # Shift close_perc by one (because the percentage change apply to the next day)
    """
          date invested  close_perc
    2017-11-08        0    0.3
    2017-11-09       <1>   0.5  <- first investment point, but close_perc refers to the percentage change from the last day (where you are not invested)
    2017-11-10        1   <0.1> <- this is the first percentage change when invested from 2017-11-09 to 2017-11-10
    2017-11-11        0    0.2  <- this is the second percentage
    -> shift close_perc one row up
    """
    df['close_perc'] = df['close_perc'].shift(-1)
    df = df.iloc[:-1] # delete the last row of df, because ot the shift(-1) there is no close_perc in the last column


    # Evaluation
    # Main evaluation values
    BaH = _calc_total_accumulated_perc(df, 0)  # Buy_and_Hold
    S = _calc_total_accumulated_perc(df, 2)    # Strategy_with_fee

    # Dict of all evaluation values
    min_calculations = True
    if min_calculations:
        result_dict = {
            'S': S,
            'BaH': BaH,
            'diff': S - BaH,
            '%_inv': (df['invested'] == 1).sum() / len(df)
        }
    else:
        # Calculate different states based on [{in, out}, {+, -}]
        portions_dict = _calc_all_investment_states(df)

        result_dict = {
                # Meta
            'start': df.index.min(),
            'end': df.index.max(),
            'days': (df.index.min() - df.index.max()).days,
            'transactions': _calc_amount_transactions(df),
                # Evaluation
            'in+': portions_dict['in+'],
            'in-': portions_dict['in-'],
            'out+': portions_dict['out+'],
            'out-': portions_dict['out-'],
            'Buy_and_Hold': _calc_total_accumulated_perc(df, 0),
            'Strategy_without_fee': _calc_total_accumulated_perc(df, 1),
            'Strategy_with_fee': _calc_total_accumulated_perc(df, 2),
            #'Strategy_with_fees_and_tax': calc_total_accumulated_perc(self.df, 3),
                # Comparability to the benchmark
            'diff_benchmark': S - BaH,
            #'ratio_benchmark': S / BaH,
            #'perc_benchmark': (S - BaH) / BaH,
            #'factor_benchmark': 1 + (S - BaH) / BaH if S > BaH else -(1 + (BaH - S) / S) if S < BaH else 1
            #'factor_benchmark': (S - BaH) / BaH if S > BaH else -(BaH - S) / S if S < BaH else 1
        }

    # Plot for debugging
    save = False
    show = False
    if show or save:
        fig = fig_invested_default(df, title=json_round_dict(result_dict))
        if save:
         save_fig(fig, None)
        if show:
            plt.show()

    # Return Evaluation as dict
    """
    result_dict = {'S': 12.53, 'BaH': 12.27, 'diff': 0.25, ...}
    """
    #print(result_dict)
    #exit()
    return result_dict



def evaluate_invested_multiple_cycles(df) -> (dict[str,float], pd.DataFrame):
    """ [eval_dict df] Run evaluation_dict multiple times in different periods and summarize the results
    :param df: df[close, invested]
    :return: evaluation dict as mean over multiple cycles and pd.DataFrame of all cycles

    Input:
        df[close, invested]
    Output 2:
        df_summary =
               start   end         S        BaH       diff     %_inv
            0      0   350  4.606851   2.800000   1.806851  0.515670
            1    250   600  0.980588   0.385714   0.594874  0.558405
            2    500   850  0.956191   1.292683  -0.336492  0.626781
            3    750  1100  2.549863   2.450000   0.099863  0.547009
            4   1000  1350  4.533366  18.234568 -13.701202  0.501425
            5   1250  1600  0.905994   0.840329   0.065665  0.455840
            6   1500  1850  0.505449   0.188147   0.317302  0.487179
            7   1750  2100  1.137066   0.637555   0.499511  0.538462
            8   2000  2350  2.242643   1.946237   0.296406  0.561254
            9   2250  2600  1.835778   1.500000   0.335778  0.495726

    Output 1:
        a) mean and std from multiple cycles
            df_stats =
                      Buy_and_Hold  Strategy_with_fee  diff_benchmark
                mean      2.862849           1.229129       -1.633720
                std       4.463157           1.417515        3.346977

        b) only mean from multiple cycles
            result_dict = {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    """

    # Iterate over multiple periods
    intervals = get_intervals(len(df))
    summary_dict = {}
    for index, interval in enumerate(intervals):
        # Period (start, stop)
        start = df.index[interval[0]]
        end = df.index[interval[1]]
        # Evaluation result of one specific interval
        result = {
            'start': interval[0],
            'end': interval[1],
            **evaluate_invested(df[start:end].copy())
        }
        # Append all results in one dict
        for key, value in result.items():
            if key not in summary_dict:
                summary_dict[key] = []
            summary_dict[key].append(value)
    df_summary = pd.DataFrame(summary_dict)
    #print(df_summary)
    #exit()

    # Result dict over multiple cycles
    # Mean and std
    """ mean and std from all numeric columns over multiple cycles
    df_stats = df_summary.select_dtypes(include=['number']).agg(['mean', 'std'])
    print(df_stats)
                    start          end         S       BaH      diff     %_inv
        mean  1125.000000  1475.000000  2.025379  3.027523 -1.002144  0.528775
        std    756.912589   756.912589  1.486954  5.412831  4.496627  0.048334
    
    """
    # Only mean
    """ Only mean from all numeric columns (standard deviation currently not because I don't know how to use it for the evaluation)
    result_dict = df_summary.select_dtypes(include=['number']).mean().to_dict()
    print(result_dict)
        result_dict = {'start': 1125.0, 'end': 1475.0, 'S': 2.03, 'BaH': 3.03, 'diff': -1.0, '%_inv': 0.53}
    """
    result_dict = df_summary.select_dtypes(include=['number']).mean().to_dict()
    for key in ['start', 'end']:
        result_dict.pop(key, None)
    return result_dict, df_summary



#------------------------- Evaluation of df[invested] -------------------------#
"""
Input: df[close, invested, close_perc]
"""

def _calc_amount_transactions(df, period='') -> float:
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


def _calc_all_investment_states(df) -> dict[str, float]:
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


def _calc_accumulated_perc(df, n=2):
    """ Accumulated return (last accumulated value equals total return)
    :param df: df['invested', 'close_perc']
    :param n: 0 - Buy and Hold | 1 - Strategy without fee | 2 - Strategy with fee | 3 - Strategy with fee and tax
    :return: df['factor', 'accumulate']
    """
    # Check
    if df['invested'].isna().any(): # if None or NaN in df[invested]
        raise ValueError(f'NaN or None in df[invested] - this will lead to errors in this function (take care of it beforehand)')

    df = df.copy() # working on a copy, because this function is called 1 - 3 times per basic evaluation and the columns in the df are not needed
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


def _calc_total_accumulated_perc(df, n=2) -> float:
    """ Last value of accumulated return
    :param df: see calc_accumulated_perc()
    :param n: see calc_accumulated_perc()
    :return: total return
    """
    # Call calc_accumulated_perc(df, n) and take the last accumulated value - this corresponds to the total return
    return _calc_accumulated_perc(df, n)['accumulate'].iloc[-1]


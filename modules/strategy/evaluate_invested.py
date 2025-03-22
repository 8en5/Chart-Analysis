
import pandas as pd
import numpy as np

from modules.utils import get_period, get_intervals, pandas_print_all
from modules.plot import fig_type1_default, save_fig


def evaluate_invested(df) -> dict[str, any]:
    """ [eval_dict df] Calculate evaluation_dict of one symbol with one param - df[invested]
    :param df: df[close, invested]
    :return: evaluation dict

    Input:    df[close, invested]
    Output:
        min: {'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
        all: {'start': Timestamp('2017-10-05 00:00:00'), 'end': Timestamp('2018-09-20 00:00:00'), 'days': 350, 'transactions': 22,
             'in+': 32.728, 'in-': 58.884, 'out+': 67.271, 'out-': 41.115,
             'S': 12.53, 'BaH': 12.27, 'diff': 0.25}
    """
    # Work on a copy, because this function is called several cycles
    df = df.copy()

    # Check None values in df[invested]
    """
    df[invested] must not have None values, otherwise calculations in this function will fail.
    - None values are where the indicator does not yet provide any signals
    - Here to run the calculation, all None values re replaced with 0. But then this strategy (1x params of an indicator)
      is not comparable with the other parameters that can already make decisions at this point. Therefore make sure 
      beforehand that all parameters start with the same offset, so there are no None values
    """
    amount_none_values = df['invested'].isnull().sum()
    if amount_none_values > 0:
        print(f'Warning: Cut {amount_none_values}/{len(df)} values from None to 0 where there was no signal')
        df = df.replace({None: 0})

    # Calculate daily perc change from course - df['close_perc']
    df['close_perc'] = df['close'].pct_change(periods=1)  # * 100

    # Main evaluation values
    BaH = calc_total_accumulated_perc(df, 0)  # Buy_and_Hold
    S = calc_total_accumulated_perc(df, 2)    # Strategy_with_fee

    # Dict of all evaluation values
    min_calculations = True
    if min_calculations:
        result_dict = {
            'S': S,
            'BaH': BaH,
            'diff': S - BaH,
        }
    else:
        # Calculate different states based on [{in, out}, {+, -}]
        portions_dict = calc_all_investment_states(df)

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
            'Buy_and_Hold': calc_total_accumulated_perc(df, 0),
            'Strategy_without_fee': calc_total_accumulated_perc(df, 1),
            'Strategy_with_fee': calc_total_accumulated_perc(df, 2),
            #'Strategy_with_fees_and_tax': calc_total_accumulated_perc(self.df, 3),
                # Comparability to the benchmark
            'diff_benchmark': S - BaH,
            #'ratio_benchmark': S / BaH,
            #'perc_benchmark': (S - BaH) / BaH,
            #'factor_benchmark': 1 + (S - BaH) / BaH if S > BaH else -(1 + (BaH - S) / S) if S < BaH else 1
            #'factor_benchmark': (S - BaH) / BaH if S > BaH else -(BaH - S) / S if S < BaH else 1
        }

    # Plot
    plot = False
    if plot:
        fig = fig_type1_default(df, '')
        save_fig(fig, None)

    # Return Evaluation as dict
    #print(result_dict)
    return result_dict



def run_evaluate_invested_multiple_cycles(df) -> pd.DataFrame:
    """ [eval_sum_cycle df] Run evaluation_dict multiple times in different periods and summarize the result
    :return: df_summary -> df[S, BaH, diff]

    Input:
        df[close, invested]
    Output
        All
               start        end  days  transactions        in+        in-       out+       out-  Buy_and_Hold  Strategy_without_fee  Strategy_with_fee
        0 2017-10-05 2018-09-20   350            22  32.728084  58.884625  67.271916  41.115375      3.718401              0.110469           0.101552
        1 2018-06-12 2019-05-28   350            30  49.721213  54.213025  50.278787  45.786975      0.564459              0.539257           0.480084
        2 2019-02-17 2020-02-02   350            32  50.156938  54.908679  49.843062  45.091321      1.350605              0.878070           0.775477
        3 2019-10-25 2020-10-09   350            31  48.398018  52.845813  51.601982  47.154187      2.456438              1.084703           0.961814
        4 2020-07-01 2021-06-16   350            41  43.589992  36.443157  56.410008  63.556843     15.198689              5.706372           4.861090
        5 2021-03-08 2022-02-21   350            37  53.025593  38.030742  46.974407  61.969258      0.766577              2.769912           2.397740
        6 2021-11-13 2022-10-29   350            31  58.074943  51.425244  41.925057  48.574756      0.204922              0.657962           0.583420
        7 2022-07-21 2023-07-06   350            32  50.641365  60.986784  49.358635  39.013216      0.557646              0.450793           0.398123
        8 2023-03-28 2024-03-12   350            33  40.723208  44.248819  59.276792  55.751181      2.031768              1.157571           1.018231
        9 2023-12-03 2024-11-17   350            31  40.902785  50.047369  59.097215  49.952631      1.778987              0.804957           0.713761

        Min
           Buy_and_Hold  Strategy_with_fee  diff_benchmark
        0      3.718401           0.101552       -3.616850
        1      0.564459           0.480084       -0.084376
        2      1.350605           0.775477       -0.575129
        3      2.456438           0.961814       -1.494624
        4     15.198689           4.861090      -10.337600
        5      0.766577           2.397740        1.631163
        6      0.204922           0.583420        0.378498
        7      0.557646           0.398123       -0.159523
        8      2.031768           1.018231       -1.013536
        9      1.778987           0.713761       -1.065226
    """
    # Check min columns
    minimal_columns = ['close', 'invested']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')

    # Remove all columns where df[invested] is None
    """
    df[invested] in the beginning always multiple None values
      (because the the indicators only provide signals after a certain amount of data)
    The None values in df[invested] can be used specifically to remove all columns where the indicators do not yet provide any values.
      (this has an impact on buy and hold, which also begins on the same day when the indicators deliver values)
    """
    df = df.dropna(subset=['invested']) # remove all rows in the beginning, where df[invested] is None - comparability to BaH
    if df.empty: # all entries are None
        raise ValueError(f'df[invested] only None values -> handle it earlier') # TODO weiß noch nicht wie ich damit umgehe (an welcher Stelle abfangen)
    df.loc[:, 'invested'] = df['invested'].astype(int) # because there is no None value, the column can be set to int

    # Iterate over multiple periods
    intervals = get_intervals(len(df))
    #print(len(df))
    #print(intervals)
    summary_dict = {}
    for index, interval in enumerate(intervals):
        start = df.index[interval[0]]
        end = df.index[interval[1]]
        result = evaluate_invested(df[start:end])

        # Append all results in one dict
        for key, value in result.items():
            if key not in summary_dict:
                summary_dict[key] = []
            summary_dict[key].append(value)
    df_summary = pd.DataFrame(summary_dict)
    #print(df_summary)
    return df_summary



def get_evaluation_invested_statistics(df) -> dict[str,float]:
    """ [eval_dict_cycle df] Calculate mean and std of the most important key figures from the evaluation
    :param df: df[close, invested]
    :return: result: mean and std from important key figures over multiple cycles
    """
    # Summarize all Evaluations in one df
    df_summary = run_evaluate_invested_multiple_cycles(df)
    #print(df_summary)

    # Statistics (mean and std from all number columns)
    """ mean and std from multiple cycles
          Buy_and_Hold  Strategy_with_fee  diff_benchmark
    mean      2.862849           1.229129       -1.633720
    std       4.463157           1.417515        3.346977
    df_stats = df_summary.select_dtypes(include=['number']).agg(['mean', 'std'])
    print(df_stats)
    """

    # Mean of all numeric columns (standard deviation currently not because I don't know how to use it for the evaluation)
    result_dict = df_summary.select_dtypes(include=['number']).mean().to_dict()
    #print(result_dict)

    return result_dict



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


def calc_total_accumulated_perc(df, n=2) -> float:
    """ Last value of accumulated return
    :param df: see calc_accumulated_perc()
    :param n: see calc_accumulated_perc()
    :return: total return
    """
    # Call calc_accumulated_perc(df, n) and take the last accumulated value - this corresponds to the total return
    return calc_accumulated_perc(df, n)['accumulate'].iloc[-1]
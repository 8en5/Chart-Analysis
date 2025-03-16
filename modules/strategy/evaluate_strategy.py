
import numpy as np
import pandas as pd

from modules.utils import *
from modules.evaluation import *
from modules.strategy.visualize_strategy import VisualizeStrategy

pandas_print_width()


class EvaluateStrategy:
    """
    Input:
        df[close, invested]
    Output
        All
            {'start': Timestamp('2017-10-05 00:00:00'), 'end': Timestamp('2018-09-20 00:00:00'), 'days': 350, 'transactions': 22,
             'in+': 32.728, 'in-': 58.884, 'out+': 67.271, 'out-': 41.115,
             'Buy_and_Hold': 3.718, 'Strategy_without_fee': 0.110, 'Strategy_with_fee': 0.101}
        Min
            {'Buy_and_Hold': 3.718, 'Strategy_with_fee': 0.101, 'diff_benchmark': -3.616}
    """

    def __init__(self, df):
        self.df = df.replace({None: 0})

        # Calculate daily perc change from course
        self.df['close_perc'] = self.df['close'].pct_change(periods=1)  # * 100

        # Main calculations
        BaH = calc_total_accumulated_perc(self.df, 0)  # Buy_and_Hold
        S = calc_total_accumulated_perc(self.df, 2)  # Strategy_with_fee

        min_calculations = True
        if min_calculations:
            self.result_dict = {
                'S': S,
                'BaH': BaH,
                'diff': S - BaH,
            }
        else:
            # Calculate different states based on [{in, out}, {+, -}]
            self.portions_dict = calc_all_investment_states(self.df)

            self.result_dict = {
                    # Meta
                'start': df.index.min(),
                'end': df.index.max(),
                'days': (df.index.min() - df.index.max()).days,
                'transactions': calc_amount_transactions(self.df),
                    # Evaluation
                'in+': self.portions_dict['in+'],
                'in-': self.portions_dict['in-'],
                'out+': self.portions_dict['out+'],
                'out-': self.portions_dict['out-'],
                'Buy_and_Hold': calc_total_accumulated_perc(self.df, 0),
                'Strategy_without_fee': calc_total_accumulated_perc(self.df, 1),
                'Strategy_with_fee': calc_total_accumulated_perc(self.df, 2),
                #'Strategy_with_fees_and_tax': calc_total_accumulated_perc(self.df, 3),
                    # Comparability to the benchmark
                'diff_benchmark': S - BaH,
                #'ratio_benchmark': S / BaH,
                #'perc_benchmark': (S - BaH) / BaH,
                #'factor_benchmark': 1 + (S - BaH) / BaH if S > BaH else -(1 + (BaH - S) / S) if S < BaH else 1
                #'factor_benchmark': (S - BaH) / BaH if S > BaH else -(BaH - S) / S if S < BaH else 1
            }

            self.plot = False
            if self.plot:
                self._plot()


    def get_result(self) -> dict[str,float]:
        #print(self.result_dict)
        return self.result_dict


    def _plot(self):
        """ Plot (debugging purposes)
        For evaluation, each strategy is split into several overlapping sections and the performance is calculated.
          This plot provides a visual insight into the calculation (plotting each section)
        Currently plots are saved under default folder and default name
        """
        vs = VisualizeStrategy(self.df)
        title = f"{self.result_dict['Strategy_with_fee']:.2f} | {self.result_dict['factor_benchmark']:.2f}"
        vs.init(title=title)
        vs.run()


def run_evaluation_multiple_cycles(df) -> pd.DataFrame:
    """ Run evaluation multiple times in different periods and summarize the result
    :return: df_summary -> df[start, end, days, amount_transactions, in+, in, out+, out-, Buy and Hold, Strategy without fee, Strategy with fee, factor_benchmark]

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
    df = df.dropna(subset=['invested']) # remove all rows in the beginning, where df[invested] is None
    if df.empty: # all entries are None
        raise ValueError(f'df[invested] only None values -> handle it earlier') # TODO weiß noch nicht wie ich damit umgehe (an welcher Stelle abfangen)
    df['invested'] = df['invested'].astype(int) # because there is no None value, the column can be set to int

    # Iterate over multiple periods
    intervals = get_intervals(len(df))
    #print(len(df))
    #print(intervals)
    summary_dict = {}
    for index, interval in enumerate(intervals):
        start = df.index[interval[0]]
        end = df.index[interval[1]]
        result = EvaluateStrategy(df[start:end]).get_result()

        # Append all results in one dict
        for key, value in result.items():
            if key not in summary_dict:
                summary_dict[key] = []
            summary_dict[key].append(value)
    df_summary = pd.DataFrame(summary_dict)
    #print(df_summary)
    return df_summary



def get_evaluation_statistics(df) -> dict[str,float]:
    """ Calculate mean and std of the most important key figures from the evaluation
    :param df: df[close, invested]
    :return: result: mean and std from important key figures over multiple cycles
    """
    # Summarize all Evaluations in one df
    df_summary = run_evaluation_multiple_cycles(df)
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
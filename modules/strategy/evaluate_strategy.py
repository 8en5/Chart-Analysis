
import numpy as np
import pandas as pd

from modules.utils import *
from modules.evaluation import *

pandas_print_width()


class EvaluateStrategy:
    def __init__(self, df):
        self.df = df[['close', 'invested']].copy().replace({None: 0})

        # Calculate daily perc change from course
        self.df['close_perc'] = self.df['close'].pct_change(periods=1)  # * 100

        # General information
        self.start_date = df.index.min()
        self.end_date = df.index.max()
        self.days_total = (self.end_date - self.start_date).days

        # Calculate amount of transactions
        self.amount_transactions = calc_amount_transactions(self.df)

        # Calculate different states based on [{in, out}, {+, -}]
        self.portions_dict = calc_all_investment_states(self.df)

        # Calculate accumulated percentages for benchmark (Buy and Hold), Strategy without fee and Strategy with fee
        self.total_return_dict = {
            'Buy_and_Hold': calc_total_accumulated_perc(self.df, 0),
            'Strategy_without_fee': calc_total_accumulated_perc(self.df, 1),
            'Strategy_with_fee': calc_total_accumulated_perc(self.df, 2),
            #'Strategy_with_fees_and_tax': calc_total_accumulated_perc(self.df, 3)
        }

        # Summarize result
        self.result_dict = {
            'start': self.start_date,
            'end': self.end_date,
            'days': self.days_total,
            'transactions': self.amount_transactions,
            'in+': self.portions_dict['in+'],
            'in-': self.portions_dict['in-'],
            'out+': self.portions_dict['out+'],
            'out-': self.portions_dict['out-'],
            'Buy_and_Hold': self.total_return_dict['Buy_and_Hold'],
            'Strategy without fee': self.total_return_dict['Strategy_without_fee'],
            'Strategy_with_fee': self.total_return_dict['Strategy_with_fee'],
            'diff_benchmark': self.total_return_dict['Strategy_with_fee'] - self.total_return_dict['Buy_and_Hold']
        }

    def get_result(self):
        #df_result = pd.DataFrame(self.result_dict, index=[0])
        #return df_result
        return self.result_dict


    @staticmethod
    def run_evaluation_multiple_cycles(df):
        """ Run evaluation multiple times in different periods and summarize the result
        :return: df_summary -> df[start, end, days, amount_transactions, in+, in, out+, out-, Buy and Hold, Strategy without fee, Strategy with fee, diff_benchmark]
        """
        df = df[['close', 'invested']].copy()

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
        return df_summary



def get_evaluation_statistics(df):
    """ Calculate mean and std of the most important key figures from the evaluation
    :param df: df[close, invested] (full df)
    :return:
    """
    # Summarize all Evaluations in one df
    df_summary = EvaluateStrategy.run_evaluation_multiple_cycles(df)
    #print(df_summary)

    # Statistics (mean and std from all number columns)
    stats = df_summary.select_dtypes(include=['number']).agg(['mean', 'std'])
    #print(stats)

    return stats


# TODO: diff_benchmark als Faktor und nicht absolut (es war 2x besser oder 0.3x schlechter, absolute Werte sagen weniger aus)
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
import pandas as pd

from modules.utils import *

pandas_print_width()


class EvaluateStrategy:
    def __init__(self, df):
        self.df = df.copy().replace({None: 0})

        # General information
        self.start_date = df.index.min()
        self.end_date = df.index.max()
        self.days_total = (self.end_date - self.start_date).days

        # Initialize variables, value assigned at runtime
        self.amount_transactions = 0
        self.portions_dict = {}
        self.total_return_dict = {}

        # Run
        self.main_routine()


    def main_routine(self):
        """
        Input: df[close, invested]
        Output: Key figures on the evaluation (in one specific period of time)
        """

        # Calculate amount of transaction (buy, sell)
        self._calc_amount_transactions()

        # Calculate daily perc change from course
        self.df['close_perc'] = self.df['close'].pct_change(periods=1)  # * 100

        # Calculate different states based on [{in, out}, {+, -}]
        self._calculate_all_investment_states()

        # Calculate accumulated percentages for benchmark (Buy and Hold), Strategy without fee and Strategy with fee
        self._calc_total_accumulated_perc()

        # Print result
        #print(self.df)
        #print(self.amount_transactions)
        #print(self.portions_dict)
        #print(self.total_return_dict)


    def get_result(self):
        """
        # Variant 1
        result_dict = {
            'start': self.start_date,
            'end': self.end_date,
            'days': self.days_total,
            'amount_transactions': self.amount_transactions,
            'portions_dict': [self.portions_dict],
            'total_return_dict': [self.total_return_dict]
        }
        """
        # Variant 2
        result_dict = {
            'start': self.start_date,
            'end': self.end_date,
            'days': self.days_total,
            'transactions': self.amount_transactions,
            'in+': self.portions_dict['in+'],
            'in-': self.portions_dict['in-'],
            'out+': self.portions_dict['out+'],
            'out-': self.portions_dict['out-'],
            'Buy and Hold': self.total_return_dict['Buy and Hold'],
            'Strategy without fee': self.total_return_dict['Strategy without fee'],
            'Strategy with fee': self.total_return_dict['Strategy with fee'],
            'diff_benchmark': self.total_return_dict['Strategy with fee'] - self.total_return_dict['Buy and Hold']
        }
        df_result = pd.DataFrame(result_dict, index=[0])
        return df_result


    def _calc_amount_transactions(self, freq=1):
        """
        :return: amount of transaction
        # TODO per time unit (e.g. transactions/month)
        """
        total = (self.df['invested'] != self.df['invested'].shift()).sum()  # sum all flank changes
        self.amount_transactions = total


    def _calculate_all_investment_states(self):
        df = self.df.copy()
        # Calculate different states based on [in, out]
        conditions = [
            (df['invested'] == 1) & (df['close_perc'] > 0),  # in+ (invested and course rises)
            (df['invested'] == 1) & (df['close_perc'] < 0),  # in- (invested and course falls)
            (df['invested'] == 0) & (df['close_perc'] > 0),  # out+ (not invested and course rises)
            (df['invested'] == 0) & (df['close_perc'] < 0),  # out- (not invested and course falls)
        ]
        values_type = ['in+', 'in-', 'out+', 'out-']
        df['invested_states'] = np.select(conditions, values_type, default='')
        self.df = df

        # Calculate the proportions of rising and falling prices
        total_perc_plus = sum(df.loc[df['close_perc'] > 0, 'close_perc'].to_list())
        total_perc_minus = sum(df.loc[df['close_perc'] < 0, 'close_perc'].to_list())

        eval_dict = {}
        for key in values_type:
            eval_dict[key] = {}
            list_perc = df.loc[df['invested_states'] == key, 'close_perc'].to_list()  # list all corresponding percentages (from the 4 categories ['in+', 'in-', 'out+', 'out-']
            eval_dict[key]['sum'] = sum(list_perc)  # sum
            # Calculate portion (e.g. "invested and rising" / "all rising prices")
            if '+' in key:
                eval_dict[key]['portion'] = eval_dict[key]['sum'] / total_perc_plus * 100
            elif '-' in key:
                eval_dict[key]['portion'] = eval_dict[key]['sum'] / total_perc_minus * 100
            else:
                raise ValueError(f'no + or - in {key}')

        # two important numbers [%]: in and invested & out and not invested
        self.portions_dict = {key: value["portion"] for key, value in eval_dict.items()}


    def _calc_accumulated_perc(self, n):
        """ Accumulated return (last accumulated value equals total return)
        Input: df['invested', 'close_perc']
        :param n: 0 - Buy and Hold | 1 - Strategy without fee | 2 - Strategy with fee
        :return: df['factor', 'accumulate']
        """
        df = self.df[['close', 'close_perc', 'invested']].copy()

        match n:
            case 0:
                # Buy and Hold
                df['factor'] = 1 + df['close_perc']
            case 1:
                # Strategy without fees
                df['factor'] = 1 + df['close_perc'] * df['invested'].shift(1)
            case 2:
                # Strategy with fees
                FEE = 0.004  # 0.4 %
                df['trade_occurred'] = df['invested'].diff().fillna(0).ne(0)
                df['factor_trading_fee'] = df['trade_occurred'].apply(lambda x: 1 - FEE if x else 1)
                df['factor_without_fee'] = 1 + df['close_perc'] * df['invested'].shift(1)
                df['factor'] = df['factor_without_fee'] * df['factor_trading_fee']
            case _:
                raise ValueError(f'n should be between 0-2: {n}')

        df['accumulate'] = df['factor'].cumprod()
        return df


    def _calc_total_accumulated_perc(self):
        total_return = {
            'Buy and Hold': self._calc_accumulated_perc(0)['accumulate'].iloc[-1],
            'Strategy without fee': self._calc_accumulated_perc(1)['accumulate'].iloc[-1],
            'Strategy with fee': self._calc_accumulated_perc(2)['accumulate'].iloc[-1]
        }
        self.total_return_dict = total_return


    @staticmethod
    def run_evaluation_multiple_cycles(df):
        """ Run evaluation multiple times in different periods and summarize the result
        :return: df_summary -> df[start, end, days, amount_transactions, in+, in, out+, out-, Buy and Hold, Strategy without fee, Strategy with fee, diff_benchmark]
        """
        df = df.copy()
        df = df.dropna(subset=['invested'])
        df['invested'] = df['invested'].astype(int)

        intervals = _get_intervals(len(df))
        df_summary = pd.DataFrame()
        for index, interval in enumerate(intervals):
            start = df.index[interval[0]]
            end = df.index[interval[1]]
            eval_strategy = EvaluateStrategy(df[start:end])
            df_summary = pd.concat([df_summary, eval_strategy.get_result()], ignore_index=True) # ignore_index=True set new ongoing index

        return df_summary


    @staticmethod
    def get_statistics(df):
        """ Calculate mean and std of the most important key figures from the evaluation
        :param df: df[close, invested] (full df)
        :return:
        """
        # Summarize all Evaluations in one df
        df_summary = EvaluateStrategy.run_evaluation_multiple_cycles(df)
        print(df_summary)

        # Extract the most important data for further calculation
        statistics_dict = {
            'strategy': df_summary['Strategy without fee'],
            'diff_benchmark': df_summary['diff_benchmark']
        }

        # Print result
        print()
        print('Strategy with fee:')
        print('\tMean:', statistics_dict['strategy'].mean())
        print('\tStd:', statistics_dict['strategy'].std())
        print('Diff_benchmark:')
        print('\tMean:', statistics_dict['diff_benchmark'].mean())
        print('\tStd:', statistics_dict['diff_benchmark'].std())
        exit()



def _get_intervals(data_length):
    """ Calculate intervals with fixed length
    :param data_length: len(df)
    :return: intervals -> [(start1, end1), (start2, end2), ...]
    """
    window_size = 350   # const period days
    overlap = 100       # periods overlapping
    intervals = []      # save all intervals

    # Return only 1 interval, if length < window_size
    if data_length < window_size:
        return [(0, data_length)]

    # Start iterating
    start = 0
    while start + window_size <= data_length:
        intervals.append((start, start + window_size))
        start += (window_size - overlap)
    return intervals
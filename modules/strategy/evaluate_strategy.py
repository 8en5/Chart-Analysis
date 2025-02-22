
import numpy as np
import pandas as pd

from modules.utils import *

pandas_print_width()


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


class EvaluateStrategy:
    def __init__(self, df):
        self.df = df[['close', 'invested']].copy().replace({None: 0})

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
        #self._calc_amount_transactions()

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
        result_dict = {
            #'start': self.start_date,
            #'end': self.end_date,
            #'days': self.days_total,
            #'transactions': self.amount_transactions,
            #'in+': self.portions_dict['in+'],
            #'in-': self.portions_dict['in-'],
            #'out+': self.portions_dict['out+'],
            #'out-': self.portions_dict['out-'],
            'Buy_and_Hold': self.total_return_dict['Buy_and_Hold'],
            #'Strategy without fee': self.total_return_dict['Strategy without fee'],
            'Strategy_with_fee': self.total_return_dict['Strategy_with_fee'],
            'diff_benchmark': self.total_return_dict['Strategy_with_fee'] - self.total_return_dict['Buy_and_Hold']
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
        df = self.df.copy()

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
            'Buy_and_Hold': self._calc_accumulated_perc(0)['accumulate'].iloc[-1],
            #'Strategy without fee': self._calc_accumulated_perc(1)['accumulate'].iloc[-1],
            'Strategy_with_fee': self._calc_accumulated_perc(2)['accumulate'].iloc[-1]
        }
        self.total_return_dict = total_return


    @staticmethod
    def _run_evaluation_multiple_cycles(df):
        """ Run evaluation multiple times in different periods and summarize the result
        :return: df_summary -> df[start, end, days, amount_transactions, in+, in, out+, out-, Buy and Hold, Strategy without fee, Strategy with fee, diff_benchmark]
        """
        df = df[['close', 'invested']].copy()

        df = df.dropna(subset=['invested']) # remove all rows, where df[invested] is None (until the strategy delivers signals)
        if df.empty: # all entries are None
            raise ValueError(f'df[invested] only None values -> handle it earlier') # TODO weiß noch nicht wie ich damit umgehe (an welcher Stelle abfangen)
        df['invested'] = df['invested'].astype(int) # because there is no None value, set the column to int

        intervals = _get_intervals(len(df))
        df_summary = pd.DataFrame()
        for index, interval in enumerate(intervals):
            start = df.index[interval[0]]
            end = df.index[interval[1]]
            eval_strategy = EvaluateStrategy(df[start:end])
            # TODO df_summary in Schleife als dict umsetzten und erst das fertige dict als pd.DataFrame speichern (Rechenleistung)
            df_summary = pd.concat([df_summary, eval_strategy.get_result()], ignore_index=True) # ignore_index=True set new ongoing index

        return df_summary



def get_evaluation_statistics(df):
    """ Calculate mean and std of the most important key figures from the evaluation
    :param df: df[close, invested] (full df)
    :return:
    """
    # Summarize all Evaluations in one df
    df_summary = EvaluateStrategy._run_evaluation_multiple_cycles(df)
    #print(df_summary)

    # Statistics
    stats = df_summary.select_dtypes(include=['number']).agg(['mean', 'std'])   # mean and std from all number columns
    #print(stats)
    #exit()

    return stats
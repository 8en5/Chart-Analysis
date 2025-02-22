from modules.utils import pandas_print_width
from test import *
from modules.evaluation import *


#------------------------- evaluation.py -------------------------#
def test_get_intervals():
    test_data_lengths = [2, 50, 400, 1000, 2000, 5000]
    for data_length in test_data_lengths:
        intervals = get_intervals(data_length)
        print(f'{data_length}: {intervals}')


def test_calc_amount_transactions():
    df = get_dummy_data_2()
    """
    len(df) = 365
    transactions = 188
    """
    #print(df)
    test_periods = ['', 'D', 'W', 'ME', 'QE', 'YE']
    for period in test_periods:
        trans_per_freq = calc_amount_transactions(df, period)
        print(f'{period}: {trans_per_freq}')


def test_calc_all_investment_states():
    df = get_dummy_data_strategy()
    #print(df)
    states = calc_all_investment_states(df)
    print(states)


def test_calc_accumulated_perc():
    #pandas_print_all()
    pandas_print_width()
    test_dict = {
        'Buy_and_Hold': 0,
        'Strategy_without fees': 1,
        'Strategy_with_fees': 2,
        #'Strategy_with_fees_and_tax': 3
    }
    for key, value in test_dict.items():
        df = get_dummy_data_strategy()
        df = calc_accumulated_perc(df[20:], value)  # df[20:0] to skip none values
        print(key)
        print(df)
        print('Total:', calc_total_accumulated_perc(df[20:], value))
        print('\n')



#------------------------- evaluate_strategy.py -------------------------#
from modules.strategy.evaluate_strategy import get_evaluation_statistics

def test_get_evaluation_statistics():
    df = get_dummy_data_strategy()
    df_summary = get_evaluation_statistics(df)
    print(df_summary)



if __name__ == "__main__":

    #test_get_intervals()
    #test_calc_amount_transactions()
    #test_calc_all_investment_states()
    #test_calc_accumulated_perc()

    test_get_evaluation_statistics()
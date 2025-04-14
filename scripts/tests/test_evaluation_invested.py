from modules.utils import *
from test import *

from modules.strategy.evaluate_invested import _calc_amount_transactions, _calc_all_investment_states, \
    _calc_accumulated_perc, _calc_total_accumulated_perc, evaluate_invested_multiple_cycles


#------------------------- evaluation.py -------------------------#

def test_get_intervals():
    test_data_lengths = [2, 50, 400, 1000, 2000, 5000]
    for data_length in test_data_lengths:
        intervals = get_intervals(data_length)
        print(f'{data_length}: {intervals}')


def test_calc_amount_transactions():
    df = get_dummy_data_random()
    """
    len(df) = 365
    transactions = 188
    """
    #print(df)
    test_periods = ['', 'D', 'W', 'ME', 'QE', 'YE']
    for period in test_periods:
        trans_per_freq = _calc_amount_transactions(df, period)
        print(f'{period}: {trans_per_freq}')


def test_calc_all_investment_states():
    df = get_dummy_data_course()
    #print(df)
    states = _calc_all_investment_states(df)
    print(states)


def test_calc_accumulated_perc():
    #pandas_print_all()
    pandas_print_width()
    test_dict = {
        'Buy_and_Hold': 0,
        'Strategy_without fees': 1,
        'Strategy_with_fees': 2,
        #'Strategy_with_fees_and_tax': 3 # TODO: Inbetriebnahme
    }
    for key, value in test_dict.items():
        df = get_dummy_data_course('BB', 'BTC')
        df = _calc_accumulated_perc(df, value)
        print(key)
        print(df)
        print('Total:', _calc_total_accumulated_perc(df, value))
        print('\n')



#------------------------- evaluate_strategy.py -------------------------#

def test_get_evaluation_statistics():
    df = get_dummy_data_course()
    df_summary = evaluate_invested_multiple_cycles(df)
    print(df_summary)



if __name__ == "__main__":

    # evaluation.py
    #test_get_intervals()
    #test_calc_amount_transactions()
    #test_calc_all_investment_states()
    test_calc_accumulated_perc()

    # evaluate_strategy.py
    #test_get_evaluation_statistics()
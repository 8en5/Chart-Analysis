import itertools
import numpy as np

from modules.plot import *
from modules.indicators import *
from modules.functional_analysis import *
from modules.utils import pandas_print_all

pd.set_option('future.no_silent_downcasting', True) # if values are converted down (value to nan - when calculating df[invested] based on df[signal])


params_study_dict = {
    'BB' : {
        'visualize': {
            'bb_l': [6],
            'bb_std': [1.5, 2.5]
        },
        'brute_force': {
            'bb_l': (5, 30, 5),
            'bb_std': (1.5, 2.5, 0.3)
        }
    },

    'MACD': {
        'visualize': {
            'm_fast': [10, 18],
            'm_slow': [20, 40],
            'm_signal': [30, 90]  # m_signal accidentally set to 90 (copy from rsi) -> really good param
        },
        'brute_force': {
            'm_fast': (2, 50, 3),
            'm_slow': (15, 200, 5),
            'm_signal': (1, 3, 0.2)
        },
        'optimization': {
            'm_fast': [2, 5, 15, 25],
            'm_slow': [15, 25, 50, 80, 100],
            'm_signal': [10, 30, 60, 90, 120]
        }
    },

    'RSI': {
        'visualize': {
            'rsi_l': [10, 14, 18],
            'bl': [20, 30, 40],
            'bu': [60, 70, 90]
        },
        'brute_force': {
            'rsi_l': (5, 100, 3),
            'bl': (10, 40, 2),
            'bu': (50, 95, 2)
        },
    },
}

def func_manual_strategy(strategy_name, *args):
    """ Call function set_manual_strategy_{strategy_name}()
    :param strategy_name: name for the strategy defined in this file
    :param args: *args for the func
    :return: set_manual_strategy_{strategy_name}
    """
    func_name = f'set_manual_strategy_{strategy_name}'
    # Check
    func = globals().get(func_name)
    if not callable(func):
        raise ValueError(f'The function "{func_name}" does not exist - define it in manual_strategies.py')
    # Return called function
    return func(*args)

def func_plot(strategy_name, *args):
    """
    :param strategy_name: name for the strategy defined in this file
    :param args: *args for the func
    :return: set_manual_plot_{strategy_name}
    """
    func_name = f'set_manual_plot_{strategy_name}'
    # Check
    func = globals().get(func_name)
    if not callable(func):
        raise ValueError(f'The function "{func_name}" does not exist - define it in manual_strategies.py')
    # Return called function
    return func(*args)


def get_params_from_dict(strategy_name, variant):
    """ Return params defined in params_study_dict
    :param strategy_name: dict[key]
    :param variant: dict[strategy_name][key]
    :return: dict of params
    """
    if strategy_name not in params_study_dict:
        raise ValueError(f'key "{strategy_name}" not in {params_study_dict}')
    if variant not in params_study_dict[strategy_name]:
        raise ValueError(f'key "{variant}" not in {params_study_dict[strategy_name]}')
    return params_study_dict[strategy_name][variant]

def get_all_combinations_from_params_study(strategy_name, variant):
    """ Return list of all params variations
    :param strategy_name: dict[key]
    :param variant: dict[strategy_name][key]
    :return: list of all params variations
    """
    # Get raw params and prepare it
    params_study = get_params_from_dict(strategy_name, variant)
    params_study = _set_param_variation(params_study)
    # Calculate all combinations
    keys = params_study.keys()
    values = params_study.values()
    combination = list(itertools.product(*values))
    combinations_list = [dict(zip(keys, combi)) for combi in combination]  # combination_list = [{self.params1}, {self.params2}, ... ]
    return combinations_list


def _set_param_variation(params_study: dict[str, list[float] | tuple[float, float, float]]) -> dict[str, list]:
    """ If present, converts a tuple (range) parameter set into a list.

    :param params_study: {key: [x,x,x], key: (start, end, step)}
    :return: dict all in format {key: [x,x,x]}
    """
    for key, value in params_study.items():
        if isinstance(value, tuple) and len(value) == 3:
            start, end, step = float(value[0]), float(value[1]), float(value[2])
            params_study[key] = [round(start + i * step, 10) for i in range(int((end - start) / step) + 1)]

    return params_study


def _calc_invested_from_signal(df):
    """ Calculate status 'invested' from signal
    :param df: df['signal']
    :return: df['invested']
    """

    """ Input                                                                                             Output
                  close  BBL_5_1.5  BBM_5_1.5  BBU_5_1.5   BBB_5_1.5  BBP_5_1.5   signal                invested
    date                                                                                
    2017-10-01  0.02519        NaN        NaN        NaN         NaN        NaN                             None    <- (leading None until indicator has only no None values)
    2017-10-02  0.02588        NaN        NaN        NaN         NaN        NaN                             None
    2017-10-03  0.02084        NaN        NaN        NaN         NaN        NaN                             None
    2017-10-04  0.02189        NaN        NaN        NaN         NaN        NaN                             None
    2017-10-05  0.02152   0.019978   0.023064   0.026150         NaN        NaN                             None
    2017-10-06  0.01849   0.018138   0.021724   0.025310   33.017230        NaN                             None
    2017-10-07  0.02080   0.018933   0.020708   0.022483   17.143734   0.525915                                0    <- this is the first row where the signal could deliver values (fill column with 0 starting from here until first signal)
    2017-10-08  0.02052   0.018869   0.020644   0.022419   17.193739   0.465065                                0
    2017-10-09  0.02207   0.018846   0.020680   0.022514   17.736032   0.878973  bullish                       0    <- first signal (fill column with 0 until this row)
    2017-10-10  0.02148   0.018846   0.020672   0.022498   17.664475   0.721273                                1    <- (buy and sell signals one day later, because percentage change you see on the next day)
    2017-10-11  0.02253   0.020351   0.021480   0.022609   10.515934   0.964844                                1
    2017-10-12  0.02635   0.019595   0.022590   0.025585   26.512972   1.127788  bearish                       1
    2017-10-13  0.03354   0.018431   0.025194   0.031957   53.687847   1.117029                                0
    2017-10-14  0.03221   0.019857   0.027222   0.034587   54.111225   0.838625  bullish                       0
    2017-10-15  0.03003   0.022901   0.028932   0.034963   41.692945   0.591025                                1
    """

    df['invested'] = None
    if df['signal'].isin(['bullish', 'bearish']).any():
        df['invested'] = df['signal'].replace({'bullish': 1, 'bearish': 0, '': None})
    elif df['signal'].isin(['buy', 'sell']).any():
        df['invested'] = df['signal'].replace({'buy': 1, 'sell': 0, '': None})

    # shift everything 1 day later (because percentage changes only apply to the next day)
    df['invested'] = df['invested'].shift(1)
    # fill the None values between the buy and sell signals
    df['invested'] = df['invested'].ffill() #.fillna(0)
    #df['invested'] = df['invested'].replace({np.nan: None}) # to be sure there is no nan (sometimes in first line because of shift)

    # Fill area with non-None values where there could have been signals
    """ 
    Signals only deliver values after a certain number of times.
    Fill the area with non-None values from when signals could in principle be present up to the first signal
    
    e.g. Leading None for MACD
    leading_nans = df.apply(lambda col: col.isna().cumprod().sum())
    print(leading_nans)
        close                                   0
        MACD_10_20_7                           19
        MACDh_10_20_7                          25
        MACDs_10_20_7                          25
        Crossing_MACD_10_20_7-MACDs_10_20_7     0
        signal                                  0
        invested                               40
    
    -> first signal could be there after 25 days, but is only there after 40 days
    => fill the days from 25 - 40 with 0
    As a result: if df[invested] is None, then mathematically there can't be a signal (important for benchmark comparison to buy and hold)
    """
    df_leading_nans = df.loc[:,df.columns!='invested'].apply(lambda col: col.isna().cumprod().sum()) # lists all none values of all columns (except invested)
    max_leading_nans = df_leading_nans.max() # largest number of leading None values (from there on signals could deliver values)
    if (df['signal'] != '').any():
        first_value = df['signal'][df['signal'] != ''].index[0] # index when signal delivers the first value
    else:
        first_value = df.index[-1]
    df.loc[df.index[max_leading_nans]:first_value, 'invested'] = 0

    #print(df)
    return df



#------------------------ BB ------------------------#
def set_manual_strategy_BB(df, params=None):
    if params is None:
        params = {
            'bb_l': 6,
            'bb_std': 2.0
        }

    # Indicator
    df = func_indicator('BB', df, length=params['bb_l'], std=params['bb_std'])
    col_l, col_m, col_u = get_indicator_col_names(df, 'BB')

    # Signals
    conditions = [
        (df['close'] <= df[col_l]),  # Bullish, if course is smaller than the lower band
        (df['close'] >= df[col_u])   # Bearish, if course is larger than the upper band
    ]
    values = ['bullish', 'bearish']
    df['signal'] = np.select(conditions, values, default='')

    # Invested [in, out] from signals
    df = _calc_invested_from_signal(df)
    #print(df)
    return df


#---------------------- MACD ----------------------#
def set_manual_strategy_MACD(df, params=None):
    if params is None:
        params = {
            'm_fast': 12,
            'm_slow': 26,
            'm_signal': 90 # 9
        }

    # Indicator
    df = func_indicator('MACD', df, fast=params['m_fast'], slow=params['m_slow'], signal=params['m_signal'])
    col_MACD, coll_diff, col_signal = get_indicator_col_names(df, 'MACD')

    # Signals
    df, col_crossing = calculate_crossings(df, col_MACD, col_signal)

    conditions = [
        (df[col_crossing] == 'up'),    # Buy, if MACD crosses the signal line from bottom to top
        (df[col_crossing] == 'down')   # Sell, if MACD crosses the signal line from top to bottom
    ]
    values = ['buy', 'sell']
    df['signal'] = np.select(conditions, values, default='')

    # Invested [in, out] from signals
    df =_calc_invested_from_signal(df)
    return df


#---------------------- RSI ----------------------#
def set_manual_strategy_RSI(df, params=None):
    if params is None:
        params = {
            'rsi_l': 14,
            'bl': 30,
            'bu': 70
        }

    # Indicator
    df = func_indicator('RSI', df, params['rsi_l'], params['bl'], params['bu'])
    col_RSI, col_bl, col_bu = get_indicator_col_names(df, 'RSI')

    # Signals
    conditions = [
        (df[col_RSI] < params['bl']), # Bullish, if course is smaller than 30 (lower border)
        (df[col_RSI] > params['bu'])  # Bearish, if course is bigger than 70 (upper border)
    ]
    values = ['bullish', 'bearish']
    df['signal'] = np.select(conditions, values, default='')

    # Invested [in, out] from signals
    df =_calc_invested_from_signal(df)

    return df

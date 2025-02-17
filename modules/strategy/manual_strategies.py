import itertools
import numpy as np

from modules.plot import *
from modules.indicators import *
from modules.functional_analysis import *
from modules.utils import pandas_print_all

pd.set_option('future.no_silent_downcasting', True) # if values are converted down (value to nan - when calculating df[invested] based on df[signal])


params_study_dict = {
    'BB' : {
        'bb_l': [6], #[5, 6, 8, 10, 15, 20, 30],
        'bb_std': [1.5, 2.5] #[1.5, 1.8, 2.0, 2.2, 2.5]
    },

    'MACD': {
            'm_fast': [10, 14, 18],
            'm_slow': [20, 30, 40],
            'm_signal': [7, 9, 12, 30, 90]  # m_signal accidentally set to 90 (copy from rsi) -> really good param
    },

    'RSI': {
            'rsi_l': [10, 14, 18],
            'bl': [20, 30, 40],
            'bu': [60, 7, 90]
    },
}

def get_func_manual_strategy(strategy_name, *args):
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

def get_func_plot(strategy_name, *args):
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
    # specified in 'manual_strategies.py'

def get_all_combinations_from_params_study(name):
    """ Return params_study defined in params_study_dict
    :param name: strategy name (key in dict)
    :return: list of all params variations
    """
    if name not in params_study_dict:
        raise ValueError(f'name "{name}" not in {params_study_dict}')
    # Get raw params and prepare it
    params_study = params_study_dict[name]
    params_study = _set_param_variation(params_study)
    # Calculate all combinations
    keys = params_study.keys()
    values = params_study.values()
    combination = list(itertools.product(*values))
    combinations_list = [dict(zip(keys, combi)) for combi in combination]  # combination_list = [{self.params1}, {self.params2}, ... ]
    return combinations_list


def _set_param_variation(params_study: dict[str,list[int]|tuple[int]]) -> dict[str,list]:
    """ If present, converts a tuple (range) parameter set into a list
    :param params_study: {key: [x,x,x], key: (start,end,step)}
    :return: dict all in format {key: [x,x,x]}
    """
    for key, value in params_study.items():
        if isinstance(value, tuple):
            start, end, step = map(int, value)
            params_study[key] = list(range(start, end + 1, step))
    return params_study


def _calc_invested_from_signal(df):
    """ Calculate status 'invested' from signal
    :param df: df['signal']
    :return: df['invested']
    """
    if df['signal'].eq('bullish').any():
        df['invested'] = df['signal'].replace({'bullish': 1, 'bearish': 0, '': None})
    elif df['signal'].eq('buy').any():
        df['invested'] = df['signal'].replace({'buy': 1, 'sell': 0, '': None})

    # shift everything 1 day later (because percentage changes only apply to the next day)
    df['invested'] = df['invested'].shift(1)
    df['invested'] = df['invested'].ffill() #.fillna(0)
    return df


#------------------------ BB ------------------------#
def set_manual_strategy_BB(df, params=None):
    if params is None:
        params = {
            'bb_l': 6,
            'bb_std': 2.0
        }

    df = df.copy()

    # Indicator
    df = indicator_BB(df, length=params['bb_l'], std=params['bb_std'])
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

    df = df.copy()

    # Indicator
    df = indicator_MACD(df, fast=params['m_fast'], slow=params['m_slow'], signal=params['m_signal'])
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

    df = df.copy()

    # Indicator
    df = indicator_RSI(df, params['rsi_l'], params['bl'], params['bu'])
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

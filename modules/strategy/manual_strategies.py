import itertools
import numpy as np

from modules.plot import *
from modules.indicators import *
from modules.functional_analysis import *


params_study_dict = {
    'BB' : {
        'bb_l': [5], #[5, 6, 8, 10, 15, 20, 30],
        'bb_std': [1.5] #[1.5, 1.8, 2.0, 2.2, 2.5]
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

def get_all_combinations_from_params_study(name):
    params_study = params_study_dict[name]
    keys = params_study.keys()
    values = params_study.values()
    combination = list(itertools.product(*values))
    combinations_list = [dict(zip(keys, combi)) for combi in combination]  # combination_list = [{self.params1}, {self.params2}, ... ]
    return combinations_list


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
    df['invested'] = df['signal'].replace({'bullish': 1, 'bearish': 0, '': np.nan})
    df['invested'] = df['invested'].ffill().fillna(0)
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
    df['invested'] = df['signal'].replace({'buy': 1, 'sell': 0, '': np.nan})
    df['invested'] = df['invested'].ffill().fillna(0)

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
    df['invested'] = df['signal'].replace({'bullish': 1, 'bearish': 0, '': np.nan})
    df['invested'] = df['invested'].ffill().fillna(0)

    return df

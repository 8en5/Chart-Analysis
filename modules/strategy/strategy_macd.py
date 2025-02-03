import matplotlib.pyplot as plt
import numpy as np
import pandas_ta as ta

from .strategy import Strategy
from modules.plot import *
from modules.indicators import *
from modules.functional_analysis import *


class MACD(Strategy):
    def __init__(self, symbol, df_raw):
        super().__init__(symbol, df_raw)

        self.strategy_name = 'MACD'

        # Parameter study
        self.params = {
            'm_fast': 12,
            'm_slow': 26,
            'm_signal': 90 # 9
        }

        self.params_study = {
            'm_fast': [10, 14, 18],
            'm_slow': [20, 30, 40],
            'm_signal': [7, 9, 12, 30, 90]  # m_signal accidentally set to 90 (copy from rsi) -> really good param
        }


    def set_manual_strategy(self):
        # Indicator
        self.df_indices['MACD'] = indicator_MACD(self.df_min, fast=self.params['m_fast'], slow=self.params['m_slow'], signal=self.params['m_signal'])
        col_MACD, coll_diff, col_signal = get_indicator_col_names(self.df_indices['MACD'], 'MACD')

        # Signals
        self.df_indices['MACD'], col_crossing = calculate_crossings(self.df_indices['MACD'], col_MACD, col_signal)

        conditions = [
            (self.df_indices['MACD'][col_crossing] == 'up'),    # Buy, if MACD crosses the signal line from bottom to top
            (self.df_indices['MACD'][col_crossing] == 'down')   # Sell, if MACD crosses the signal line from top to bottom
        ]

        values = ['buy', 'sell']
        self.df_indices['MACD']['signal'] = np.select(conditions, values, default='')
        self._summarize_signals()

        # Invested [in, out] from signals
        self.df_signals['invested'] = self.df_signals['MACD'].replace({'buy': 1, 'sell': 0, '': np.nan})
        self.df_signals['invested'] = self.df_signals['invested'].ffill().fillna(0)


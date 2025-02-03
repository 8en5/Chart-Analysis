import matplotlib.pyplot as plt
import numpy as np
import pandas_ta as ta


from .strategy import Strategy
from modules.plot import *
from modules.indicators import *


class BB(Strategy):
    def __init__(self, symbol, df_raw):
        super().__init__(symbol, df_raw)

        self.strategy_name = 'BB'

        # Parameter study
        self.params = {
            'bb_l': 6,
            'bb_std': 2.0
        }

        self.params_study = {
            'bb_l': [5, 6, 8, 10, 15, 20, 30],
            'bb_std': [1.5, 1.8, 2.0, 2.2, 2.5]
        }


    def set_manual_strategy(self):
        # Indicator
        self.df_indices['BB'] = indicator_BB(self.df_min, length=self.params['bb_l'], std=self.params['bb_std'])
        col_l, col_m, col_u = get_indicator_col_names(self.df_indices['BB'], 'BB')

        # Signals
        conditions = [
            (self.df_min['close'] <= self.df_indices['BB'][col_l]),  # Bullish, if course is smaller than the lower band
            (self.df_min['close'] >= self.df_indices['BB'][col_u])   # Bearish, if course is larger than the upper band
        ]
        values = ['bullish', 'bearish']
        self.df_indices['BB']['signal'] = np.select(conditions, values, default='')

        self._summarize_signals()


        # Invested [in, out] from signals
        self.df_signals['invested'] = self.df_signals['BB'].replace({'bullish': 1, 'bearish': 0, '': np.nan})
        self.df_signals['invested'] = self.df_signals['invested'].ffill().fillna(0)


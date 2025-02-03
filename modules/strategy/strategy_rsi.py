import matplotlib.pyplot as plt
import numpy as np
import pandas_ta as ta


from .strategy import Strategy
from modules.plot import *
from modules.indicators import *


class RSI(Strategy):
    def __init__(self, symbol, df_raw):
        super().__init__(symbol, df_raw)

        self.strategy_name = 'RSI'

        # Parameter study
        self.params = {
            'rsi_l': 14,
            'bl': 30,
            'bu': 70
        }

        self.params_study = {
            'rsi_l': [10, 14, 18],
            'bl': [20, 30, 40],
            'bu': [60, 70, 90]
        }


    def set_manual_strategy(self):
        # Indicator
        self.df_indices['RSI'] = indicator_RSI(self.df_min, self.params['rsi_l'], self.params['bl'], self.params['bu'])
        col_RSI, col_bl, col_bu = get_indicator_col_names(self.df_indices['RSI'], 'RSI')

        # Signals
        conditions = [
            (self.df_indices['RSI'][col_RSI] < self.params['bl']),  # Bullish, if course is smaller than 30 (lower border)
            (self.df_indices['RSI'][col_RSI] > self.params['bu'])   # Bearish, if course is bigger than 70 (upper border)
        ]
        values = ['bullish', 'bearish']
        self.df_indices['RSI']['signal'] = np.select(conditions, values, default='')

        self._summarize_signals()


        # Invested [in, out] from signals
        self.df_signals['invested'] = self.df_signals['RSI'].replace({'bullish': 1, 'bearish': 0, '': np.nan})
        self.df_signals['invested'] = self.df_signals['invested'].ffill().fillna(0)



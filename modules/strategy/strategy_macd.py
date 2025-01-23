import matplotlib.pyplot as plt
import numpy as np
import pandas_ta as ta


from .strategy import Strategy
from modules.plot import *
from modules.indicators import *
from modules.evaluation import *
from ..utils import pandas_print_all, pandas_print_width


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
        self.df_indices['MACD'] = ta.macd(self.df_min['close'], fast=self.params['m_fast'], slow=self.params['m_slow'], signal=self.params['m_signal'])
        col_MACD, coll_diff, col_signal = list(self.df_indices['MACD'].columns)

        # Evaluation
        self.df_indices['MACD'], col_crossing = calculate_crossings(self.df_indices['MACD'], col_MACD, col_signal)

        conditions = [
            (self.df_indices['MACD'][col_crossing] == 'up'),    # Buy, if MACD crosses the signal line from bottom to top
            (self.df_indices['MACD'][col_crossing] == 'down')   # Sell, if MACD crosses the signal line from top to bottom
        ]

        values = ['buy', 'sell']
        self.df_indices['MACD']['evaluation'] = np.select(conditions, values, default='')

        self.summarize_evaluation()


        # Buy and sell triggers from evaluation
        self.df_evaluation['status'] = self.df_evaluation['MACD'].replace({'buy':'in','sell':'out','': np.nan})
        self.df_evaluation['status'] = self.df_evaluation['status'].ffill().fillna('out')



    def plot(self, save=False):
        fig, ax = plt.subplots(2, 1, sharex=True, sharey=True) # share -> synch both plots during zoom
        # Plot 1 (Course)
        ax_background_colored_evaluation(ax[0], self.df_evaluation)     # Evaluation In, Out
        ax_course(ax[0], self.df_min)                                   # Course
        ax_graph_elements(ax[0], self.symbol)                           # Labels

        # Plot 2 (Indicator BB)
        ax_background_colored_evaluation(ax[1], self.df_indices['MACD'])  # Evaluation Index
        ax_MACD(ax[1], self.df_indices['MACD'])                           # MACD
        ax_graph_elements(ax[1], 'MACD')                             # Labels

        if save:
            self.save_plot(fig)

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

        self.param_study = {
            'rsi_l': [10, 14, 18],
            'bl': [20, 30, 40],
            'bu': [60, 70, 90]
        }


    def set_manual_strategy(self):
        # Indicator
        self.df_indices['RSI'] = get_RSI(self.df_min, self.params['rsi_l'], self.params['bl'], self.params['bu'])
        col_RSI, col_bl, col_bu = list(self.df_indices['RSI'].columns)

        # Evaluation
        conditions = [
            (self.df_indices['RSI'][col_RSI] < 30),  # Bullish, if course is smaller than 30 (lower border)
            (self.df_indices['RSI'][col_RSI] > 70)   # Bearish, if course is bigger than 70 (upper border)
        ]

        values = ['bullish', 'bearish']
        self.df_indices['RSI']['evaluation'] = np.select(conditions, values, default='')

        self.summarize_evaluation()


        # Buy and sell triggers from evaluation
        self.df_evaluation['status'] = self.df_evaluation['RSI'].replace({'bullish':'in','bearish':'out','': np.nan})
        self.df_evaluation['status'] = self.df_evaluation['status'].ffill().fillna('out')


    def plot(self, save=False):
        fig, ax = plt.subplots(2, 1)
        # Plot 1 (Course)
        ax_background_colored_evaluation(ax[0], self.df_evaluation)     # Evaluation In, Out
        ax_course(ax[0], self.df_min)                                   # Course
        ax_graph_elements(ax[0], self.symbol)                           # Labels

        # Plot 2 (Indicator BB)
        ax_background_colored_evaluation(ax[1], self.df_indices['RSI'])  # Evaluation Index
        ax_RSI(ax[1], self.df_indices['RSI'])                            # RSI
        ax_graph_elements(ax[1], 'RSI')                             # Labels

        if save:
            self.save_plot(fig)

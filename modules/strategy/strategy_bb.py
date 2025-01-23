import matplotlib.pyplot as plt
import numpy as np
import pandas_ta as ta


from .strategy import Strategy
from modules.plot import *


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
        self.df_indices['BB'] = ta.bbands(self.df_min['close'], length=self.params['bb_l'], std=self.params['bb_std'])
        col_l, col_m, col_u, col_b, col_p = list(self.df_indices['BB'].columns)
        # Evaluation
        conditions = [
            (self.df_min['close'] <= self.df_indices['BB'][col_l]),  # Bullish, if course is smaller than the lower band
            (self.df_min['close'] >= self.df_indices['BB'][col_u])   # Bearish, if course is larger than the upper band
        ]
        values = ['bullish', 'bearish']
        self.df_indices['BB']['evaluation'] = np.select(conditions, values, default='')

        self.summarize_evaluation()


        # Buy and sell triggers from evaluation
        self.df_evaluation['status'] = self.df_evaluation['BB'].replace({'bullish':'in','bearish':'out','': np.nan})
        self.df_evaluation['status'] = self.df_evaluation['status'].ffill().fillna('out')


    def plot(self, save=False):
        fig, ax = plt.subplots(2, 1, sharex=True, sharey=True) # share -> synch both plots during zoom
        # Plot 1 (Course)
        ax_background_colored_evaluation(ax[0], self.df_evaluation)     # Evaluation In, Out
        ax_course(ax[0], self.df_min)                                   # Course
        ax_graph_elements(ax[0], self.symbol)                           # Labels

        # Plot 2 (Indicator BB)
        ax_course(ax[1], self.df_min)                                   # Course
        ax_background_colored_evaluation(ax[1], self.df_indices['BB'])  # Evaluation Index
        ax_BB(ax[1], self.df_indices['BB'])                             # BB
        ax_graph_elements(ax[1], 'BB')                             # Labels

        if save:
            self.save_plot(fig)

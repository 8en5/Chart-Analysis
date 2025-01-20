import matplotlib.pyplot as plt
import numpy as np
import pandas_ta as ta

from modules.file_handler import *
from .strategy import Strategy
from modules.plot import *


class BB(Strategy):
    def __int__(self, symbol, df_raw):
        super().__init__(symbol, df_raw)


    def calculate_indices(self):
        self.df_indices['BB'] = ta.bbands(self.df_min['close'], length=6, std=2.0)


    def evaluate_strategy(self):
        # Indicators
        # BB
        df = self.df_indices['BB']
        col_l, col_m, col_u, col_b, col_p = list(df.columns)

        # Conditions for evaluation
        conditions = [
            (self.df_min['close'] <= df[col_l]),  # Bullish, if course is smaller than the lower band
            (self.df_min['close'] >= df[col_u])   # Bearish, if course is larger than the upper band
        ]
        values = ['bullish', 'bearish']
        df['evaluation'] = np.select(conditions, values, default='')


    def plot(self):
        fig, ax = plt.subplots(2, 1)
        # Plot 1 (Course)
        ax_course(ax[0], self.df_min)                                   # Course
        ax_graph_elements(ax[0], self.symbol)                           # Labels
                                            # Trigger

        # Plot 2 (Indicator BB)
        ax_course(ax[1], self.df_min)                                   # Course
        ax_background_colored_evaluation(ax[1], self.df_indices['BB'])  # Evaluation
        ax_BB(ax[1], self.df_indices['BB'])                             # BB
        ax_graph_elements(ax[1], 'BB')                             # Labels

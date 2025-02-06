import sys
sys.path.append(r'/') # to run py-file in separate cmd

import itertools
import matplotlib.pyplot as plt
import pandas as pd

from modules.strategy.manual_strategies import *
from modules.utils import *
from modules.file_handler import *
from modules.plot import *
from modules.strategy.eval_strategy import *

pd.set_option('future.no_silent_downcasting', True)


class VisualizeStrategy:
    def __init__(self, strategy_name, run_type=1):
        self.strategy_name = strategy_name      # strategy name (e.g. BB)

        self.run_type = run_type                # Control of the different logics

        # parameter study
        self.params = None                      # all params for the study

        self.show_plot = False                  # bool, show plot
        self.save_plot = False                  # bool, save plot
        self.plot_type = 1                      # 0 (only course), 1 (course + indicator)


    def routine_manager(self):
        if self.run_type == 0:                  # Test -> Plot one strategy without saving
            self.show_plot = True
            self.save_plot = False
            self.routine_plot_strategy('BTC')


        elif self.run_type == 1:                 # Test -> Save one param study and save plots (without show)
            self.routine_save_param_study('BTC')


        elif self.run_type > 9:
            folder_path = os.path.join(get_path('course_cc'), 'yaml')
            file_paths_symbols = list_file_paths_in_folder(folder_path, '.csv')
            # Loop over all symbols
            for index, file_path_symbol in enumerate(file_paths_symbols):
                symbol = get_filename_from_path(file_path_symbol)
                print(f'{index+1}/{len(file_paths_symbols)}: {symbol}')
                if self.run_type == 10:
                    self.show_plot = False
                    self.save_plot = True
                    self.routine_plot_strategy(symbol)
                elif self.run_type == 11:
                    self.routine_save_param_study(symbol)


    def routine_plot_strategy(self, symbol):
        self._load_symbol(symbol)
        self._main_routine()

    def routine_save_param_study(self, symbol):
        self.show_plot = False
        self.save_plot = True
        self._load_symbol(symbol)

        # Param study - Loop over all params im params_study
        params_study = get_all_combinations_from_params_study(name)
        for index, params in enumerate(params_study):
            self.params = params
            print(f'{index+1}/{len(params_study)}: {params}')
            self._main_routine()
            # print(df)


    def _main_routine(self):
        self._manual_strategy()
        if self.show_plot or self.save_plot:
            self._plot()
            if self.show_plot:
                plt.show()
        self._reset()


    def _reset(self):
        self.df_invested = pd.DataFrame()


    def _load_symbol(self, symbol):
        self.symbol = symbol  # symbol (e.g. BTC)
        df = load_pandas_from_symbol(symbol)
        self.df_raw = df            # raw data for the next cycle in param study: df = ['time', 'high', 'low', 'open', 'volumefrom', 'volumeto', 'close']
        self.df_min = df[['close']] # min input for functions: df = ['close']


    def _manual_strategy(self):
        func_set_manual_strategy = globals()[f'set_manual_strategy_{self.strategy_name}']
        df = func_set_manual_strategy(self.df_min)
        self.df_invested = df


    def _plot(self):
        """ Plot strategy
        Default (for every strategy):
          Plot 1: Course + Status (status = background color, if in or out)
        With Indicator (only if strategy == Indicator)
          Plot 1: Course + Status (status = background color, if in or out)
          Plot 2: Indicator + Evaluation (evaluation = signals ['buy', 'sell', 'bullish', 'bearish'] from indicators)
        """
        if self.plot_type == 0:
            # Default Plot
            fig, ax = plt.subplots(1, 1)
             # Plot 1 (Course)
            ax_background_colored_signals(ax, self.df_invested[['invested']])     # df['invested'] -> [in,out]
            ax_course(ax, self.df_invested)                                       # Course
            ax_graph_elements(ax, self.symbol)                                    # Labels
        elif self.plot_type == 1:
            # Default Plot
            fig, ax = plt.subplots(2, 1, sharex=True)                 # share -> synch both plots during zoom
            # Plot 1 (Course)
            ax_background_colored_signals(ax[0], self.df_invested[['invested']])  # df['invested'] -> [in,out]
            ax_course(ax[0], self.df_invested)                                    # Course
            ax_graph_elements(ax[0], self.symbol)                                 # Labels
            # Plot 2 (Indicator BB)
            ax_background_colored_signals(ax[1], self.df_invested[['signal']])    # df['signal'] -> [buy, sell, bullish, bearish]
            func_ax_indicator = globals()[f'ax_{name}']                           # e.g. ax_BB
            func_ax_indicator(ax[1], self.df_invested)                            # Indicator
            ax_graph_elements(ax[1], self.strategy_name)                          # Labels
        else:
            raise ValueError(f'Wrong plot type (0 or 1): {self.plot_type}')

        if self.save_plot:
            self._save_fig(fig)


    def _save_fig(self, fig):
        """ Save matplotlib fig
        param study: analyse/crypto_compare/{strategy}/parameter_study/{symbol}
        normal:      analyse/crypto_compare/{strategy}/symbols
        """
        # Folder and name
        base_folder_path = str(os.path.join(get_path('analyse_cc'), self.strategy_name))
        if self.params:
            folder_path = os.path.join(base_folder_path, f'parameter_study/{self.symbol}')
            file_name = f'{self.symbol}' # e.g. 'ETH_bb_l-5_bb_std-1.5' | '{symbol}_param1-value1_param2-value2
            for key, value in self.params.items():
                file_name += f'_{key}-{value}'
        else:
            folder_path = os.path.join(base_folder_path, 'symbols') # e.g. ETH
            file_name = self.symbol

        # Save
        save_matplotlib_figure(fig, folder_path, file_name)



if __name__ == "__main__":

    name = 'BB' # MACD, BB, RSI

    vs = VisualizeStrategy(name, 11)
    vs.routine_manager()


import itertools
import matplotlib.pyplot as plt

from modules.utils import *
from modules.file_handler import *
from modules.plot import *
from modules.strategy.eval_strategy import *

pd.set_option('future.no_silent_downcasting', True)

class Strategy:
    def __init__(self, symbol, df_raw):
        # df
        self.symbol = symbol                    # symbol (e.g. BTC)
        self.strategy_name = ''                 # CHILD, strategy (e.g. MACD)
        self.df_raw = df_raw                    # raw data for the next cycle in param study: df = ['time', 'high', 'low', 'open', 'volumefrom', 'volumeto', 'close']
        self.df_min = df_raw[['close']]         # min input for functions: df = ['close']
        self.df_indices = {}                    # CHILD, calculated indices: df_indices = {'BB': df, 'RSI': df, ...}
        self.df_signals = df_raw[['close']]     # CHILD, summary signals + [in,out] from indicators

        # parameter study
        self.study = False                      # bool param study
        self.params = {}                        # CHILD, all params for the study
        self.params_study = {}                  # CHILD, for every param a param variation

        self.save = False                       # bool, save plot


    def run(self):
        """ Main control routine to call all functions
        Distinction between parameter study and no parameter study (hard specified in the class as bool - self.study)
        """
        if self.study:
            # Param study
            keys = self.params_study.keys()
            values = self.params_study.values()
            combination = list(itertools.product(*values))
            combinations_list = [dict(zip(keys, combi)) for combi in combination] # combination_list = [{self.params1}, {self.params2}, ... ]
            i = 1
            # Go through all parameter variations
            for study in combinations_list:
                print(f'{i}/{len(combinations_list)}: {study}')
                self.params = study
                self.set_manual_strategy()
                self.plot()    # reset calculations from the current cycle
                self._reset_df()
                i += 1

        else:
            # 1x default parameter
            self.set_manual_strategy()
            #self.plot()
            evaluate_strategy(self.df_signals[['close', 'invested']])


    def set_manual_strategy(self):
        """ Define strategy - 100% in the Child class (because every strategy is unique)
        1. Calculate indices | self.df_indices['index1', 'index2', 'index3']
        2. Calculate buy and sell signals from every index | self.df_indices['evaluation']
        3. Summarize all evaluations from indices to one df | self.df_evaluation['Eval-BB', 'Eval-RSI', ...]
        4. Calculate status [in, out] from the evaluations | self.df_evaluation['status']
        """
        raise NotImplementedError

    def plot(self):
        """ Plot strategy
        Default (for every strategy):
          Plot 1: Course + Status (status = background color, if in or out)
          Plot 2: Indicator + Evaluation (evaluation = signals ['buy', 'sell', 'bullish', 'bearish'] from indicators)
        Unique:
          plot() function defined in Child
        """
        # Default Plot
        fig, ax = plt.subplots(2, 1, sharex=True)  # share -> synch both plots during zoom
         # Plot 1 (Course)
        ax_background_colored_signals(ax[0], self.df_signals)  # [in,out]
        ax_course(ax[0], self.df_min)                          # Course
        ax_graph_elements(ax[0], self.symbol)                  # Labels
         # Plot 2 (Indicator BB)
        ax_background_colored_signals(ax[1], self.df_indices[self.strategy_name])  # Signals index
        func_ax_indicator = globals()[f'ax_{self.strategy_name}']       # e.g. ax_BB
        func_ax_indicator(ax[1], self.df_indices[self.strategy_name])   # Indicator
        ax_graph_elements(ax[1], self.strategy_name)                    # Labels

        if self.save:
            self._save_plot(fig)


    def _reset_df(self):
        """ Reset all calculations from this cycle (in param study)
        """
        self.df_min = self.df_raw[['close']]
        self.df_indices = {}
        self.df_signals = self.df_raw[['close']]


    def _save_plot(self, fig):
        """ Save matplotlib fig
        param study: analyse/crypto_compare/{strategy}/parameter_study/{symbol}
        normal:      analyse/crypto_compare/{strategy}/symbols
        """
        # Folder and name
        base_folder_path = str(os.path.join(get_path('analyse_cc'), self.strategy_name))
        if self.study:
            folder_path = os.path.join(base_folder_path, f'parameter_study/{self.symbol}')
            name = f'{self.symbol}' # e.g. 'ETH_bb_l-5_bb_std-1.5' | '{symbol}_param1-value1_param2-value2
            for key, value in self.params.items():
                name += f'_{key}-{value}'
        else:
            folder_path = os.path.join(base_folder_path, 'symbols')
            name = self.symbol
        # Save
        save_matplotlib_figure(fig, folder_path, name)


    def _summarize_signals(self):
        """ Summarize all different evaluations in df_indices to one new df_evaluation
        Step 3 in set_manual_strategy(): Summarize all evaluations from indices to one df
        self.df_signals['BB', 'RSI', ...]
        """
        for index in self.df_indices:
            col = f'{index}'
            self.df_signals = pd.concat([self.df_signals, self.df_indices[index]['signal']], axis=1)
            self.df_signals = self.df_signals.rename(columns={'signal': col})


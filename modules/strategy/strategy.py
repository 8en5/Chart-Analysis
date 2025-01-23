import itertools

from modules.utils import *
from modules.file_handler import *

pd.set_option('future.no_silent_downcasting', True)

class Strategy:
    def __init__(self, symbol, df_raw):
        # df
        self.symbol = symbol                    # symbol (e.g. BTC)
        self.strategy_name = ''                 # CHILD, strategy (e.g. MACD)
        self.df_raw = df_raw                    # raw data for the next cycle in param study: df = ['time', 'high', 'low', 'open', 'volumefrom', 'volumeto', 'close']
        self.df_min = df_raw[['close']]         # min input for functions: df = ['close']
        self.df_indices = {}                    # CHILD, calculated indices: df_indices = {'BB': df, 'RSI': df, ...}
        self.df_evaluation = df_raw[['close']]  # CHILD, every evaluation colum from indices, to calculate in, out signals

        # parameter study
        self.study = False                      # bool param study
        self.params = {}                        # CHILD, all params for the study
        self.params_study = {}                  # CHILD, for every param a param variation

        self.save = False                       # bool, save plot


    def run(self):
        """ Main control routine to call all functions
        distinction between parameter study and no parameter study (hard specified in the class as bool - self.study)
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
                self.plot(self.save)    # reset calculations from the current cycle
                self.reset_df()
                i += 1

        else:
            # 1x default parameter
            self.set_manual_strategy()
            self.plot(self.save)


    def set_manual_strategy(self):
        """ Define strategy - 100% in the Child class (because every strategy is unique)
        1. Calculate indices | self.df_indices['index1', 'index2', 'index3']
        2. Calculate buy and sell signals from every index | self.df_indices['evaluation']
        3. Summarize all evaluations from indices to one df | self.df_evaluation['Eval-BB', 'Eval-RSI', ...]
        4. Calculate status [in, out] from the evaluations | self.df_evaluation['status']
        """
        raise NotImplementedError

    def plot(self, save=False):
        """ Define plot - 100% in the Child class (because every plot is unique)
        Plot 1: Course + Status (status = background color, if in or out)
        Plot 2: Indicator + Evaluation (evaluation = signals ['buy', 'sell', 'bullish', 'bearish'] from indicators)
        :param save: bool: True, if plot should be saved
        """
        raise NotImplementedError


    def reset_df(self):
        """ Reset all calculations from this cycle (in param study)
        """
        self.df_min = self.df_raw[['close']]
        self.df_indices = {}
        self.df_evaluation = self.df_raw[['close']]

    def save_plot(self, fig):
        """ Save matplotlib fig
        param study: analyse/crypto_compare/{strategy}/parameter_study/{symbol}
        normal:      analyse/crypto_compare/{strategy}/symbols
        """
        # Folder and name
        base_folder_path = str(os.path.join(get_path('analyse_cc'), self.strategy_name))
        if self.study:
            folder_path = os.path.join(base_folder_path, f'parameter_study/{self.symbol}')
            name = f'{self.symbol}' # 'ETH_bb_l-5_bb_std-1.5' | '{symbol}_param1-value1_param2-value2
            for key, value in self.params.items():
                name += f'_{key}-{value}'
        else:
            folder_path = os.path.join(base_folder_path, 'symbols')
            name = self.symbol
        # Save
        save_matplotlib_figure(fig, folder_path, name)


    def print(self):
        """ Print different dfs
        """
        pandas_print_width()
        print(self.df_raw)

        for key in self.df_indices:
            print(key)
            print(self.df_indices[key])
            print()

        print(self.df_evaluation)


    def summarize_evaluation(self):
        """ Summarize all different evaluations in df_indices to one new df_evaluation
        Step 3 in set_manual_strategy(): Summarize all evaluations from indices to one df
        self.df_evaluation['Eval-BB', 'Eval-RSI', ...]
        """
        for index in self.df_indices:
            col = f'{index}'
            self.df_evaluation = pd.concat([self.df_evaluation, self.df_indices[index]['evaluation']], axis=1)
            self.df_evaluation = self.df_evaluation.rename(columns={'evaluation': col})


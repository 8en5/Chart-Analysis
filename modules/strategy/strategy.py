import itertools

from modules.utils import *
from modules.file_handler import *

pd.set_option('future.no_silent_downcasting', True)

class Strategy:
    def __init__(self, symbol, df_raw):
        # df
        self.symbol = symbol
        self.strategy_name = ''
        self.df_raw = df_raw
        self.df_min = df_raw[['close']]
        self.df_indices = {}
        self.df_evaluation = df_raw[['close']]

        # parameter study
        self.study = False
        self.params = {}
        self.param_study = {}

        self.save = True


    def run(self):
        if self.study:
            keys = self.param_study.keys()
            values = self.param_study.values()
            combination = list(itertools.product(*values))
            combinations_list = [dict(zip(keys, combi)) for combi in combination]
            i = 1
            for study in combinations_list:
                print(f'{i}/{len(combinations_list)}: {study}')
                self.params = study
                self.set_manual_strategy()
                self.plot(self.save)
                self.reset_df()
                i += 1

        else:
            self.set_manual_strategy()
            self.plot(self.save)


    def set_manual_strategy(self):
        raise NotImplementedError

    def plot(self, save=False):
        raise NotImplementedError


    def reset_df(self):
        self.df_min = self.df_raw[['close']]
        self.df_indices = {}
        self.df_evaluation = self.df_raw[['close']]

    def save_plot(self, fig):
        base_folder_path = str(os.path.join(get_path('analyse_cc'), self.strategy_name))
        if self.study:
            folder_path = os.path.join(base_folder_path, f'parameter_study/{self.symbol}')
            name = f'{self.symbol}'
            for key, value in self.params.items():
                name += f'_{key}-{value}'
            save_matplotlib_figure(fig, folder_path, name)
        else:
            folder_path = os.path.join(base_folder_path, 'symbols')
            name = self.symbol
            save_matplotlib_figure(fig, folder_path, name)


    def print(self):
        pandas_print_width()
        print(self.df_raw)

        for key in self.df_indices:
            print(key)
            print(self.df_indices[key])
            print()

        print(self.df_evaluation)


    def summarize_evaluation(self):
        for index in self.df_indices:
            col = f'{index}'
            self.df_evaluation = pd.concat([self.df_evaluation, self.df_indices[index]['evaluation']], axis=1)
            self.df_evaluation = self.df_evaluation.rename(columns={'evaluation': col})


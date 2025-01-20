

from modules.utils import *

class Strategy:
    def __init__(self, symbol, df_raw):
        self.symbol = symbol
        self.df_raw = df_raw
        self.df_min = df_raw[['close']]
        self.df_indices = {}


    def run(self):
        self.calculate_indices()
        self.evaluate_strategy()
        self.plot()

    def calculate_indices(self):
        pass

    def evaluate_strategy(self):
        pass

    def plot(self):
        pass


    def print(self):
        pandas_print_width()
        print(self.df_raw)

        for key in self.df_indices:
            print(key)
            print(self.df_indices[key])
            print()
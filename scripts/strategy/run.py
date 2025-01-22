import matplotlib.pyplot as plt
import sys

sys.path.append(r'C:\Users\bense\PycharmProjects\Chart-Analysis') # to run py-file in separate cmd
from modules.file_handler import *

from modules.strategy.strategy_bb import BB
from modules.strategy.strategy_rsi import RSI



def run(func):
    symbol = 'BTC'
    df = load_pandas_from_symbol(symbol)

    strategy = func(symbol, df)
    strategy.run()
    #strategy.print()

    plt.show()


def study_symbols(func):
    folder_path = os.path.join(get_path('course_cc'), 'yaml')
    file_paths = list_file_paths_in_folder(folder_path)
    i = 1

    file_paths_symbols = []
    for file_path in file_paths:
        if file_path.endswith('.csv'):
            file_paths_symbols.append(file_path)

    for file_path in file_paths_symbols:
        symbol = get_filename_from_path(file_path)
        df = load_pandas_from_file_path(file_path)
        print(f'{i}/{len(file_paths_symbols)}: {symbol}')
        strategy = func(symbol, df)
        strategy.run()
        i += 1


if __name__ == "__main__":

    #run(RSI)

    study_symbols(RSI)
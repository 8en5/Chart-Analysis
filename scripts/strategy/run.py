import matplotlib.pyplot as plt

from modules.file_handler import *

from modules.strategy.strategy_bb import BB



if __name__ == "__main__":
    symbol = 'BTC'
    df = load_pandas_from_symbol(symbol)

    strategy = BB(symbol, df)
    strategy.run()

    plt.show()
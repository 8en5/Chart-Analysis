
from modules.strategy.evaluate_signals import *

def test_compute_return():
    start_price = 50
    future_price  = list(range(5, 205, 5))
    print(future_price)

    pd.set_option('display.float_format', '{:.2f}'.format)
    df = pd.DataFrame({'close_today': [start_price] * len(future_price)})
    df['close_future'] = future_price
    df['percentage'] = df['close_future'].apply(lambda x: compute_return(start_price, x, mode='percentage'))
    df['fracture'] = df['close_future'].apply(lambda x: compute_return(start_price, x, mode='fracture'))
    df['factor'] = df['close_future'].apply(lambda x: compute_return(start_price, x, mode='factor'))
    df['log'] = df['close_future'].apply(lambda x: compute_return(start_price, x, mode='log'))
    print(df)


if __name__ == '__main__':
    test_compute_return()
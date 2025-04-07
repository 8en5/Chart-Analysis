


def evaluate_signals(df):
    pass




def min_max_df(df):
    return df.min, df.max


def single_evaluation_states(df):
    periods = [-30, -14, -7, 7, 14, 30, 60, 120, 180]


def evaluate_single_signals(df):
    for index, signal in enumerate(df['signal']):
        if signal in ['buy', 'sell', 'bullish', 'bearish']:
            print(signal)
            exit()
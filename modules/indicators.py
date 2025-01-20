import pandas as pd
import pandas_ta as ta



def get_period(freq='D'):
    if freq == 'D':
        periods = 1
    elif freq == '3D':
        periods = 3
    elif freq == 'W':
        periods = 7
    elif freq == 'ME':
        periods = 30
    elif freq == 'QE':
        periods = 91
    elif freq == 'YE':
        periods = 365
    else:
        raise ValueError(f'Warning: Wrong frequenz: {freq}')
    return periods


def percentage_change(df, freq='D'):
    # ['percentage_D']
    allowed_freq = ['D', '3D', 'W', 'ME', 'QE', 'YE']
    if freq not in allowed_freq:
        raise ValueError(f'Frequent "{freq}" not in {allowed_freq}')
    periods = get_period(freq)
    # percentage change
    col_perc = f'percentage_{freq}'
    df[col_perc] = df['close'].pct_change(periods=periods) * 100
    return df[[col_perc]]


def RSI(df, length=14, lower_border=30, upper_border=70):
    # ['RSI_14', 'border_lower_30', 'border_upper_70']
    df_RSI = pd.DataFrame(ta.rsi(df['close'], length=length))
    df_RSI[['border_lower_30', 'border_upper_70']] = [lower_border, upper_border]
    return df_RSI


def SMA(df, *lengths):
    # ['SMA_200']
    df_SMA = pd.DataFrame()
    if not lengths: # default value, if no parameter is given
        lengths = [200]
    for length in lengths:
        df_indicator = pd.DataFrame(ta.sma(df['close'], length=length))
        if df_SMA.empty:
            df_SMA = df_indicator
        else:
            df_SMA = pd.concat([df_SMA, df_indicator], axis=1)
    return df_SMA
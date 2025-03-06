import re
import pandas as pd
import pandas_ta as ta


COL_NAMES = {
    'BB': [r'BBL.*', r'BBM.*', r'BBU.*'], # ['BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'BBB_5_2.0', 'BBP_5_2.0'] - [Low, SMA, Up, Bandwith, Percentage]
    'CMA': ['CMA'], # ['CMA']
    'EMA': ['EMA.*'], # ['EMA_200']
    'MACD': [r'MACD_.*', r'MACDh.*', r'MACDs.*'], # ['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'] - [MACD, Histogram (Diff), Signal]
    'RSI': [r'RSI.*', '.*lower.*', '.*upper.*'], # ['RSI_14', 'border_lower_30', 'border_upper_70']
    'SMA': [r'SMA.*'], # multiple return allowed ['SMA_200', 'SMA_50']

    'perc': [r'perc.*'],
}

def func_indicator(indicator_name:str, *args, **kwargs):
    """
    :param indicator_name: name for the indicator defined in this file
    :param args: *args for the func
    :return: _indicator_{indicator_name}
    """
    func_name = f'_indicator_{indicator_name}'
    # Check if function is defined
    func = globals().get(func_name)
    if not callable(func):
        raise ValueError(f'The function "{func_name}" does not exist - define it in indicators.py')
    # Return called function
    try:
        return func(*args, **kwargs)
    except TypeError:
        """ TypeError if df has too little data
        Indicators need a certain amount of data before they generate signals. Before that they are only None
        The indicator in the library pandas_pa runs immediately Error if there is too little data:
            TypeError: unsupported operand type(s) for -: 'float' and 'NoneType'
        """
        print(f'There are too few values in the df')

def get_indicator_col_names(df, indicator:str):
    # Check
    if indicator not in COL_NAMES:
        raise ValueError(f'{indicator} not in {COL_NAMES.keys()}')

    # Calculate col names
    regex_list = COL_NAMES[indicator]
    matching_columns = []
    for regex in regex_list:
        matches = [element for element in df.columns if re.fullmatch(regex, element)]
        matching_columns.extend(matches)
        if not matches:
            raise ValueError(f'Column {regex} not in df: {df.columns}')

    # Prepare return
    if len(matching_columns) == 1:
        # c1 = func()
        return matching_columns[0]
    else:
        # c1, c2, c3 = func()
        return matching_columns


def get_period(period='D'):
    """
    :param period: [D, 3D, W, ME, QE, YE]
    :return:
    """
    match period:
        case 'D': freq = 1      # Day
        case '3D': freq = 3     # 3 Days
        case 'W': freq = 7      # Week
        case 'ME': freq = 30    # Month
        case 'QE': freq = 91    # Quarter
        case 'YE': freq = 365   # Year
        case _: # else
            raise ValueError(f'Warning: Wrong frequent: {period}')
    return freq


# TODO: df.copy entfernen -> direkt auf einem df arbeiten

#------------- Own calculated Indicators -------------#

def perc_change(df, freq='D'):
    """ Percentage Change df['close']
    :param freq: over how many samples
    :return: df['perc_D']
    """
    allowed_freq = ['D', '3D', 'W', 'ME', 'QE', 'YE']
    if freq not in allowed_freq:
        raise ValueError(f'Frequent "{freq}" not in {allowed_freq}')
    periods = get_period(freq)
    # percentage change
    col_perc = f'perc_{freq}'
    df[col_perc] = df['close'].pct_change(periods=periods) * 100
    return df


def _indicator_CMA(df):
    """ Cumulative Moving Average (CMA)
    :return: df['CMA']
    """
    df['CMA'] = df['close'].expanding().mean()
    return df


#------------- Indicators from pandas_ta -------------#

def _indicator_BB(df, length=6, std=2.0):
    """ Bollinger Bands (BB)
    :param length: SMA samples
    :param std: factor, by which the standard deviation for the bandwidth is multiplied
    :return: df['BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'BBB_5_2.0', 'BBP_5_2.0'] - [Low, SMA, Up, Bandwith, Percentage] - col_l, col_m, col_u

    3 lines: middle (SMA), upper and lower band
    Bearish: close > upper band -> if course is larger than the upper band
    Bullish: close < lower band -> if course is smaller than the lower band
    """
    df_indicator = ta.bbands(df['close'], length=length, std=std)
    df = pd.concat([df, df_indicator], axis=1)
    return df


def _indicator_EMA(df, length=2):
    """ Exponential Moving Average (EMA)
    :param length: samples
    :return: df['EMA_200']
    """
    df[f'EMA_{length}'] = ta.ema(df['close'], length=length)
    return df


def _indicator_MACD(df, fast=12, slow=26, signal=9):
    """ Moving Average Convergence Divergence (MACD)
    :param fast: fast moving average (typically a short-term EMA)
    :param slow: slow moving average (typically a long-term EMA)
    :param signal: EMA of the MACD line over n samples
    :return: df['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'] - [MACD, Histogram (Diff), Signal] - col_MACD, coll_diff, col_signal

    Spot changes in the strength, direction, momentum, and duration of a trend in a stock
    buy: when the MACD crosses the signal line from bottom to top
    sell: when the MACD crosses the signal line from top to bottom
    """
    df_indicator = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    df = pd.concat([df, df_indicator], axis=1)
    return df


def _indicator_RSI(df, length=14, lower_border=30, upper_border=70):
    """ Relative Strength Index (RSI)
    :param length: samples
    :return: df['RSI_14', 'border_lower_30', 'border_upper_70'] - col_RSI, col_bl, col_bu

    upper and lower border
    sell: RSI >= upper border -> too high -> sell | crossing from above under 70
    buy: RSI <= lower border -> too low -> buy | crossing from below over 30
    """
    df[f'RSI_{length}'] = ta.rsi(df['close'], length=length)
    df[['border_lower_30', 'border_upper_70']] = [lower_border, upper_border]
    return df


def _indicator_SMA(df, length=200):
    """ Simple Moving Average (SMA)
    :param length: samples
    :return: df['SMA_200']
    """
    df[f'SMA_{length}'] = ta.sma(df['close'], length=length)
    return df

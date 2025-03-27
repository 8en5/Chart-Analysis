
from modules.indicators import *
from modules.functional_analysis import *
from modules.params import get_params_from_yaml


pd.set_option('future.no_silent_downcasting', True) # if values are converted down (value to nan - when calculating df[invested] based on df[signal])


def func_get_invested_from_indicator(indicator_name, df, params=None):
    """ Call function set_manual_strategy_{indicator_name}()
    :param indicator_name: name for the strategy defined in this file
    :param df: df[close]
    :param params: params for the indicator [None, dict, list]
    :return: _get_invested_from_{indicator_name} -> df[<indicators>, signal, invested]
    """
    func_name = f'_get_invested_from_{indicator_name}'
    # Check
    func = globals().get(func_name)
    if not callable(func):
        raise ValueError(f'The function "{func_name}" does not exist - define it in manual_strategies.py')
    # Return called function
    return func(df, params)


def _calc_invested_from_signal(df):
    """ Calculate status 'invested' from the signals of the indicators
    :param df: df[signal]
    :return: df[invested, close_perc, group_invested]
    """

    """ Input                                                                                             Output
                  close  BBL_5_1.5  BBM_5_1.5  BBU_5_1.5   BBB_5_1.5  BBP_5_1.5   signal                invested
    date                                                                                
    2017-10-01  0.02519        NaN        NaN        NaN         NaN        NaN                             None    <- (leading None until indicator has only no None values)
    2017-10-02  0.02588        NaN        NaN        NaN         NaN        NaN                             None
    2017-10-03  0.02084        NaN        NaN        NaN         NaN        NaN                             None
    2017-10-04  0.02189        NaN        NaN        NaN         NaN        NaN                             None
    2017-10-05  0.02152   0.019978   0.023064   0.026150         NaN        NaN                             None
    2017-10-06  0.01849   0.018138   0.021724   0.025310   33.017230        NaN                             None
    2017-10-07  0.02080   0.018933   0.020708   0.022483   17.143734   0.525915                                0    <- this is the first row where the signal could deliver values (fill column with 0 starting from here until first signal)
    2017-10-08  0.02052   0.018869   0.020644   0.022419   17.193739   0.465065                                0
    2017-10-09  0.02207   0.018846   0.020680   0.022514   17.736032   0.878973  bullish                       0    <- first signal (fill column with 0 until this row)
    2017-10-10  0.02148   0.018846   0.020672   0.022498   17.664475   0.721273                                1    <- (buy and sell signals one day later, because percentage change you see on the next day)
    2017-10-11  0.02253   0.020351   0.021480   0.022609   10.515934   0.964844                                1
    2017-10-12  0.02635   0.019595   0.022590   0.025585   26.512972   1.127788  bearish                       1
    2017-10-13  0.03354   0.018431   0.025194   0.031957   53.687847   1.117029                                0
    2017-10-14  0.03221   0.019857   0.027222   0.034587   54.111225   0.838625  bullish                       0
    2017-10-15  0.03003   0.022901   0.028932   0.034963   41.692945   0.591025                                1
    """

    df['invested'] = None
    if df['signal'].isin(['bullish', 'bearish']).any():
        df['invested'] = df['signal'].replace({'bullish': 1, 'bearish': 0, '': None})
    elif df['signal'].isin(['buy', 'sell']).any():
        df['invested'] = df['signal'].replace({'buy': 1, 'sell': 0, '': None})

    # shift everything 1 day later (because percentage changes only apply to the next day)
    df['invested'] = df['invested'].shift(1)
    # fill the None values between the buy and sell signals
    df['invested'] = df['invested'].ffill() #.fillna(0)
    #df['invested'] = df['invested'].replace({np.nan: None}) # to be sure there is no nan (sometimes in first line because of shift)

    # Fill area with non-None values where there could have been signals
    """ 
    Signals only deliver values after a certain number of times.
    Fill the area with non-None values from when signals could in principle be present up to the first signal
    
    e.g. Leading None for MACD
    leading_nans = df.apply(lambda col: col.isna().cumprod().sum())
    print(leading_nans)
        close                                   0
        MACD_10_20_7                           19
        MACDh_10_20_7                          25
        MACDs_10_20_7                          25
        Crossing_MACD_10_20_7-MACDs_10_20_7     0
        signal                                  0
        invested                               40
    
    -> first signal could be there after 25 days, but is only there after 40 days
    => fill the days from 25 - 40 with 0
    As a result: if df[invested] is None, then mathematically there can't be a signal (important for benchmark comparison to buy and hold)
    """
    df_leading_nans = df.loc[:,df.columns!='invested'].apply(lambda col: col.isna().cumprod().sum()) # lists all none values of all columns (except invested)
    max_leading_nans = df_leading_nans.max() # largest number of leading None values (from there on signals could deliver values)
    if (df['signal'] != '').any():
        first_value = df['signal'][df['signal'] != ''].index[0] # index when signal delivers the first value
    else:
        first_value = df.index[-1]
    df.loc[df.index[max_leading_nans]:first_value, 'invested'] = 0

    # Extra calculations, because they are needed everywhere (but doesn't really fit here)
    # Calculate daily perc change from course - df['close_perc']
    df['close_perc'] = df['close'].pct_change(periods=1)  # * 100

    # Group invested
    df = _df_group_invested(df)

    #print(df)
    return df


def _df_group_invested(df):
    """ [df] Group invested periods
    :param df: df[invested]
    :return: df[group_invested]

    Output:
        print(df[['close', 'invested', 'group_invested']])
                         close invested  group_invested
        date
        2010-09-26   0.062        0        NaN
        2010-09-27   0.062        0        NaN
        2010-09-28   0.062        1        1.0
        2010-09-29   0.062        1        1.0
        2010-09-30   0.062        1        1.0
        2010-10-01   0.062        1        1.0
        2010-10-02   0.061        1        1.0
        2010-10-03   0.061        1        1.0
        2010-10-04   0.061        1        1.0
        2010-10-05   0.061        0        NaN
        2010-10-06   0.063        0        NaN
        2010-10-07   0.067        1        2.0
        2010-10-08   0.087        1        2.0
        2010-10-09   0.094        1        2.0
        2010-10-10   0.097        1        2.0
    """
    # Group every connected invested block
    df['group_invested'] = (df['invested'].fillna(0).diff(1) == 1).cumsum()
    # Set everything else to None
    df.loc[df['invested'].isna() | (df['invested'] == 0), 'group_invested'] = None
    return df


#------------------------ Indicators ------------------------#

def _get_invested_from_BB(df, params=None):
    if params is None:
        params = get_params_from_yaml('BB', 'default')

    # Indicator
    df = func_indicator('BB', df, params)
    col_l, col_m, col_u = get_indicator_col_names(df, 'BB')

    # Signals
    conditions = [
        (df['close'] <= df[col_l]),  # Bullish, if course is smaller than the lower band
        (df['close'] >= df[col_u])   # Bearish, if course is larger than the upper band
    ]
    values = ['bullish', 'bearish']
    df['signal'] = np.select(conditions, values, default='')

    # Invested [in, out] from signals
    df = _calc_invested_from_signal(df)
    #print(df)
    return df


def _get_invested_from_MACD(df, params=None):
    if params is None:
        params = get_params_from_yaml('MACD', 'default')

    # Indicator
    df = func_indicator('MACD', df, params)
    col_MACD, coll_diff, col_signal = get_indicator_col_names(df, 'MACD')

    # Signals
    df, col_crossing = calculate_crossings(df, col_MACD, col_signal)

    conditions = [
        (df[col_crossing] == 'up'),    # Buy, if MACD crosses the signal line from bottom to top
        (df[col_crossing] == 'down')   # Sell, if MACD crosses the signal line from top to bottom
    ]
    values = ['buy', 'sell']
    df['signal'] = np.select(conditions, values, default='')

    # Invested [in, out] from signals
    df = _calc_invested_from_signal(df)
    return df


def _get_invested_from_RSI(df, params=None):
    if params is None:
        params = get_params_from_yaml('RSI', 'default')

    # Indicator
    df = func_indicator('RSI', df, params)
    col_RSI, col_bl, col_bu = get_indicator_col_names(df, 'RSI')

    # Signals
    conditions = [
        (df[col_RSI] < params['bl']), # Bullish, if course is smaller than 30 (lower border)
        (df[col_RSI] > params['bu'])  # Bearish, if course is bigger than 70 (upper border)
    ]
    values = ['bullish', 'bearish']
    df['signal'] = np.select(conditions, values, default='')

    # Invested [in, out] from signals
    df =_calc_invested_from_signal(df)
    return df

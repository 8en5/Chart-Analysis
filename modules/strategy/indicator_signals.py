"""
df[<indicators>, signal, invested, close_perc, group_invested]

            close  MACD_5_10_14  MACDh_5_10_14  MACDs_5_10_14 Crossing_MACD_5_10_14-MACDs_5_10_14 signal invested  close_perc  group_invested
date
2017-10-01  0.025           NaN            NaN            NaN                                       None     None         NaN             NaN
2017-10-02  0.026           NaN            NaN            NaN                                       None     None    0.040000             NaN
2017-10-03  0.021           NaN            NaN            NaN                                       None     None   -0.192308             NaN
2017-10-04  0.022           NaN            NaN            NaN                                       None     None    0.047619             NaN
2017-10-05  0.022           NaN            NaN            NaN                                       None     None    0.000000             NaN
2017-10-06  0.018           NaN            NaN            NaN                                       None     None   -0.181818             NaN
2017-10-07  0.021           NaN            NaN            NaN                                       None     None    0.166667             NaN
2017-10-08  0.021           NaN            NaN            NaN                                       None     None    0.000000             NaN
2017-10-09  0.022           NaN            NaN            NaN                                       None     None    0.047619             NaN
2017-10-10  0.021     -0.000586            NaN            NaN                                       None     None   -0.045455             NaN
2017-10-11  0.023     -0.000224            NaN            NaN                                       None     None    0.095238             NaN
2017-10-12  0.026      0.000442            NaN            NaN                                       None     None    0.130435             NaN
2017-10-13  0.034      0.001990            NaN            NaN                                       None     None    0.307692             NaN
2017-10-14  0.032      0.002411            NaN            NaN                                       None     None   -0.058824             NaN
2017-10-15  0.030      0.002191            NaN            NaN                                       None     None   -0.062500             NaN
2017-10-16  0.029      0.001787            NaN            NaN                                       None     None   -0.033333             NaN
2017-10-17  0.027      0.001156            NaN            NaN                                       None     None   -0.068966             NaN
2017-10-18  0.027      0.000741            NaN            NaN                                       None     None    0.000000             NaN
2017-10-19  0.027      0.000470            NaN            NaN                                       None     None    0.000000             NaN
2017-10-20  0.030      0.000748            NaN            NaN                                       None     None    0.111111             NaN
2017-10-21  0.028      0.000551            NaN            NaN                                       None     None   -0.066667             NaN
2017-10-22  0.028      0.000411            NaN            NaN                                       None     None    0.000000             NaN
2017-10-23  0.026      0.000006  -8.577989e-04       0.000864                                                   0   -0.071429             NaN
2017-10-24  0.027     -0.000063  -8.037266e-04       0.000740                                                   0    0.038462             NaN
2017-10-25  0.027     -0.000098  -7.261225e-04       0.000629                                                   0    0.000000             NaN
2017-10-26  0.027     -0.000110  -6.403060e-04       0.000530                                                   0    0.000000             NaN
2017-10-27  0.026     -0.000262  -6.864548e-04       0.000424                                                   0   -0.037037             NaN
2017-10-28  0.026     -0.000329  -6.529061e-04       0.000324                                                   0    0.000000             NaN
2017-10-29  0.028     -0.000042  -3.175753e-04       0.000275                                                   0    0.076923             NaN
2017-10-30  0.029      0.000268  -6.267243e-06       0.000274                                                   0    0.035714             NaN
2017-10-31  0.031      0.000724   3.898298e-04       0.000334                                  up    buy        0    0.068966             NaN
2017-11-01  0.023     -0.000283  -5.350836e-04       0.000252                                down   sell        1   -0.258065             1.0
2017-11-02  0.021     -0.001119  -1.187635e-03       0.000069                                                   0   -0.086957             NaN
2017-11-03  0.023     -0.001203  -1.102761e-03      -0.000101                                                   0    0.095238             NaN
2017-11-04  0.022     -0.001328  -1.063914e-03      -0.000264                                                   0   -0.043478             NaN
2017-11-05  0.021     -0.001467  -1.042625e-03      -0.000425                                                   0   -0.045455             NaN
2017-11-06  0.022     -0.001303  -7.609913e-04      -0.000542                                                   0    0.047619             NaN
2017-11-07  0.022     -0.001134  -5.133117e-04      -0.000621                                                   0    0.000000             NaN
2017-11-08  0.025     -0.000519   8.838403e-05      -0.000607                                  up    buy        0    0.136364             NaN
2017-11-09  0.032      0.000909   1.313901e-03      -0.000405                                                   1    0.280000             2.0
2017-11-10  0.026      0.000724   9.779819e-04      -0.000254                                                   1   -0.187500             2.0
2017-11-11  0.027      0.000730   8.532221e-04      -0.000123                                                   1    0.038462             2.0
2017-11-12  0.024      0.000235   3.102498e-04      -0.000075                                                   1   -0.111111             2.0
2017-11-13  0.026      0.000253   2.850629e-04      -0.000032                                                   1    0.083333             2.0
2017-11-14  0.026      0.000248   2.425669e-04       0.000006                                                   1    0.000000             2.0
2017-11-15  0.027      0.000382   3.260490e-04       0.000056                                                   1    0.038462             2.0
2017-11-16  0.027      0.000432   3.256921e-04       0.000106                                                   1    0.000000             2.0
2017-11-17  0.026      0.000281   1.517976e-04       0.000129                                                   1   -0.037037             2.0
"""

import pandas as pd
import numpy as np

from modules.indicators import func_indicator, get_indicator_col_names
from modules.functional_analysis import calculate_crossings


pd.set_option('future.no_silent_downcasting', True) # if values are converted down (value to nan - when calculating df[invested] based on df[signal])



#------------------------ Signals from Indicators ------------------------#

def func_df_signals_from_indicator(indicator_name, df, params=None):
    """ [df[<indicators>, signal]] Call function set_manual_strategy_{indicator_name}()
    :param indicator_name: name of the indicator defined in this file
    :param df: df[close]
    :param params: params for the indicator [None, dict, list]
    :return: _get_invested_from_{indicator_name} -> df[<indicators>, signal]

    Output (e.g. BB)
                  close  BBL_5_1.5  BBM_5_1.5  BBU_5_1.5   BBB_5_1.5  BBP_5_1.5      signal
    date
    2017-10-01  0.02519        NaN        NaN        NaN         NaN        NaN        None    <- leading None start
    2017-10-02  0.02588        NaN        NaN        NaN         NaN        NaN        None
    2017-10-03  0.02084        NaN        NaN        NaN         NaN        NaN        None
    2017-10-04  0.02189        NaN        NaN        NaN         NaN        NaN        None
    2017-10-05  0.02152   0.019978   0.023064   0.026150         NaN        NaN        None
    2017-10-06  0.01849   0.018138   0.021724   0.025310   33.017230        NaN        None    <- leading None end
    2017-10-07  0.02080   0.018933   0.020708   0.022483   17.143734   0.525915                <- this is the first row where df[signal] could deliver values
    2017-10-08  0.02052   0.018869   0.020644   0.022419   17.193739   0.465065
    2017-10-09  0.02207   0.018846   0.020680   0.022514   17.736032   0.878973     bullish    <- first signal (fill column with 0 until this row)
    2017-10-10  0.02148   0.018846   0.020672   0.022498   17.664475   0.721273
    2017-10-11  0.02253   0.020351   0.021480   0.022609   10.515934   0.964844
    2017-10-12  0.02635   0.019595   0.022590   0.025585   26.512972   1.127788     bearish
    2017-10-13  0.03354   0.018431   0.025194   0.031957   53.687847   1.117029
    2017-10-14  0.03221   0.019857   0.027222   0.034587   54.111225   0.838625     bullish
    2017-10-15  0.03003   0.022901   0.028932   0.034963   41.692945   0.591025
    """

    func_name = f'_get_signals_from_{indicator_name}'
    # Check
    func = globals().get(func_name)
    if not callable(func):
        raise ValueError(f'The function "{func_name}" does not exist - define it in manual_strategies.py')
    # Return called function
    return func(df, params)


def _get_signals_from_BB(df, params=None):
    """[df[<indicators>]]"""
    # Indicator
    df = func_indicator('BB', df, params)
    col_l, col_m, col_u = get_indicator_col_names(df, 'BB')

    # Signals
    conditions = [
        (df['close'] <= df[col_l]),  # Bullish, if course is smaller than the lower band
        (df['close'] >= df[col_u])   # Bearish, if course is larger than the upper band
    ]
    values = ['buy', 'sell']
    df['signal'] = np.select(conditions, values, default='')

    # Fill leading time with None
    df = _lead_time_signals(df)
    return df


def _get_signals_from_MACD(df, params=None):
    """[df[<indicators>]]"""
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

    # Fill leading time with None
    df = _lead_time_signals(df)
    return df


def _get_signals_from_RSI(df, params=None):
    """[df[<indicators>]]"""
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

    # Fill leading time with None
    df = _lead_time_signals(df)
    return df


def _lead_time_signals(df):
    """ [df[signal]] Fill leading time for the signals with None values
    Signals deliver values after a certain period of time.
    Fill all values of df[signals] with None where no signals can be delivered

    e.g. Leading None for MACD
    leading_nans = df.apply(lambda col: col.isna().cumprod().sum())
    print(leading_nans)
        close                                   0
        MACD_10_20_7                           19
        MACDh_10_20_7                          25
        MACDs_10_20_7                          25  <- after this leading time signals can be generated
        Crossing_MACD_10_20_7-MACDs_10_20_7     0
        signal                                  0

    -> the first possible signal could be generated after 25 days (the first signal was after 40 days)
    => fill the leading time of df[signals] with None values
    (this is important for benchmark comparison, because the comparison only makes sense if signals can actually be present)
    """
    df_leading_nans = df.apply(lambda col: col.isna().cumprod().sum())  # lists all none values of all columns (except invested)
    max_leading_nans = df_leading_nans.max()  # largest number of leading None values (from there on signals could deliver values)
    df.loc[df.index[0:max_leading_nans], 'signal'] = None # set leading time of df[signals] to None
    return df


#------------------------ Invested from Indicators ------------------------#

def df_invested_from_signal(df):
    """ [df[signal, invested]] Calculate status 'invested' from the signals
    :param df: df[signal] - [buy/bullish , sell/bearish]
    :return: df[invested]

        Input                      Output
                    close signal invested
        date                             
        2017-10-01  0.025   None        0
        2017-10-02  0.026   None        0
        2017-10-03  0.021   None        0
        2017-10-04  0.022   None        0
        2017-10-05  0.022   None        0
        2017-10-06  0.018               0
        2017-10-07  0.021               0
        2017-10-08  0.021    buy        0
        2017-10-09  0.022               1   <- shift 1 (percentage change apply the next day)
        2017-10-10  0.021               1
        2017-10-11  0.023               1
        2017-10-12  0.026               1
        2017-10-13  0.034   sell        1
        2017-10-14  0.032               0
        2017-10-15  0.030               0
        2017-10-16  0.029               0
        2017-10-17  0.027               0
        2017-10-18  0.027               0
        2017-10-19  0.027    buy        0
        2017-10-20  0.030               1
        2017-10-21  0.028               1
        2017-10-22  0.028               1
    """

    # Convert signals to invested status
    df['invested'] = 0
    if df['signal'].isin(['bullish', 'bearish']).any():
        df['invested'] = df['signal'].replace({'bullish': 1, 'bearish': 0, '': None})
    elif df['signal'].isin(['buy', 'sell']).any():
        df['invested'] = df['signal'].replace({'buy': 1, 'sell': 0, '': None})

    # shift everything 1 day later (because percentage changes only apply to the next day)
    df['invested'] = df['invested'].shift(1)
    # fill all None values with 0
    df['invested'] = df['invested'].ffill().fillna(0)
    # set df[invested] to None if df[signal] is None
    df.loc[df['signal'].isna(), 'invested'] = None
    return df


def df_group_invested(df):
    """ [df[invested, group_invested]] Group invested periods
    :param df: df[invested]
    :return: df[group_invested]

    Output:
        print(df[['close', 'invested', 'group_invested']])
                     close invested  group_invested
        date
        2010-09-26   0.062        0             NaN
        2010-09-27   0.062        0             NaN
        2010-09-28   0.062        1             1.0
        2010-09-29   0.062        1             1.0
        2010-09-30   0.062        1             1.0
        2010-10-01   0.062        1             1.0
        2010-10-02   0.061        1             1.0
        2010-10-03   0.061        1             1.0
        2010-10-04   0.061        1             1.0
        2010-10-05   0.061        0             NaN
        2010-10-06   0.063        0             NaN
        2010-10-07   0.067        1             2.0
        2010-10-08   0.087        1             2.0
        2010-10-09   0.094        1             2.0
        2010-10-10   0.097        1             2.0
    """
    # Group every connected invested block
    df['group_invested'] = (df['invested'].fillna(0).diff(1) == 1).cumsum()
    # Set everything else to None
    df.loc[df['invested'].isna() | (df['invested'] == 0), 'group_invested'] = None
    return df


def df_close_perc(df):
    """[df[close_perc]]"""
    df['close_perc'] = df['close'].pct_change(periods=1)  # * 100
    return df

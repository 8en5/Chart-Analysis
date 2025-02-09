import pandas as pd
import numpy as np

def zero_crossing(df, col):
    df_calc = df.copy()
    df_calc['sign'] = np.sign(df_calc[col]) # sign (-1, 0, 1), 0 is a problem, replace it with last value
    df_calc['sign'] = df_calc['sign'].replace(0, np.nan).ffill().bfill() # replace 0 with last value
    df_calc['sign_shift1'] = df_calc['sign'].shift(1) # shift 1
    # Calculate zero crossing (True, False)
    df_calc['zero_crossing'] = (df_calc['sign'] * df_calc['sign_shift1'] < 0) # advanced calculation - mult. with with last sign
    # Calculate direction of crossing (up, down)
    conditions = [
        df_calc['zero_crossing'] & (df_calc['sign'] > 0),  # above 0 -> 'up'
        df_calc['zero_crossing'] & (df_calc['sign'] < 0)  # below 0 -> 'down'
    ]
    values = ['up', 'down']
    df_calc['zero_crossing_dir'] = np.select(conditions, values, default='')
    #print(df_calc)
    # Result
    df = pd.merge(df, df_calc[['zero_crossing_dir']], on='date', how='left')
    cols = ['zero_crossing_dir']
    return df, cols


def calculate_crossings(df, col1, col2):
    """ Calculate crossing between two lines (columns)
    :return:
    """
    name_crossing = f'Crossing_{col1}-{col2}'
    # Diff
    df_calc = df.copy()
    df_calc['diff'] = df[col1] - df[col2]
    # If col1 crosses col2, then diff crosses the zero line
    df_calc, cols = zero_crossing(df_calc, 'diff')      # cols = ['zero_crossing', 'zero_crossing_dir']
    #print(df_calc)
    # Result
    df = pd.merge(df, df_calc[[cols[0]]], on='date', how='left')
    df = df.rename(columns={cols[0]: name_crossing})
    cols = [name_crossing]
    return df, cols
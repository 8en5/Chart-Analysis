import pandas as pd
import sys
import os

#------------------------- Helper -------------------------#

def disable_print():
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__  # standard


def pandas_print_all():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', None)

def pandas_print_width():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)



#------------------------- Functional -------------------------#

def get_period(period='D'):
    """ [util] Get amount of days based on the period
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


def get_intervals(data_length):
    """ [util cycle] Calculate intervals with fixed length
    :param data_length: len(df)
    :return: intervals -> [(start1, end1), (start2, end2), ...]

    Input: 1000
    Output: [(0, 350), (250, 600), (500, 850)]
    """
    window_size = 350   # const period days
    overlap = 100       # days overlapping
    intervals = []      # summary of all intervals

    # Return only 1 interval, if length < window_size
    if data_length < window_size:
        return [(0, data_length)]

    # Start iterating
    start = 0
    while start + window_size < data_length:
        intervals.append((start, start + window_size))
        start += (window_size - overlap)
    return intervals
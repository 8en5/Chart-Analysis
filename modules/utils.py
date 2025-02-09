import pandas as pd
import sys
import os


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
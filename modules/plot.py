
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from modules.indicators import get_indicator_col_names
from modules.file_handler import *


def df_group_invested_periods(df):
    """ Group invested periods
    :param df: df[invested]
    :return: df[group_inv]

    Output:
        print(df[['close', 'invested', 'group_inv']])
                         close invested  group_inv
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
    df['group_inv'] = (df['invested'].diff(1) == 1).cumsum()
    # Set everything else to None
    df.loc[df['invested'] == 0, 'group_inv'] = None
    return df


#---------------------- Lvl 2 - full figures (based on axes) ----------------------#

def fig_type1_default(df, title=''):
    """ [fig] Default plot
    - Plot 1: Course + Background invested
    """
    # Check columns
    minimal_columns = ['close', 'invested']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')
    # Default Plot
    fig, ax = plt.subplots(1, 1)                  # 1 Plot
    # Plot 1 (Course with evaluation)
    ax_course_highlight_invested(ax, df, 'rect') # ['background', 'start_stop', 'interruption_line', 'rect']
    ax_properties(ax, title=title)                             # Labels
    plt_properties(plt)                                        # Labels
    return fig

def fig_type2_indicator(df, indicator_name, title1=None, title2=None, suptitle=None):
    """ [fig] Plot indicator
    - Plot 1: Course + Background invested
    - Plot 2: Indicator + Background signals (['buy', 'sell', 'bullish', 'bearish'] from indicators)
    """
    # Check columns
    minimal_columns = ['close', 'invested', 'signal']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')

    # Indicator
    fig, ax = plt.subplots(2, 1, sharex=True)            # 2 Plots (share -> synch both plots during zoom)
    # Plot 1 (Course with evaluation)
    ax_course_highlight_invested(ax, df, 'rect')  # ['background', 'start_stop', 'interruption_line', 'rect']
    ax_properties(ax[0], title=title1)                               # Labels
    # Plot 2 (Indicator)
    ax_background_colored_highlighting(ax[1], df[['signal']])        # df['signal'] -> [buy, sell, bullish, bearish]
    func_ax_indicator(indicator_name, ax[1], df)               # Indicator
    ax_properties(ax[1], title=title2)                               # Labels
    fig_properties(fig, suptitle=suptitle)                           # Labels
    plt_properties(plt)                                              # Labels
    return fig

def save_fig(fig, file_path=None):
    """ [fig] Save matplotlib fig
    Calculate folder path from strategy name (when this class is called first) | default temp
    Calculate file name (from global counter, symbol and params | default counter
    """
    # Check file path
    if not file_path:
        # Set default folder path, if not defined
        # Folder
        folder_path = get_path() / 'data/analyse/visualize/temp'
        create_dir(folder_path)
        # File name (simple counter)
        available_paths = list_file_paths_in_folder(folder_path)
        counter = -1
        for path in available_paths:
            if path.stem.isdigit():
                n = int(path.stem)
                if n > counter:
                    counter = n
        file_path = folder_path / f'{counter+1}.png'

    # Save plot
    save_matplotlib_figure(fig, file_path.parent, file_path.stem, 'png')


#---------------------- Lvl 1.5 - visualize evaluation df[invested]  ----------------------#

def ax_course_highlight_invested(ax, df, key='rect'):
    """[ax] Call the different highlight functions by key"""
    match key:
        case None: return
        case 'background':
            _ax_course_highlight_invested_background(ax, df)
        case 'start_stop':
            _ax_course_highlight_invested_start_stop(ax, df)
        case 'interruption_line':
            _ax_course_highlight_invested_interruption_line(ax, df)
        case 'rect':
            _ax_course_highlight_invested(ax, df)
        case _:
            raise ValueError(f'Wrong highlight key: {key}')

def _ax_course_highlight_invested_background(ax, df):
    """[ax]"""
    # Course
    ax_course(ax, df, background=False, log=False)
    # Background color of df[invested]
    ax_background_colored_highlighting(ax, df[['invested']])


def _ax_course_highlight_invested_start_stop(ax, df):
    """[ax]"""
    ax_course(ax, df, background=True, log=False)
    # Groups of df[invested]
    df = df_group_invested_periods(df)
    for index, group in df.groupby('group_inv'):
        # Plot a dot at the first and last day of a invested group
        ax.scatter(group.index[0], group.loc[group.index[0], 'close'], color='green', marker='o', label='buy' if index==1 else None)
        ax.scatter(group.index[-1], group.loc[group.index[-1], 'close'], color='red', marker='o', label='sell' if index==1 else None)


def _ax_course_highlight_invested_interruption_line(ax, df):
    """[ax]"""
    # Course
    ax_course(ax, df, background=True, log=False)
    # Groups of df[invested]
    df = df_group_invested_periods(df)
    for index, group in df.groupby('group_inv'):
        # Plot green line only if df[invested] is in
        ax.plot(group.index, group['close'], linestyle='-', color='green', label='invested' if index==1 else None)


def _ax_course_highlight_invested(ax, df):
    """[ax]"""
    # Course
    ax_course(ax, df, background=False, log=False)
    # Groups of df[invested]
    df = df_group_invested_periods(df)
    for index, group in df.groupby('group_inv'):
        # Plot rect from first to the last day of a invested group
        x_start, x_end = group.index[0], group.index[-1]
        y_start, y_end = group.loc[group.index[0], 'close'], group.loc[group.index[-1], 'close']
        # Rect
        color = 'green' if y_end > y_start else 'red'
        rect = patches.Rectangle(
            (x_start, y_start),
            x_end - x_start,  # width
            y_end - y_start,  # height
            linewidth=1, edgecolor=color, facecolor=color, alpha=0.3
        )
        ax.add_patch(rect)


#---------------------- Lvl 1 - individual axes (which together form a fig) ----------------------#

def func_ax_indicator(indicator_name:str, *args):
    """ [ax] Central function to call the other modular functions
    :param indicator_name: name for the indicator defined in this file
    :param args: *args for the func: df
    :return: _ax_{indicator_name}
    """
    func_name = f'ax_{indicator_name}'
    # Check if function is defined
    func = globals().get(func_name)
    if not callable(func):
        raise ValueError(f'The function "{func_name}" does not exist - define it in plot.py')
    # Return called function
    return func(*args)

def keys_func_ax_indicator():
    """ [func] Return all keys with which you can call the function func_ax_indicator(key)
    :return: list[keys]
    """
    return [name.replace('ax_', '', 1) for name in globals().keys() if name.startswith('ax_')]


def ax_course(ax, df, background=False, log=False):
    """[ax]"""
    # Color
    color = 'lightgray' if background else 'black'
    # Plot
    if log:
        ax.semilogy(df.index, df['close'], linestyle='-', color=color, label='Course')    # log
    else:
        ax.plot(df.index, df['close'], linestyle='-', color=color, label='Course')        # linear


def ax_perc(ax, df):
    """[ax]"""
    # ['percentage_D']
    col_perc = get_indicator_col_names(df, 'perc')
    ax_ylim_threshold(df[col_perc], ax)
    ax.plot(df.index, df[col_perc], label=col_perc, color='blue', linestyle='-')                # Line Percentage
    #ax.bar(df.index, df[name_perc], color='blue', label=name_perc)                             # Bar Percentage

def ax_perc_bar(ax, df):
    """[ax]"""
    # ['percentage_D']
    col_perc = get_indicator_col_names(df, 'perc')
    # Frequency
    freq = col_perc.split('_')[-1]
    df_freq = df.resample(freq).first()
    #print(df_freq)
    # Calculate bar width and ylim
    bar_width = (df_freq.index[1] - df_freq.index[0]).days
    ax_ylim_threshold(df_freq[col_perc], ax)
    #ax.plot(df_grouped.index, df_grouped, label=f'percentage_{freq}', color='blue', linestyle='-')        # Line Percentage
    ax.bar(df_freq.index, df_freq[col_perc], label=f'percentage_{freq}', color='blue', width=bar_width)    # Bar Percentage


#--- ax Indicators ---#

def ax_BB(ax, df):
    """[ax]"""
    # ['BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'BBB_5_2.0', 'BBP_5_2.0'] - [Low, SMA, Up, Bandwith, Percentage]
    col_l, col_m, col_u = get_indicator_col_names(df, 'BB')
    ax_course(ax, df)
    ax.plot(df.index, df[col_m], label=col_m, color='orange', linestyle='-')
    ax.fill_between(df.index, df[col_l], df[col_u], color="darkviolet", alpha=0.3, label="Bollinger Bands")

def ax_MACD(ax, df):
    """[ax]"""
    # ['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'] - [MACD, Histogram (Diff), Signal]
    col_MACD, coll_diff, col_signal = get_indicator_col_names(df, 'MACD')
    ax.plot(df.index, df[col_MACD], label=col_MACD, color='blue', linestyle='-')              # Line MACD
    ax.plot(df.index, df[col_signal], label=col_signal, color='magenta', linestyle='-')       # Line Signal
    #ax.plot(df.index, df[name_diff], label=name_diff, color='pink', linestyle='-')           # Line Diff
    ax.bar(df.index, df[coll_diff], color='blue', label=coll_diff)                            # Bar Diff

def ax_RSI(ax, df):
    """[ax]"""
    # ['RSI_14', 'border_lower_30', 'border_upper_70']
    col_RSI, col_lower, col_upper = get_indicator_col_names(df, 'RSI')
    ax.plot(df.index, df[col_RSI], label=col_RSI, color='blue', linestyle='-')
    ax.plot(df.index, df[col_upper], label=col_upper, color='red', linestyle='--')
    ax.plot(df.index, df[col_lower], label=col_lower, color='green', linestyle='--')

def ax_SMA(ax, df):
    """[ax]"""
    # ['SMA_200', 'SMA_50]
    cols_SMA = get_indicator_col_names(df, 'SMA')
    if not isinstance(cols_SMA, list):
        cols_SMA = [cols_SMA]
    for col_SMA in cols_SMA:
        ax.plot(df.index, df[col_SMA], label=col_SMA, color='orange', linestyle='-')



#--- ax background color ---#

def ax_background_colored_highlighting(ax, df):
    """[ax]"""
    allowed_col = ['signal', 'invested']
    col = ''
    if any(element in allowed_col for element in df.columns):
        if 'signal' in df.columns:
            col = 'signal'
        elif 'invested' in df.columns:
            col = 'invested'
    else:
        raise ValueError(f'Column name {allowed_col} not in: {df.columns}')

    colors = {
        None: 'grey',
        # Signal - One event [buy, sell]
        'buy': 'lime',
        'sell': 'red',
        # Signal - Trend [bullish, bearish]
        'bullish': 'green',
        'bearish': 'salmon',
        # invested - [1, 0]
        1: 'green',
        0: 'salmon',
    }
    for i in range(0, len(df)-1):
        evaluation = df.iloc[i][col]
        if evaluation == '':
            continue
        if evaluation not in colors:
            print(f'Warning: evaluation "{evaluation}" not in color_status"')
        if evaluation in ['buy', 'sell']:
            # Vertical Line - concrete calculated signal
            color = colors[evaluation]
            ax.axvline(x=df.index[i], color=color, linestyle='-', linewidth=2)
        elif evaluation in ['bullish', 'bearish', 1, 0, None]:
            # Background color - general trend
            color = colors[evaluation]
            ax.axvspan(df.index[i], df.index[i+1], color=color, alpha=0.3)



#--- ax Graph elements (title, xlim, xlabel, grid, legend) ---#

def ax_ylim_threshold(values, ax, lower=0.05, upper=99.95):
    """[ax]"""
    lower_threshold = np.percentile(values.fillna(0), lower)  # lower threshold
    upper_threshold = np.percentile(values.fillna(0), upper)  # upper threshold
    #print(lower_threshold, upper_threshold)
    ax.set_ylim(lower_threshold, upper_threshold)


def ax_properties(ax, title=None, xlabel='Date', ylabel='Chart', grid=True, legend=True):
    """[ax]"""
    # Graph elements
    if title: ax.set_title(title)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if grid: ax.grid()
    if legend: ax.legend()


def fig_properties(fig, suptitle=None):
    """[fig]"""
    if suptitle: fig.suptitle(suptitle) # big title (over the normal title)


def plt_properties(plt, loc='upper left'):
    """[plt]"""
    plt.legend(loc=loc) # position legend
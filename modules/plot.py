
import numpy as np
import matplotlib.patches as patches
from matplotlib.pyplot import ylabel
from scipy.stats import alpha

from modules.indicators import get_indicator_col_names
from modules.file_handler import *


#---------------------- Lvl 2 - full figures (based on axes) ----------------------#

def fig_invested_default(df, title=''):
    """ [fig] Default plot
    - Plot 1: Course + Evaluation invested
    """
    # Check columns
    minimal_columns = ['close', 'invested']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')
    # Default Plot
    fig, ax = plt.subplots(1, 1)                     # 1 Plot
    # Plot 1 (Course with evaluation)
    ax_course(ax, df, True, True, True, True)  # Course
    ax_course_highlight_invested(ax, df, 'rect')             # Course with evaluation ['background', 'start_stop', 'interruption_line', 'rect']
    ax_properties(ax, title=title, xlabel='Date', ylabel='Chart') # Labels
    plt_properties(plt)                                           # Labels
    return fig

def fig_invested_indicator(df, indicator_name, title1=None, title2=None, suptitle=None):
    """ [fig] Plot indicator
    - Plot 1: Course + Evaluation invested
    - Plot 2: Indicator + Evaluation signals (['buy', 'sell', 'bullish', 'bearish'] from indicators)
    """
    # Check columns
    minimal_columns = ['close', 'invested', 'signal']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')

    # Indicator
    fig, ax = plt.subplots(2, 1, sharex=True)           # 2 Plots (share -> synch both plots during zoom)
    # Plot 1 (Course with evaluation)
    ax_course(ax[0], df, True, True, True, True) # Course
    ax_course_highlight_invested(ax[0], df, 'rect')             # Course with evaluation ['background', 'start_stop', 'interruption_line', 'rect']
    ax_properties(ax[0], title=title1, ylabel='Chart')               # Labels
    # Plot 2 (Indicator)
    ax_highlight_signals_vertical_line(ax[1], df)                    # Evaluate df['signal'] -> [buy, sell, bullish, bearish]
    func_ax_indicator(indicator_name, ax[1], df)               # Indicator
    ax_properties(ax[1], title=title2, xlabel='Date', ylabel='Chart')# Labels
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


#---------------------- Lvl 1.5 - highlight evaluation df[signal, invested]  ----------------------#

def ax_course_highlight_invested(ax, df, key='rect'):
    """[ax] Call the different highlight functions by key"""
    match key:
        case None: return
        case 'background':
            _ax_course_highlight_invested_background(ax, df)
        case 'dots':
            _ax_course_highlight_invested_dots(ax, df)
        case 'interruption_line':
            _ax_course_highlight_invested_interruption_line(ax, df)
        case 'rect':
            _ax_course_highlight_invested_rect(ax, df)
        case _:
            raise ValueError(f'Wrong highlight key: {key}')


def _ax_course_highlight_invested_background(ax, df):
    """[ax]"""
    # Background color for df[invested]
    color_map = {1: 'green', 0: 'red', None: 'grey'}
    for i in range(len(df) - 1):
        color = color_map.get(df.iloc[i]['invested'], 'grey')
        ax.axvspan(df.index[i], df.index[i + 1], color=color, alpha=0.1)


def _ax_course_highlight_invested_dots(ax, df):
    """[ax]"""
    for index, group in df.groupby('group_invested'):
        # Plot a dot at the first and last day of a invested group
        ax.scatter(group.index[0], group.loc[group.index[0], 'close'], color='green', marker='o', label='buy' if index==1 else None)
        ax.scatter(group.index[-1], group.loc[group.index[-1], 'close'], color='red', marker='o', label='sell' if index==1 else None)


def _ax_course_highlight_invested_interruption_line(ax, df):
    """[ax]"""
    # Groups of df[invested]
    for index, group in df.groupby('group_invested'):
        # Plot green line only if df[invested] is 1
        ax.plot(group.index, group['close'], linestyle='-', color='green', label='invested' if index==1 else None)


def _ax_course_highlight_invested_rect(ax, df):
    """[ax]"""
    # Groups of df[invested]
    for index, group in df.groupby('group_invested'):
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


def ax_highlight_signals_vertical_line(ax, df):
    # Vertical line for the signals
    color_map = {'buy': 'green', 'sell': 'red',
                 'bullish': 'green', 'bearish': 'red'}
    for idx, row in df.iterrows():
        if row['signal'] in ['buy', 'sell', 'bullish', 'bearish']:
            ax.axvline(x=idx, color=color_map[row['signal']], linestyle='-', alpha=0.3)



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
        raise ValueError(f'The function "{func_name}" does not exist in {keys_func_ax_indicator()} - define it in plot.py')
    # Return called function
    return func(*args)

def keys_func_ax_indicator():
    """ [func] Return all keys with which you can call the function func_ax_indicator(key)
    :return: list[keys]
    """
    return [name.replace('ax_', '', 1) for name in globals().keys() if name.startswith('ax_')]


def ax_course(ax, df, background=False, log=False, leading=False, invested=False):
    """[ax]"""
    # Color
    color = 'lightgray' if background else 'black'

    # df[signal] is None
    if leading:
        # Plot None values interrupted
        df['linestyle'] = df['signal'].notna().map({True: '-', False: '--'})
    else:
        # Plot everything as line
        df['linestyle'] = '-'

    # linear or log
    plot_func = ax.semilogy if log else ax.plot

    # Plot
    for index, (linestyle, sub_df) in enumerate(df.groupby('linestyle')):
        plot_func(sub_df.index, sub_df['close'], linestyle=linestyle, color=color, label='Course' if index==0 else None)

    # Highlight df[invested]
    if invested:
        for index, group in df.groupby('group_invested'):
            # Plot highlighted line only if df[invested] is 1
            plot_func(group.index, group['close'], linestyle='-', color='black') #label='invested' if index==1 else None


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



#--- ax Graph elements (title, xlim, xlabel, grid, legend) ---#

def ax_ylim_threshold(values, ax, lower=0.05, upper=99.95):
    """[ax]"""
    lower_threshold = np.percentile(values.fillna(0), lower)  # lower threshold
    upper_threshold = np.percentile(values.fillna(0), upper)  # upper threshold
    #print(lower_threshold, upper_threshold)
    ax.set_ylim(lower_threshold, upper_threshold)


def ax_properties(ax, title=None, xlabel='', ylabel='', grid=True, legend=True):
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
import numpy as np

from modules.indicators import get_indicator_col_names
from modules.utils import pandas_print_all


def ax_course(ax, df):
    ax.plot(df.index, df['close'], linestyle='-', color='black', label='Course')         # linear
    #ax.semilogy(df.index, df['close'], linestyle='-', color='black', label='Course')    # log

def ax_percentage(ax, df):
    # ['percentage_D']
    col_perc = get_indicator_col_names(df, 'perc')
    ax_ylim_threshold(df[col_perc], ax)
    ax.plot(df.index, df[col_perc], label=col_perc, color='blue', linestyle='-')                # Line Percentage
    #ax.bar(df.index, df[name_perc], color='blue', label=name_perc)                             # Bar Percentage

def ax_percentage_freq(ax, df):
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



def ax_BB(ax, df):
    # ['BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'BBB_5_2.0', 'BBP_5_2.0'] - [Low, SMA, Up, Bandwith, Percentage]
    col_l, col_m, col_u = get_indicator_col_names(df, 'BB')
    ax_course(ax, df)
    ax.plot(df.index, df[col_m], label=col_m, color='orange', linestyle='-')
    ax.fill_between(df.index, df[col_l], df[col_u], color="darkviolet", alpha=0.3, label="Bollinger Bands")

def ax_MACD(ax, df):
    # ['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'] - [MACD, Histogram (Diff), Signal]
    col_MACD, coll_diff, col_signal = get_indicator_col_names(df, 'MACD')
    ax.plot(df.index, df[col_MACD], label=col_MACD, color='blue', linestyle='-')              # Line MACD
    ax.plot(df.index, df[col_signal], label=col_signal, color='magenta', linestyle='-')       # Line Signal
    #ax.plot(df.index, df[name_diff], label=name_diff, color='pink', linestyle='-')           # Line Diff
    ax.bar(df.index, df[coll_diff], color='blue', label=coll_diff)                            # Bar Diff

def ax_RSI(ax, df):
    # ['RSI_14', 'border_lower_30', 'border_upper_70']
    col_RSI, col_lower, col_upper = get_indicator_col_names(df, 'RSI')
    ax.plot(df.index, df[col_RSI], label=col_RSI, color='blue', linestyle='-')
    ax.plot(df.index, df[col_upper], label=col_upper, color='red', linestyle='--')
    ax.plot(df.index, df[col_lower], label=col_lower, color='green', linestyle='--')

def ax_SMA(ax, df):
    # ['SMA_200']
    cols_SMA = get_indicator_col_names(df, 'SMA')
    for col_SMA in cols_SMA:
        ax.plot(df.index, df[col_SMA], label=col_SMA, color='orange', linestyle='-')




def ax_background_colored_signals(ax, df):
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



# Graph elements (title, xlim, xlabel, grid, legend)
def ax_ylim_threshold(values, ax, lower=0.05, upper=99.95):
    lower_threshold = np.percentile(values.fillna(0), lower)  # lower threshold
    upper_threshold = np.percentile(values.fillna(0), upper)  # upper threshold
    #print(lower_threshold, upper_threshold)
    ax.set_ylim(lower_threshold, upper_threshold)


def ax_default_properties(ax, title='', ylabel='Chart'):
    # Graph elements
    ax.set_title(title)
    #ax.set_xlabel('Date')
    #ax.set_ylabel(ylabel)
    ax.grid()
    ax.legend()


def ax_set_properties(ax, **kwargs):
    """ Sets multiple properties of a Matplotlib Axes object at once with default values.
    :param ax: The Axes object to modify.
    :param kwargs: dict, optional
        Keyword arguments specifying properties to set. Supported properties:
        - 'title' (str): Title of the plot (default: 'Default Title').
        - 'xlabel' (str): Label for the X-axis (default: 'Default X-Axis').
        - 'ylabel' (str): Label for the Y-axis (default: 'Default Y-Axis').
        - 'grid' (bool): Whether to display grid lines (default: True).

    Example:
    fig, ax = plt.subplots()
    set_ax_properties(ax, title='{symbol}', xlabel='Date', ylabel='Chart')
    plt.show()
    """
    defaults = {
        'title': '',
        'xlabel': '',
        'ylabel': '',
        'grid': True,
        'legend': True
    }

    # Update defaults with provided values
    for key, value in defaults.items():
        kwargs.setdefault(key, value)

    # Mapping of attribute names to methods
    mapping = {
        'title': ax.set_title,
        'xlabel': ax.set_xlabel,
        'ylabel': ax.set_ylabel,
        'grid': ax.grid,
        'legend': ax.legend
    }

    for key, value in kwargs.items():
        if key in mapping:
            mapping[key](value)  # Call the method with the value
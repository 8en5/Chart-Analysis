import numpy as np
import re

def get_col_names(df, regex_list:list):
    matching_columns = []
    for regex in regex_list:
        matches = [col for col in df.columns if re.fullmatch(regex, col)]
        matching_columns.extend(matches)
        if not matches:
            raise ValueError(f'Column {regex} not in df: {df.columns}')

    if len(matching_columns) == 1:
        return matching_columns[0]
    else:
        return matching_columns


def ax_course(ax, df):
    ax.plot(df.index, df['close'], linestyle='-', color='black', label='Course')         # linear
    #ax.semilogy(df.index, df['close'], linestyle='-', color='black', label='Course')    # log


def ax_percentage(ax, df):
    # ['percentage_D']
    regex_list = [r'percentage_.*']
    col_perc = get_col_names(df, regex_list)
    ax_ylim_threshold(df[col_perc], ax)
    ax.plot(df.index, df[col_perc], label=col_perc, color='blue', linestyle='-')                # Line Percentage
    #ax.bar(df.index, df[name_perc], color='blue', label=name_perc)                             # Bar Percentage

def ax_percentage_freq(ax, df):
    # ['percentage_D']
    regex_list = [r'percentage_.*']
    col_perc = get_col_names(df, regex_list)
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
    regex_list = [r'BBL_.*', r'BBM_.*', r'BBU_.*']
    col_l, col_m, col_u = get_col_names(df, regex_list)
    ax.plot(df.index, df[col_m], label=col_m, color='orange', linestyle='-')
    ax.fill_between(df.index, df[col_l], df[col_u], color="darkviolet", alpha=0.3, label="Bollinger Bands")

def ax_MACD(ax, df):
    # ['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'] - [MACD, Histogram (Diff), Signal]
    regex_list = [r'MACD_.*', r'MACDh_.*', r'MACDs_.*']
    col_MACD, coll_diff, col_signal = get_col_names(df, regex_list)
    ax.plot(df.index, df[col_MACD], label=col_MACD, color='blue', linestyle='-')              # Line MACD
    ax.plot(df.index, df[col_signal], label=col_signal, color='magenta', linestyle='-')       # Line Signal
    #ax.plot(df.index, df[name_diff], label=name_diff, color='pink', linestyle='-')           # Line Diff
    ax.bar(df.index, df[coll_diff], color='blue', label=coll_diff)                            # Bar Diff

def ax_RSI(ax, df):
    # ['RSI_14', 'border_lower_30', 'border_upper_70']
    regex_list = [r'RSI_.*', '.*lower.*', '.*upper.*']
    col_RSI, col_lower, col_upper = get_col_names(df, regex_list)
    ax.plot(df.index, df[col_RSI], label=col_RSI, color='blue', linestyle='-')
    ax.plot(df.index, df[col_upper], label=col_upper, color='red', linestyle='--')
    ax.plot(df.index, df[col_lower], label=col_lower, color='green', linestyle='--')

def ax_SMA(ax, df):
    # ['SMA_200']
    regex_list = [r'SMA_.*']
    col_SMA = get_col_names(df, regex_list)
    ax.plot(df.index, df[col_SMA], label=col_SMA, color='orange', linestyle='-')




def ax_background_colored_evaluation(ax, df):
    colors = {
        # Signal
        'buy': 'lime',
        'sell': 'red',
        # Trend
        'bullish': 'green',
        'bearish': 'salmon',
    }
    for i in range(0, len(df)-1):
        evaluation = df.iloc[i]['evaluation']
        if evaluation not in colors:
            print(f'Warning: evaluation "{evaluation}" not in color_status"')
        if evaluation in ['buy', 'sell']:
            # Vertical Line - concrete calculated signal
            color = colors[evaluation]
            ax.axvline(x=df.index[i], color=color, linestyle='-', linewidth=2)
        elif evaluation in ['bullish', 'bearish']:
            # Background color - general trend
            color = colors[evaluation]
            ax.axvspan(df.index[i], df.index[i+1], color=color, alpha=0.3)



# Graph elements (title, xlim, xlabel, grid, lagend)
def ax_ylim_threshold(values, ax, lower=0.05, upper=99.95):
    lower_threshold = np.percentile(values.fillna(0), lower)  # lower threshold
    upper_threshold = np.percentile(values.fillna(0), upper)  # upper threshold
    #print(lower_threshold, upper_threshold)
    ax.set_ylim(lower_threshold, upper_threshold)


def ax_graph_elements(ax, title='', ylabel='Chart'):
    # Graph elements
    ax.set_title(title)
    ax.set_xlabel('Date')
    ax.set_ylabel(ylabel)
    ax.grid()
    ax.legend()

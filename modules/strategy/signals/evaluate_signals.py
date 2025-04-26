import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import math

from modules.utils import json_dump_nicely


def evaluate_signals(df) -> dict|None:
    """ Calculate returns for all signals
    :param df: df[close, signal]
    :return:

    {
        "buy": {
            "2": [-0.01, 0.18, 0.03, -0.0, -0.03, 0.16, 0.04, 0.01, 0.02, 0.08, 0.01, 0.02, -0.03, -0.03, -0.03, 0.06, -0.04, -0.02, -0.03, -0.0, 0.18, 0.0, 0.03, -0.05, -0.01, -0.04, -0.04, -0.02, -0.06, 0.05, 0.07, 0.01, 0.22],
            "5": [-0.06, 0.48, 0.17, -0.06, -0.06, 0.09, 0.05, -0.11, 0.01, 0.02, -0.02, 0.04, -0.02, -0.08, -0.02, 0.1, 0.03, 0.08, -0.03, -0.06, 0.39, 0.09, -0.0, -0.07, -0.06, -0.02, 0.04, -0.14, -0.04, 0.05, 0.17, -0.16, 0.17],
            "10": [0.08, 0.79, 0.36, -0.11, -0.26, 0.19, 0.06, -0.14, -0.15, -0.28, -0.06, 0.16, -0.04, -0.08, 0.09, -0.08, -0.2, 0.14, 0.01, -0.01, 0.21, 0.04, 0.14, 0.11, -0.18, -0.08, 0.18, -0.23, 0.04, 0.14, 0.14, -0.14, 0.13],
            "30": [-0.11, 0.91, 0.86, -0.22, 0.09, 1.13, 0.14, -0.74, -0.29, -0.06, -0.05, -0.8, -0.36, 0.02, 0.04, -0.13, -0.17, 0.34, 0.22, 0.18, 0.13, 0.3, 0.44, 0.03, -0.3, 0.16, 0.14, -0.1, 0.06, 0.36, 0.24, -0.0, -0.08],
            "60": [-0.06, 2.14, 0.43, -0.04, 1.4, 1.47, -0.09, -0.82, 0.12, -0.01, -0.37, -1.01, 0.61, -0.09, -0.01, -0.39, 0.17, 0.27, 1.07, 0.26, 0.31, 0.48, 0.09, -0.09, -0.19, -0.06, -0.1, 0.06, 0.42, 0.43, 0.13, -0.39, -0.5],
            "120": [1.92, 3.32, 0.4, 1.32, 1.96, 1.82, -0.75, -0.67, -1.06, -0.2, -0.97, -0.27, 0.37, 0.14, 0.14, 0.06, -0.11, 0.56, 1.63, 0.87, 0.55, 0.39, 0.11, -0.2, -0.2, 0.2, 0.28, 0.12, 0.3, 0.31, -0.26]
        },
        "sell": {
            "2": [-0.16, -0.1, 0.04, 0.01, -0.04, -0.03, -0.21, -0.12, 0.04, -0.02, 0.02, -0.03, -0.31, 0.02, 0.06, 0.02, 0.02, -0.07, -0.01, 0.01, 0.25, -0.11, -0.05, 0.01, 0.05, -0.0, 0.11, -0.09, -0.03, 0.04, 0.17, -0.01, 0.02, 0.02],
            "5": [0.01, -0.25, 0.2, -0.04, -0.18, -0.11, -0.09, 0.05, -0.03, -0.03, -0.03, -0.01, -0.6, -0.09, 0.06, -0.0, 0.08, -0.2, -0.06, 0.04, 0.43, 0.02, 0.05, -0.01, -0.04, -0.05, 0.1, 0.14, -0.09, 0.12, 0.24, 0.0, 0.01, -0.12],
            "10": [-0.08, -0.04, 0.04, -0.24, -0.11, -0.3, -0.12, -0.13, -0.2, -0.03, -0.1, -0.04, -0.59, -0.02, 0.04, 0.15, 0.04, -0.17, 0.0, 0.07, 0.37, -0.06, 0.21, -0.17, -0.11, -0.13, 0.14, 0.03, -0.07, 0.14, 0.28, -0.04, 0.31, -0.07],
            "30": [-0.34, 0.15, 0.56, -0.07, -0.32, 0.2, 0.02, -0.21, -0.58, -0.84, -0.14, -0.74, -0.56, -0.21, 0.07, 0.08, -0.07, 0.14, -0.11, 0.67, 0.26, -0.05, 0.51, -0.28, -0.16, -0.21, 0.11, -0.05, 0.11, 0.36, 0.37, -0.23, 0.08, -0.4],
            "60": [-0.92, 1.24, 1.24, -0.29, 0.56, 1.8, 0.24, -0.39, -0.55, -1.12, -0.17, -0.83, -0.61, -0.1, -0.03, -0.0, -0.25, 0.22, -0.19, 0.41, 0.4, 0.23, 0.35, -0.09, -0.08, -0.12, 0.05, -0.02, 0.24, 0.53, 0.32, 0.01, -0.45],
            "120": [-0.68, 2.52, 0.97, 1.31, 1.45, 2.06, -0.09, -0.91, -0.61, -0.89, -1.05, -0.42, -0.27, -0.11, 0.16, 0.14, -0.01, 0.2, 0.82, 1.19, 0.59, 0.38, 0.24, -0.06, -0.13, -0.13, 0.26, 0.51, 0.27, 0.31, -0.09]
        }
    }
    """

    # Work on a copy
    df = df.copy()
    df['signal'] = df['signal'].replace({'bullish': 'buy', 'bearish': 'sell'})

    # Calculate all signals
    time_horizons = [2, 5, 10, 30, 60, 120]
    result_dict_returns = {'buy': {}, 'sell': {}}
    # Calculate future returns
    for signal_type in ['buy', 'sell']:
        signal_dates = df[df['signal'] == signal_type].index

        for time in time_horizons:
            returns = []
            for date in signal_dates:
                close_today = df.loc[date, 'close']
                idx_future = df.index.get_loc(date) + time
                if idx_future < len(df):
                    close_future = df.iloc[idx_future]['close']
                    r = calc_return(close_today, close_future, mode='log') # percentage, fracture, factor, log
                    returns.append(r)

            result_dict_returns[signal_type][time] = returns
            # Calculate states
            #result_dict[signal_type][time] = calc_stats(returns)

    #print(json_dump_nicely(result_dict_returns))
    return result_dict_returns


def calc_return(start_price, future_price, mode='log') -> float:
    """ Calculate course change (return)
    :param start_price: close today
    :param future_price: close future
    :param mode: [percentage, fracture, factor, log]
    :return: percentage change

            close_today  close_future  percentage  fracture  factor   log
        0            50             5       -0.90      0.10   -9.00 -2.30
        1            50            10       -0.80      0.20   -4.00 -1.61
        2            50            15       -0.70      0.30   -2.33 -1.20
        3            50            20       -0.60      0.40   -1.50 -0.92
        4            50            25       -0.50      0.50   -1.00 -0.69
        5            50            30       -0.40      0.60   -0.67 -0.51
        6            50            35       -0.30      0.70   -0.43 -0.36
        7            50            40       -0.20      0.80   -0.25 -0.22
        8            50            45       -0.10      0.90   -0.11 -0.11
        9            50            50        0.00      1.00   -0.00  0.00
        10           50            55        0.10      1.10    0.10  0.10
        11           50            60        0.20      1.20    0.20  0.18
        12           50            65        0.30      1.30    0.30  0.26
        13           50            70        0.40      1.40    0.40  0.34
        14           50            75        0.50      1.50    0.50  0.41
        15           50            80        0.60      1.60    0.60  0.47
        16           50            85        0.70      1.70    0.70  0.53
        17           50            90        0.80      1.80    0.80  0.59
        18           50            95        0.90      1.90    0.90  0.64
        19           50           100        1.00      2.00    1.00  0.69
        20           50           105        1.10      2.10    1.10  0.74
        21           50           110        1.20      2.20    1.20  0.79
        22           50           115        1.30      2.30    1.30  0.83
        23           50           120        1.40      2.40    1.40  0.88
        24           50           125        1.50      2.50    1.50  0.92
        25           50           130        1.60      2.60    1.60  0.96
        26           50           135        1.70      2.70    1.70  0.99
        27           50           140        1.80      2.80    1.80  1.03
        28           50           145        1.90      2.90    1.90  1.06
        29           50           150        2.00      3.00    2.00  1.10
        30           50           155        2.10      3.10    2.10  1.13
        31           50           160        2.20      3.20    2.20  1.16
        32           50           165        2.30      3.30    2.30  1.19
        33           50           170        2.40      3.40    2.40  1.22
        34           50           175        2.50      3.50    2.50  1.25
        35           50           180        2.60      3.60    2.60  1.28
        36           50           185        2.70      3.70    2.70  1.31
        37           50           190        2.80      3.80    2.80  1.34
        38           50           195        2.90      3.90    2.90  1.36
        39           50           200        3.00      4.00    3.00  1.39
    """
    if mode == 'percentage':
        return (future_price - start_price) / start_price
    elif mode == 'fracture':
        return future_price / start_price
    elif mode == 'factor':
        if future_price > start_price:
            return future_price/start_price - 1
        else:
            return -(start_price/future_price - 1)
    elif mode == 'log':
        return math.log(future_price / start_price)
    else:
        raise ValueError(f'Wrong key: {mode}')


def print_result_dict_states_as_df(result_dict_stats):
    """ Print result dict as pandas DataFrame
    :param result_dict_stats: states
    :return: None

    === buy ===
         count  return_mean  return_std  increase_perc
    2     33.0     0.022176    0.069586       0.515152
    5     33.0     0.029034    0.132041       0.484848
    10    33.0     0.029202    0.203580       0.545455
    30    33.0     0.072013    0.391196       0.575758
    60    33.0     0.170947    0.623287       0.515152
    120   31.0     0.388717    0.934689       0.677419

    === sell ===
         count  return_mean  return_std  increase_perc
    2     34.0    -0.014407    0.099071       0.500000
    5     34.0    -0.013929    0.162568       0.441176
    10    34.0    -0.029539    0.181195       0.382353
    30    34.0    -0.055415    0.343641       0.441176
    60    33.0     0.049407    0.594035       0.454545
    120   31.0     0.256395    0.811472       0.548387
    """
    for signal_type in ['buy', 'sell']:
        df = pd.DataFrame(result_dict_stats[signal_type])
        df = df.T
        print(f'\n=== {signal_type} ===')
        print(df)


def calc_states_from_dict(result_dict_returns):
    """ States for all returns lists
    :param result_dict_returns: raw returns as list
    :return: states from returns lists

    {
        "buy": {
            "2": {
                "count": 33,
                "return_mean": 0.02,
                "return_std": 0.07,
                "increase_perc": 0.52
            },
            "5": {
                "count": 33,
                "return_mean": 0.03,
                "return_std": 0.13,
                "increase_perc": 0.48
            },
            "10": {
                "count": 33,
                "return_mean": 0.03,
                "return_std": 0.2,
                "increase_perc": 0.55
            },
            "30": {
                "count": 33,
                "return_mean": 0.07,
                "return_std": 0.39,
                "increase_perc": 0.58
            },
            "60": {
                "count": 33,
                "return_mean": 0.17,
                "return_std": 0.62,
                "increase_perc": 0.52
            },
            "120": {
                "count": 31,
                "return_mean": 0.39,
                "return_std": 0.93,
                "increase_perc": 0.68
            }
        },
        "sell": {
            "2": {
                "count": 34,
                "return_mean": -0.01,
                "return_std": 0.1,
                "increase_perc": 0.5
            },
            "5": {
                "count": 34,
                "return_mean": -0.01,
                "return_std": 0.16,
                "increase_perc": 0.44
            },
            "10": {
                "count": 34,
                "return_mean": -0.03,
                "return_std": 0.18,
                "increase_perc": 0.38
            },
            "30": {
                "count": 34,
                "return_mean": -0.06,
                "return_std": 0.34,
                "increase_perc": 0.44
            },
            "60": {
                "count": 33,
                "return_mean": 0.05,
                "return_std": 0.59,
                "increase_perc": 0.45
            },
            "120": {
                "count": 31,
                "return_mean": 0.26,
                "return_std": 0.81,
                "increase_perc": 0.55
            }
        }
    }
    """
    #print(json_dump_nicely(result_dict_returns))
    #exit()
    result_dict_stats = {
        key_signal: {
            key_time: calc_state_from_list(value_returns)
            for key_time, value_returns in value_dict.items()
        }
        for key_signal, value_dict in result_dict_returns.items()
    }
    #print(json_dump_nicely(result_dict_stats))
    #exit()
    return result_dict_stats



def calc_state_from_list(returns):
    """ States from returns list
    :param returns: result_dict over multiple signals
    :return: evaluation dict
    """
    if len(returns) > 0:
        returns = np.array(returns)
        return_mean = np.mean(returns)
        return_std = np.std(returns)
        increase_perc = np.mean(returns > 0)
        #sharpe_ratio = return_mean / (return_std + 1e-6)
    else:
        return_mean = 0
        return_std = 0
        increase_perc = 0.5

    states_dict = {
        'count': len(returns),
        'return_mean': return_mean,
        'return_std': return_std,
        'increase_perc': increase_perc,
        #'sharpe_ratio': sharpe_ratio,
    }
    return states_dict


from collections import defaultdict
def join_multiple_returns(list_result_dict_returns):
    merged = defaultdict(lambda: defaultdict(list))
    for d in list_result_dict_returns:
        for key1, subdict in d.items():
            for key2, values in subdict.items():
                merged[key1][key2].extend(values)
    merged = {k: dict(v) for k, v in merged.items()}
    #print(json_dump_nicely(merged))
    return merged


#---------------------- Visualize ----------------------#

def fig_signals_evaluation(result_dict_stats, signal_type='all'):
    fig, ax = plt.subplots(4, 1)
    sub_fig_heatmap_ax(ax[0], result_dict_stats, metric='return', center=0, with_stat=True, signal_type=signal_type)
    sub_fig_heatmap_ax(ax[1], result_dict_stats, metric='increase_perc', center=0.5, with_stat=False, signal_type=signal_type)
    sub_fig_metric_curve(ax[2], result_dict_stats, metric='return', with_stat=True, signal_type=signal_type)
    sub_fig_metric_curve(ax[3], result_dict_stats, metric='increase_perc', with_stat=False, signal_type=signal_type)
    if signal_type == 'all': subtitle = f"Buy: {result_dict_stats['buy'][2]['count']} | Sell: {result_dict_stats['sell'][2]['count']}"
    elif signal_type == 'buy': subtitle = f"Buy: {result_dict_stats['buy'][2]['count']}"
    elif signal_type == 'sell': subtitle = f"Sell: {result_dict_stats['sell'][2]['count']}"
    else: raise ValueError(f'Wrong key: {signal_type}')
    fig.suptitle(subtitle)
    #plt.show()
    #exit()
    return fig


def sub_fig_heatmap_ax(ax, result_dict_stats, metric='return', center=0.0, with_stat=False, signal_type='all'):
    """
    :param ax:
    :param result_dict_stats:
    :param metric:
    :param center:
    :param with_stat:
    :param signal_type:
    :return:
    """
    data = {}
    text = {}
    for signal in result_dict_stats:
        if signal_type != 'all' and signal_type != signal:
            continue
        data[signal] = {}
        text[signal] = {}
        for time in result_dict_stats[signal]:
            if with_stat:
                value = result_dict_stats[signal][time][f'{metric}_mean']
            else:
                value = result_dict_stats[signal][time][metric]
            data[signal][time] = value
            if with_stat:
                std = result_dict_stats[signal][time][f'{metric}_std']
                text[signal][time] = f'{value:.2f}' + f'\n±{std:.2f}'
            else:
                text[signal][time] = f'{value:.2f}'

    df_data = pd.DataFrame(data).T
    df_text = pd.DataFrame(text).T
    #print(df_data)
    #print(df_text)
    #exit()

    colors = ['red', 'white', 'green']
    custom_cmap = LinearSegmentedColormap.from_list('custom_red_white_green', colors)
    sns.heatmap(df_data, annot=df_text, fmt='', cmap=custom_cmap, center=center, ax=ax)
    ax.set_title(f'{metric}')
    #ax.set_xlabel('Days after Signal')
    #ax.set_ylabel('Signal Type')



def sub_fig_metric_curve(ax, result_dict_stats, metric='return', with_stat=False, signal_type='all'):
    for signal in result_dict_stats:
        if signal_type != 'all' and signal_type != signal:
            continue
        x = list(result_dict_stats[signal].keys())
        if with_stat:
            y = [result_dict_stats[signal][t][f'{metric}_mean'] for t in x]
            yerr = [result_dict_stats[signal][t]['return_std'] for t in x]
            ax.errorbar(x, y, yerr=yerr, label=signal, capsize=5, marker='o')
            ax.axhline(0, color='black', linewidth=1, linestyle='--')
        else:
            y = [result_dict_stats[signal][t][metric] for t in x]
            ax.plot(x, y, label=signal, marker='o')
            ax.axhline(0.5, color='black', linewidth=1, linestyle='--')

    ax.set_xlabel('Days after Signal')
    ax.set_ylabel('return_mean')
    ax.set_title('return_mean vs Time')
    ax.legend()
    ax.grid(True)


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math


def evaluate_signals(df):
    # Work on a copy
    df = df.copy()
    df['signal'] = df['signal'].replace({'bullish': 'buy', 'bearish': 'sell'})

    # Calculate all signals
    time_horizons = [2, 5, 10, 30, 60, 120]
    result_dict = {'buy': {}, 'sell': {}}
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
                    r = compute_return(close_today, close_future, mode='log') # percentage, fracture, factor, log
                    returns.append(r)

            # Calculate states
            result_dict[signal_type][time] = compute_stats(returns)

    print(result_dict['buy'])
    print(result_dict['sell'])
    exit()

    sub_fig_heatmap(result_dict)
    sub_fig_metric_curve(result_dict)

    return result_dict


def compute_return(start_price, future_price, mode='log') -> float:
    """ Calculate course change
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


def compute_stats(returns):
    """ Evaluation over multiple signals
    :param returns: result_dict over multiple signals
    :return: evaluation dict
    """
    returns = np.array(returns)
    if len(returns) == 0:
        return None

    mean_return = np.mean(returns)
    std_return = np.std(returns)
    positive_rate = np.mean(returns > 0)
    sharpe_like = mean_return / (std_return + 1e-6)

    evaluation_dict = {
        'count': len(returns),
        'mean_return': mean_return,
        'std_return': std_return,
        'positive_rate': positive_rate,
        'sharpe_like': sharpe_like,
    }
    return evaluation_dict


def fig_signals_evaluation():
    fig, ax = plt.subplots(2, 1)
    pass

def sub_fig_heatmap(result_dict, metric='sharpe_like', include_std=True):
    data = {}
    annotations = {}
    for signal in result_dict:
        data[signal] = {}
        annotations[signal] = {}
        for t in result_dict[signal]:
            m = result_dict[signal][t][metric]
            std = result_dict[signal][t]['std_return']
            data[signal][t] = m
            annotations[signal][t] = f"{m:.2f}" + (f"\n±{std:.2f}" if include_std else "")
    df_plot = pd.DataFrame(data).T
    annot_df = pd.DataFrame(annotations).T
    sns.heatmap(df_plot, annot=annot_df, fmt='', cmap='coolwarm', center=0)
    plt.title(f'{metric} across Time Horizons')
    plt.xlabel('Signal Type')
    plt.ylabel('Days after Signal')
    plt.show()


def sub_fig_metric_curve(result_dict, metric='mean_return', errorbars=True):
    for signal in result_dict:
        x = list(result_dict[signal].keys())
        y = [result_dict[signal][t][metric] for t in x]
        yerr = [result_dict[signal][t]['std_return'] for t in x]
        if errorbars:
            plt.errorbar(x, y, yerr=yerr, label=signal, capsize=5, marker='o')
        else:
            plt.plot(x, y, label=signal, marker='o')
    plt.xlabel('Days after Signal')
    plt.ylabel(metric)
    plt.title(f'{metric} vs Time')
    plt.legend()
    plt.grid(True)
    plt.show()

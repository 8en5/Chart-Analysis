
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from modules.utils import pandas_print_width, json_dump_nicely
pandas_print_width()



def calc_states(df_summary):
    df = df_summary.drop(['index', 'close'], axis=1)
    result = {}
    for col in df.columns:
        min_vals = [x['min'] for x in df[col]]
        point_vals = [x['point'] for x in df[col]]
        max_vals = [x['max'] for x in df[col]]

        result[col] = {
            'min': {
                'mean': np.mean(min_vals),
                'std': np.std(min_vals, ddof=1)
            },
            'point': {
                'mean': np.mean(point_vals),
                'std': np.std(point_vals, ddof=1)
            },
            'max': {
                'mean': np.mean(max_vals),
                'std': np.std(max_vals, ddof=1)
            }
        }
    return result


def plot_mean_std(data):
    x = sorted(data.keys())

    y_min = [data[i]['min']['mean'] for i in x]
    y_point = [data[i]['point']['mean'] for i in x]
    y_max = [data[i]['max']['mean'] for i in x]

    std_min = [data[i]['min']['std'] for i in x]
    std_point = [data[i]['point']['std'] for i in x]
    std_max = [data[i]['max']['std'] for i in x]

    plt.figure(figsize=(10, 6))

    plt.errorbar(x, y_min, yerr=std_min, label='min', fmt='o', capsize=5)
    plt.errorbar(x, y_point, yerr=std_point, label='point', fmt='o', capsize=5)
    plt.errorbar(x, y_max, yerr=std_max, label='max', fmt='o', capsize=5)

    plt.xlabel('Tage')
    plt.ylabel('Wert')
    plt.title('Mittelwert & Standardabweichung über Zeit')
    plt.ylim(-3, 3)  # 👈 hier setzen wir die y-Achse
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_one_hist(df):
    # Beispiel: Spalte auswählen
    col = 7  # oder '-30', je nach dtype der Spaltennamen
    mins = []
    points = []
    maxs = []

    # Werte aus DataFrame extrahieren
    for val in df[col]:
        if isinstance(val, dict):
            mins.append(val.get('min', 0))
            points.append(val.get('point', 0))
            maxs.append(val.get('max', 0))

    # Plot
    plt.figure(figsize=(10, 6))
    bins = 30  # Anzahl der Balken im Histogramm

    plt.hist(mins, bins=bins, alpha=0.5, label='min', color='blue')
    plt.hist(points, bins=bins, alpha=0.5, label='point', color='orange')
    plt.hist(maxs, bins=bins, alpha=0.5, label='max', color='green')

    plt.title(f'Wertverteilung für Spalte {col}')
    plt.xlabel('Wert')
    plt.ylabel('Häufigkeit')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_hist(df):
    columns = df.columns
    n = len(columns)
    ncols = 2
    nrows = (n + 1) // ncols

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, 4 * nrows))
    axes = axes.flatten()

    for idx, col in enumerate(columns):
        mins, points, maxs = [], [], []

        for val in df[col]:
            if isinstance(val, dict):
                mins.append(val.get('min', 0))
                points.append(val.get('point', 0))
                maxs.append(val.get('max', 0))

        ax = axes[idx]
        bins = 20

        ax.hist(mins, bins=bins, alpha=0.5, label='min', color='blue')
        ax.hist(points, bins=bins, alpha=0.5, label='point', color='orange')
        ax.hist(maxs, bins=bins, alpha=0.5, label='max', color='green')

        ax.set_title(f'Wertverteilung: {col}')
        ax.set_xlabel('Wert')
        ax.set_ylabel('Häufigkeit')
        ax.legend()
        ax.grid(True)

    # Entferne unbenutzte Subplots
    for i in range(len(columns), len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    plt.show()

def plot_avg_return_over_time(df):

    days = []
    means = []

    for col in df.columns:
        vals = [v['point'] for v in df[col] if isinstance(v, dict)]
        if vals:
            days.append(int(col))
            means.append(np.mean(vals))

    plt.figure(figsize=(10, 6))
    plt.plot(days, means, marker='o')
    plt.axhline(0, color='grey', linestyle='--')
    plt.title('Durchschnittliche Entwicklung nach Kaufsignal')
    plt.xlabel('Tage nach Signal')
    plt.ylabel('Ø Rendite')
    plt.grid(True)
    plt.show()

def plot_hit_rate(df):
    days = []
    hit_rates = []

    for col in df.columns:
        vals = [v['point'] for v in df[col] if isinstance(v, dict)]
        if vals:
            days.append(int(col))
            hit_rates.append(np.mean(np.array(vals) > 0))

    plt.figure(figsize=(10, 6))
    plt.plot(days, hit_rates, marker='o', color='green')
    plt.axhline(0.5, color='grey', linestyle='--')
    plt.title('Trefferquote (Rendite > 0)')
    plt.xlabel('Tage nach Signal')
    plt.ylabel('Anteil positiver Signale')
    plt.grid(True)
    plt.show()

def evaluate_signals(df):
    # cut df to relevant columns
    df = df[['close', 'signal']].copy()
    # use numeric index
    df.index = range(len(df))

    eval_dict_signals = {
        'buy': [],
        'sell': []
    }
    for index, row in df.iterrows():
        if row['signal'] in ['buy', 'sell', 'bullish', 'bearish']:
            eval_dict_one_signal = {
                'index': index,
                'close': row['close'],
                **evaluate_signal(index, df)
            }
            if row['signal'] in ['buy', 'bullish']:
                eval_dict_signals['buy'].append(eval_dict_one_signal)
            else:
                eval_dict_signals['sell'].append(eval_dict_one_signal)
            #print(eval_dict_signals)
            #exit()

    df_buy = pd.DataFrame(eval_dict_signals['buy'])
    #df_sell = pd.DataFrame(eval_dict_signals['sell'])
    #print(df_buy)
    #exit()


    #result = calc_states(df_buy)
    #print(json_dump_nicely(result))
    #plot_mean_std(result)

    df_buy = df_buy.drop(columns=['index', 'close'], errors='ignore')
    #plot_hist(df_buy)
    #plot_avg_return_over_time(df_buy)
    plot_hit_rate(df_buy)
    exit()



def evaluate_signal(index, df):
    times = [-30, -14, -7, 2, 7, 14, 30, 60, 120, 180]
    eval_dict_one_signal = {}
    for time in times:
        index_time = index + time # e.g. 36+(-14) or 39 +30
        if time < 0:                 # go back
            if index_time >= 0:      # check index not negative
                df_period = df[index_time: index+1].copy()
                eval_dict_one_signal[time] = min_max_perc(df_period, 'past')
            else:
                df_period = df[index: index + 1].copy()
                eval_dict_one_signal[time] = min_max_perc(df_period, 'past')
        else:                        # go in the future
            if index_time+1 < len(df): # check index smaller then len(df)
                df_period = df[index: index_time+1].copy()
                eval_dict_one_signal[time] = min_max_perc(df_period, 'future')
            else:
                df_period = df[index: index + 1].copy()
                eval_dict_one_signal[time] = min_max_perc(df_period, 'past')
    #print(eval_dict_one_signal)
    #exit()
    return eval_dict_one_signal


def min_max_perc(df, direction):
    if direction == 'past':
        close_point = df['close'].iloc[0]
        close = df['close'].iloc[-1]
    elif direction == 'future':
        close_point = df['close'].iloc[-1]
        close = df['close'].iloc[0]
    else:
        raise ValueError(f'Wrong key: {direction}')

    close_min = df['close'].min()
    close_max = df['close'].max()

    """
    result_dict = {
        'min': close_min / close,
        'point': close_point / close,
        'max': close_max / close
    }
    """
    result_dict = {
        'min': factor(close, close_min),
        'point': factor(close, close_point),
        'max': factor(close, close_max)
    }
    #print(result_dict)
    #exit()
    return result_dict

def factor(now, future):
    if future > now:
        f = round(future / now - 1, 3)
    else:
        f = round(-(1 / (future / now) - 1), 3)
    return f


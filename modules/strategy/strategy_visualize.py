""" Strategy object - to plot and save/show
    # Aim
Visualize strategies (systematically)
Show graphically the effectiveness of a specific strategy

Input: df
- min:
    - df[close, invested]
- extended:
    - plot_type = 2:
        - df[<indicators>, signal]
- optional (defined in init() or init_analysis()):
    - folder_path: indicator_name (else temp)
    - file_name: symbol, params (else only counter)

Output: Plot (save/show) that visualizes the strategy
"""

from pathlib import Path
import matplotlib.pyplot as plt

from modules.file_handler import *
from modules.plot import *
from modules.course import get_symbol_paths


class VisualizeStrategy:
    """ Visualize strategies and save or show plots
    """

    def __init__(self, df):
        """
        :param df: df[close, invested, (<indicators>, signal)]
        """
        self.df = df                                # [df] data for the plot

        # Default values
            # Strategy
        self.indicator_name = None                  # [str] strategy name
            # Plot
        self.plot_type = 1                          # [mapping] Plot type: 0 (only course) | 1 (course + indicator)
        self.show_plot = False                      # [bool] if true show plot - plt.show()
        self.save_plot = True                       # [bool] if true save plot
        self.title = None                           # [df] title -> evaluation (statistics)
        self.folder_path = None                     # [Path] for saving the plot
        self.filename = None                        # [str] for saving the plot


    def run(self):
        """ Main routine to plot (show and/or save) the strategy
        """
        # Check
        if not 'close' in self.df.columns:
            raise AssertionError(f'Min requirement failed: no column "close" -> run load_pandas_from_symbol(symbol)')
        if not 'invested' in self.df.columns:
            raise AssertionError(f'Min requirement failed: no column "invested" -> run func_get_invested_from_indicator(indicator_name, df)')
        if not self.show_plot and not self.save_plot:
            raise AssertionError('Warning Abort: Check control parameters -> show and save is False')


        match self.plot_type:                   # Plot type
            case 1:                             # default
                self._plot_type1_default()
            case 2:                             # indicator
                self._plot_type2_indicator()
            case _:
                raise ValueError(f'Wrong plot type [1-2]: {self.plot_type}')

        if self.save_plot:
            self._save_fig()
        if self.show_plot:
            plt.show()


    def _plot_type1_default(self):
        """ Default plot
        - Plot 1: Course + Background invested
        """
        # Default Plot
        self.fig, ax = plt.subplots(1, 1)                         # 1 Plot
         # Plot 1 (Course)
        ax_background_colored_highlighting(ax, self.df[['invested']])         # df['invested'] -> [in,out]
        ax_course(ax, self.df)                                                # Course
        ax_default_properties(ax, self.title)                                 # Labels

    def _plot_type2_indicator(self):
        """ Plot indicator
        - Plot 1: Course + Background invested
        - Plot 2: Indicator + Background signals (['buy', 'sell', 'bullish', 'bearish'] from indicators)
        """
        # Check
        if not 'signal' in self.df.columns:
            raise AssertionError(f'Min requirement failed: no column "signal" -> run set_manual_strategy_<name>')

        # Indicator
        self.fig, ax = plt.subplots(2, 1, sharex=True)            # 2 Plots (share -> synch both plots during zoom)
        # Plot 1 (Course)
        ax_background_colored_highlighting(ax[0], self.df[['invested']])      # df['invested'] -> [in,out]
        ax_course(ax[0], self.df)                                             # Course
        ax_default_properties(ax[0], self.title)                              # Labels
        # Plot 2 (Indicator)
        ax_background_colored_highlighting(ax[1], self.df[['signal']])         # df['signal'] -> [buy, sell, bullish, bearish]
        func_ax_indicator(ax[1], self.df)                                # Indicator
        ax_default_properties(ax[1], self.indicator_name)                      # Labels


    def _save_fig(self):
        """ Save matplotlib fig
        Calculate folder path from strategy name (when this class is called first) | default temp
        Calculate file name (from global counter, symbol and params | default counter
        """

        # Set default folder path, if not defined
        if not self.folder_path:
            # Calculate default folder the very first time - then use this default folder for all other plots
            if not VisualizeStrategy.folder_path:
                # Set folder path with time stamp
                self.folder_path = get_path('ws') / 'data/analyse/temp' / pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
                VisualizeStrategy.folder_path = self.folder_path
            else:
                self.folder_path = VisualizeStrategy.folder_path

        # Set default file name, if not defined
        if not self.filename:
            # Simple counter
            self.filename = VisualizeStrategy.counter
            VisualizeStrategy.counter += 1

        # Save plot
        save_matplotlib_figure(self.fig, self.folder_path, self.filename)


def _calc_full_df(symbol_path, indicator_name, params):
    """ Calculate full df[close, <indicators>, signal, invested]
    :param symbol_path: path to symbol
    :param indicator_name: indicator name
    :param params: 1x params for the indicator
    :return:
    """
    # Local import to avoid circle imports between strategy_visualize.py and evaluate_invested.py
    from modules.strategy.strategy_invested import func_get_invested_from_indicator
    from evaluate_invested import get_evaluation_statistics

    # Load symbol - df[close]
    df = load_pandas_from_file_path(symbol_path)[['close']]
    # Calculate signals - df[<indicators>, signal]
    df = func_get_invested_from_indicator(indicator_name, df, params)
    # Calculate invested - df[invested]
    df = get_evaluation_statistics(df)
    #print(df)
    return df


def manager_visualize(source_symbols, indicator_name, params, study_type=''):
    """
    :param source_symbols: multiple sources possible: course_selection_key / list symbol_names
    :param indicator_name:
    :param params:
    :param study_type:
    :return:
    """

    symbol_paths = get_symbol_paths(source_symbols)
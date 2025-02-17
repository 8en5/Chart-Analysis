""" Strategy object - to plot and save/show
    # Aim
Visualize strategies (systematically)
Show graphically the effectiveness of a specific strategy

Input: df
- min: df[close, invested]
- extended:
    - plot_type = 2: df[<indicators>, signal]
- optional (defined in init() or init_analysis()):
    - folder_path: strategy_name (else temp)
    - file_name: symbol, params (else only counter)

Output: Plot (save/show) that visualizes the strategy
"""

from pathlib import Path
import matplotlib.pyplot as plt

from modules.strategy.manual_strategies import *
from modules.file_handler import *
from modules.plot import *
from modules.strategy.evaluate_strategy import EvaluateStrategy


class VisualizeStrategy:
    """ Visualize strategies and save or show plots
    """

    folder_path = None                              # [Path] storage location for saving all plots (is defined in the first call)
    counter = 1                                     # [int] counter for numbering the plots (+1 for each plot)

    def __init__(self, df):
        """
        :param df: df[close, invested, (<indicators>, signal)]
        """
        self.df = df                                # [df] data for the plot
        self.evaluation = None                      # [df] evaluation (statistics)

        # Default values
            # Strategy - only to calculate the file name
        self.strategy_name = ''                     # [str] strategy name (e.g. BB, MACD, RCI)
        self.symbol = ''                            # [str] coin or share (e.g. BTC)
        self.params = None                          # [dict[str,list]] all params for the strategy (has values only in param study | else None)
            # Plot
        self.plot_type = 1                          # [mapping] Plot type: 0 (only course) | 1 (course + indicator)
        self.show_plot = False                      # [bool] if true show plot - plt.show()
        self.save_plot = True                       # [bool] if true save plot


    def init(self, **kwargs):
        """ Set specific values for the use case
        :param kwargs: dict[key, value]
        """
        for key, value in kwargs.items():
            if hasattr(self, key):  # Check if the attribute exists
                setattr(self, key, value)  # Set the value
            else:
                raise AttributeError(f'"{key}" is not a valid attribute of this class')


    def init_analysis(self, strategy_name, symbol, params):
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.params = params
        self.plot_type = 2
        self.save_plot = True


    def run(self):
        """ Main routine to plot (show and/or save) the strategy
        """
        # Check
        if not 'close' in self.df.columns:
            raise AssertionError(f'Min requirement failed: no column "close" -> run load_pandas_from_symbol(symbol)')
        if not 'invested' in self.df.columns:
            raise AssertionError(f'Min requirement failed: no column "invested" -> run set_manual_strategy_<name>(df)')
        if not self.show_plot and not self.save_plot:
            raise AssertionError('Warning Abort: Check control parameters -> show and save is False')

        self.evaluation = 'TODO evaluation'  # EvaluateStrategy.get_statistics(self.df)

        match self.plot_type:                   # Plot type
            case 1:                             # default
                self._plot_type1_default()
            case 2:                             # indicator
                self._plot_type2_indicator()
            case 3:                             # specific
                self._plot_type3_specific()
            case _:
                raise ValueError(f'Wrong plot type [1-3]: {self.plot_type}')

        if self.save_plot:
            self._save_fig()
        if self.show_plot:
            plt.show()

        VisualizeStrategy.counter += 1


    def _plot_type1_default(self):
        """ Default plot
        - Plot 1: Course + Background invested
        """
        # Default Plot
        self.fig, ax = plt.subplots(1, 1)                         # 1 Plot
         # Plot 1 (Course)
        ax_background_colored_signals(ax, self.df[['invested']])              # df['invested'] -> [in,out]
        ax_course(ax, self.df)                                                # Course
        ax_default_properties(ax, self.evaluation)                            # Labels

    def _plot_type2_indicator(self):
        """ Plot indicator
        - Plot 1: Course + Background invested
        - Plot 2: Indicator + Background signals (['buy', 'sell', 'bullish', 'bearish'] from indicators)
        """
        # Check
        if self.strategy_name == '':
            raise AssertionError(f'strategy_name is not defined - cant call ax_<strategy_name>(). Maybe choose plot_type = 1')
        if not 'signal' in self.df.columns:
            raise AssertionError(f'Min requirement failed: no column "signal" -> run set_manual_strategy_<name>')

        # Indicator
        self.fig, ax = plt.subplots(2, 1, sharex=True)            # 2 Plots (share -> synch both plots during zoom)
        # Plot 1 (Course)
        ax_background_colored_signals(ax[0], self.df[['invested']])           # df['invested'] -> [in,out]
        ax_course(ax[0], self.df)                                             # Course
        ax_default_properties(ax[0], self.evaluation)                         # Labels
        # Plot 2 (Indicator)
        ax_background_colored_signals(ax[1], self.df[['signal']])             # df['signal'] -> [buy, sell, bullish, bearish]
        func_ax_indicator = globals()[f'ax_{self.strategy_name}']             # e.g. ax_BB
        func_ax_indicator(ax[1], self.df)                                     # Indicator
        ax_default_properties(ax[1], self.strategy_name)                      # Labels

    def _plot_type3_specific(self):
        """ Plot specific
        Call specific plot defined in manual_strategies.py
        """
        # Specific
        get_func_plot(self.df)                                                # func defined in  manual_strategies.py


    def _save_fig(self):
        """ Save matplotlib fig
        Calculate folder path from strategy name (when this class is called first) | default temp
        Calculate file name (from global counter, symbol and params | default counter
        """

        # Set folder path with time stamp in the first call for all other plots
        if not VisualizeStrategy.folder_path:
            base_folder = get_path('ws') / 'data/analyse'
            if self.strategy_name != '':
                # path separated by strategy name
                VisualizeStrategy.folder_path = base_folder / self.strategy_name / pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
            else:
                # default folder path
                VisualizeStrategy.folder_path = base_folder / 'temp' / pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Set file name - '{counter}_{symbol}_param1-value1_param2-value2'
        file_name = f'{VisualizeStrategy.counter}'      # 1
        if self.symbol != '':
            file_name += f'_{self.symbol}'              # 1_ETH
        if self.params is not None:
            for key, value in self.params.items():      # e.g. '1_ETH_bb_l-5_bb_std-1.5'
                file_name += f'_{key}-{value}'

        # Save plot
        save_matplotlib_figure(self.fig, VisualizeStrategy.folder_path, file_name)
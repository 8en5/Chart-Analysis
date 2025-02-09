""" # Aim
Visualize strategies
Show graphically the effectiveness of a specific strategy
Same logic and reusable code for each new strategy (calculating when to invest, plotting and saving, parameter and symbol studies)

   # Architecture
Indicators, plots of the indicators and calculation of the strategies each in a separate file
For generic visualization and plots in this file 2 classes:
- VisualizeStrategy
  - Each individual plot is processed in an object
  - Input: strategy, symbol, params (1x params for calculating the indicators and signals)
  - Output: Plot that visualizes the strategy
- VisualizeStrategyManager
  - manage the various processes of the analysis (program flow)
    - 4 main logics based on the two bools param_study and loop_symbols
      - for testing: plot and show 1 plot with default params
      - for analysing: save plots from param study and symbol study in the corresponding folders

    # Instructions (for defining a new strategy)
Define strategy in manual_strategy.py
Define indicator in indicators.py and plot in plot.py
Check new strategy with run_type = 1
"""

import sys
import os
ws_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")) # Workspace
sys.path.append(ws_dir) # add ws to sys-path to run py-file in separate cmd

import matplotlib.pyplot as plt

from modules.strategy.manual_strategies import *
from modules.file_handler import *
from modules.plot import *
from modules.strategy.eval_strategy import *

pd.set_option('future.no_silent_downcasting', True) # if values are converted down (value to nan - when calculating df[invested] based on df[signal])


class VisualizeStrategyManager:
    """
    This class manages the different program flows
    4 different main logics result from the two bools param_study and loop_symbols
    Based on the program flow, all symbols or parameter studies are analyzed as individual objects in the VisualizeStrategy class
    """
    def __init__(self, strategy_name, loop_param_study=False, loop_symbols=False):
        # Strategy
        self.strategy_name = strategy_name          # [str] strategy name (e.g. BB, MACD, RCI)

        # Program flow control
            # main logic - 4 possible ways: [F,F] plot one symbol | [T,F] param study for one symbol | [F,T] loop symbols for one param | [T,T] loop symbols with param study
        self.loop_param_study = loop_param_study    # [bool], if true run param study | else default param
        self.loop_symbols = loop_symbols            # [bool], if true loop over all symbols | else default symbol


    def run(self):
        """ Main function that controls all other functions
        (The only function that is called from outside the class)

        Attention: Visualization only for manual analysis. Not suitable for large amounts of data -> then mathematical
         evaluation without individual plots
.
        Program flow depends on the two bool variables [self.loop_symbols, self.loop_param_study]
         [F,F] plot one symbol (for testing or specific analysis)
         [T,F] param study for one symbol (for testing the parameter study)
         [F,T] loop symbols for one param (strategy with 1x specific params applied to all symbols)
         [T,T] loop symbols with param study (parameter study for all multiple courses)
        """
        if self.loop_symbols:
            folder_path = os.path.join(get_path('course_cc'), 'yaml')   # [yaml, api]
            file_paths_symbols = list_file_paths_in_folder(folder_path, '.csv')
            assert len(file_paths_symbols) > 100, 'Over 100 symbols - Should there really be so many graphics created?'
            # Loop over all symbols
            for index, file_path_symbol in enumerate(file_paths_symbols):
                symbol = get_filename_from_path(file_path_symbol)
                print(f'{index + 1}/{len(file_paths_symbols)}: {symbol}')
                if self.loop_param_study:            # 4) Loop symbols with param study
                    self.routine_param_study(symbol)
                    print('\n')
                else:                                # 3) Loop symbols for ONE parameter
                    self.routine_one_default_param(symbol, False)
        else:
            symbol = 'BTC'  # default hard coded symbol
            if self.loop_param_study:                # 2) Param study for ONE symbol (save plot without show)
                self.routine_param_study(symbol)
            else:                                    # 1) Test -> Plot for ONE symbol (only show without saving)
                self.routine_one_default_param(symbol, True)


    def routine_one_default_param(self, symbol, show=False):
        """ Routine for one default param
        No param study, use the default params defined in the strategy for the specified symbol
        """
        # VisualizeStrategy Class
        vs = VisualizeStrategy(self.strategy_name, symbol)
        vs.set_bools_program_flow(False, show, not show)
        vs.run_main_routine()


    def routine_param_study(self, symbol):
        """ Routine for param_study
        Loop over all params combinations for the specified symbol
        """
        # Param study - Loop over all params im params_study
        params_study = get_all_combinations_from_params_study(self.strategy_name)
        assert len(params_study) > 100, 'Over 100 params combinations - Should there really be so many graphics created?'
        for index, params in enumerate(params_study):
            self.params = params
            print(f'{index+1}/{len(params_study)}: {params}')

            # VisualizeStrategy Class
            vs = VisualizeStrategy(self.strategy_name, symbol, self.params)
            vs.set_bools_program_flow(True, False, True)
            vs.run_main_routine()


class VisualizeStrategy:
    """
    This class is responsible for the calculation, evaluation and the plot of a single symbol
    - Input: strategy, symbol, params (1x params for calculating the indicators and signals)
    - Output: Plot and evaluation of the strategy for this one individual symbol
    (Parameter studies and symbol analyses are controlled in the class VisualizeStrategyManager)
    """
    def __init__(self, strategy_name, symbol , params=None):
        # Strategy
        self.strategy_name = strategy_name          # [str] strategy name (e.g. BB, MACD, RCI)
        self.params = params                        # [dict[str,list]] init, all params for the strategy (has values only in param study | else None)

        # Symbol
        self.symbol = symbol                        # [str] init, coin or share (e.g. BTC)

        # type of plot
        self.plot_type = 1                          # [mapping], Plot type: 0 (only course) | 1 (course + indicator)


        # Initialize variables, value assigned at runtime
            # Strategy
        self.param_study = False                    # [bool], if true params_study

            # df (containing calculated data)
        self.df_raw = pd.DataFrame()                # [df] raw data from loading the course: df['time', 'high', 'low', 'open', 'volumefrom', 'volumeto', 'close']
        self.df_min = pd.DataFrame()                # [df] min input for the following functions: df['close']
        self.df_invested = pd.DataFrame()           # [df] normally df['invested'], but currently additionally the calculations of the indicators and signals (for the plots)

            # how to deal with the plot (calculated from loop_param_study and loop_symbols)
        self.show_plot = False                      # [bool] init, if true show plot - plt.show()
        self.save_plot = False                      # [bool] init, if true save plot


    def set_bools_program_flow(self, param_study, show_plot, save_plot):
        """ Set the bools, which control the program flow
        """
        self.param_study = param_study
        self.show_plot = show_plot
        self.save_plot = save_plot


    def run_main_routine(self):
        """ Main routine
        1. calculate strategy df[<indicators>, 'signal', 'invested']
        2. Plot: show or save (depending on the program flow)
        3. Reset for the next params in the params_study
        """
        self._load_symbol()
        self._manual_strategy() # calculate df_invested
        if self.show_plot or self.save_plot:
            self._plot()
            if self.show_plot:
                plt.show()


    def _load_symbol(self):
        """ Load course from csv
        self.symbol
        self.df_raw
        self.df_min
        """
        df = load_pandas_from_symbol(self.symbol)
        self.df_raw = df            # raw data for the next cycle in param study: df = ['time', 'high', 'low', 'open', 'volumefrom', 'volumeto', 'close']
        self.df_min = df[['close']] # min input for functions: df = ['close']


    def _manual_strategy(self):
        """ Call function set_manual_strategy_{name}()
        self.df_invested
        """
        func_set_manual_strategy = globals()[f'set_manual_strategy_{self.strategy_name}']
        df = func_set_manual_strategy(self.df_min)
        self.df_invested = df


    def _plot(self):
        """ Plot strategy
        Default '0' (for every strategy):
          Plot 1: Course + Status (status = background color, if in or out)
        '1' with Indicator (only if strategy == Indicator)
          Plot 1: Course + Status (status = background color, if in or out)
          Plot 2: Indicator + Evaluation (evaluation = signals ['buy', 'sell', 'bullish', 'bearish'] from indicators)
        """
        if self.plot_type == 0:
            # Default Plot
            fig, ax = plt.subplots(1, 1)
             # Plot 1 (Course)
            ax_background_colored_signals(ax, self.df_invested[['invested']])     # df['invested'] -> [in,out]
            ax_course(ax, self.df_invested)                                       # Course
            ax_graph_elements(ax, self.symbol)                                    # Labels
        elif self.plot_type == 1:
            # Default Plot
            fig, ax = plt.subplots(2, 1, sharex=True)                 # share -> synch both plots during zoom
            # Plot 1 (Course)
            ax_background_colored_signals(ax[0], self.df_invested[['invested']])  # df['invested'] -> [in,out]
            ax_course(ax[0], self.df_invested)                                    # Course
            ax_graph_elements(ax[0], self.symbol)                                 # Labels
            # Plot 2 (Indicator BB)
            ax_background_colored_signals(ax[1], self.df_invested[['signal']])    # df['signal'] -> [buy, sell, bullish, bearish]
            func_ax_indicator = globals()[f'ax_{self.strategy_name}']                           # e.g. ax_BB
            func_ax_indicator(ax[1], self.df_invested)                            # Indicator
            ax_graph_elements(ax[1], self.strategy_name)                          # Labels
        else:
            raise ValueError(f'Wrong plot type (0 or 1): {self.plot_type}')

        if self.save_plot:
            self._save_fig(fig)


    def _save_fig(self, fig):
        """ Save matplotlib fig
        param study: analyse/crypto_compare/{strategy}/parameter_study/{symbol}
        normal:      analyse/crypto_compare/{strategy}/symbols
        """
        # Folder and name
        base_folder_path = str(os.path.join(get_path('analyse_cc'), self.strategy_name))
        if self.param_study:
            folder_path = os.path.join(base_folder_path, f'parameter_study/{self.symbol}')
            file_name = f'{self.symbol}' # e.g. 'ETH_bb_l-5_bb_std-1.5' | '{symbol}_param1-value1_param2-value2
            for key, value in self.params.items():
                file_name += f'_{key}-{value}'
        else:
            folder_path = os.path.join(base_folder_path, 'symbols') # e.g. ETH
            file_name = self.symbol

        # Save
        save_matplotlib_figure(fig, folder_path, file_name)



if __name__ == "__main__":
    """ # Explanation
    There are 4 different main logics based on the two bools param_study and loop_symbols
    
        # Instructions
    - set strategy name
    - set run_type (for program flow, based on the two bools)
      - (if run_type = 1, a default symbol can be set in VisualizeStrategyManager.run())
    - (set plot type to define which plots are in the fig (only course, course + indicator): self.plot_type = [1-3])
    """

    strategy = 'MACD'     # MACD, BB, RSI
    run_type = 1      # Program flow [1-4]

    match run_type:
        case 1: # [F,F] plot one symbol with default params (for testing or specific analysis)
            param_study = False
            loop_symbols = False
            print(f'<{run_type}> - plot one symbol with default params (for testing)')
        case 2: # [T,F] param study for one symbol (for testing the parameter study)
            param_study = True
            loop_symbols = False
            print(f'<{run_type}> - param study for one symbol')
        case 3: # [F,T] loop symbols with default params (strategy with 1x specific params applied to all symbols)
            param_study = False
            loop_symbols = True
            print(f'<{run_type}> - loop symbols with default params')
        case 4: # [T,T] loop symbols with param study (parameter study for all multiple courses)
            param_study = True
            loop_symbols = True
            print(f'<{run_type}> - loop symbols with param study')
        case _:
            raise ValueError(f'run_type [1-4]: {run_type}')

    vsm = VisualizeStrategyManager(strategy, param_study, loop_symbols)
    vsm.run()


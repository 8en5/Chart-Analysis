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
from matplotlib.style.core import available

from modules.file_handler import *
from modules.plot import *
from modules.course import get_symbol_paths
from modules.params import get_all_params_combinations_from_yaml


def _plot_type1_default(df, title=''):
    """ Default plot
    - Plot 1: Course + Background invested
    """
    # Check columns
    minimal_columns = ['close', 'invested']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')
    # Default Plot
    fig, ax = plt.subplots(1, 1)  # 1 Plot
    # Plot 1 (Course)
    ax_background_colored_highlighting(ax, df[['invested']])  # df['invested'] -> [in,out]
    ax_course(ax, df)  # Course
    ax_default_properties(ax, title)  # Labels
    return fig

def _plot_type2_indicator(df, indicator_name, title1='', title2=''):
    """ Plot indicator
    - Plot 1: Course + Background invested
    - Plot 2: Indicator + Background signals (['buy', 'sell', 'bullish', 'bearish'] from indicators)
    """
    # Check columns
    minimal_columns = ['close', 'invested', 'signal']
    if not set(minimal_columns).issubset(df.columns):
        raise AssertionError(f'Min requirement failed: not all columns {minimal_columns} in {df.columns}')

    # Indicator
    fig, ax = plt.subplots(2, 1, sharex=True)            # 2 Plots (share -> synch both plots during zoom)
    # Plot 1 (Course)
    ax_background_colored_highlighting(ax[0], df[['invested']])      # df['invested'] -> [in,out]
    ax_course(ax[0], df)                                             # Course
    ax_default_properties(ax[0], title1)                             # Labels
    # Plot 2 (Indicator)
    ax_background_colored_highlighting(ax[1], df[['signal']])        # df['signal'] -> [buy, sell, bullish, bearish]
    func_ax_indicator(indicator_name, ax[1], df)               # Indicator
    ax_default_properties(ax[1], title2)                             # Labels
    return fig


class VisualizeStrategy:
    """ Visualize strategies and save or show plots
    """

    def __init__(self, df, file_path=None):
        """
        :param df: df[close, invested, (<indicators>, signal)]
        :param file_path: saving the plot
        """
        self.df = df
        self.file_path = file_path

        self.save_plot = True
        self.show_plot = False

        self.run()


    def run(self):
        """ Main routine to plot (show and/or save) the strategy
        """
        # Check

        if not self.show_plot and not self.save_plot:
            raise AssertionError('Warning Abort: show and save is False - nothing will happen')

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


    def _save_fig(self):
        """ Save matplotlib fig
        Calculate folder path from strategy name (when this class is called first) | default temp
        Calculate file name (from global counter, symbol and params | default counter
        """

        # Check file path
        if not self.file_path:
            # Set default folder path, if not defined
            # Folder
            folder_path = get_path() / 'data/analyse/visualize/temp'
            # File name (simple counter)
            available_paths = list_file_paths_in_folder(folder_path)
            counter = 0
            for path in available_paths:
                if path.stem.isdigit():
                    n = int(path.stem)
                    if n > counter:
                        counter = n
            self.file_path = folder_path / f'{counter}.png'

        # Save plot
        save_matplotlib_figure(self.fig, self.file_path.parent, self.file_path.stem, 'png')





#---------------------- Manger for Visualization ----------------------#

def manager_visualize_strategy(indicator_name, source_symbols, source_params, study_type='params'):
    """
    :param indicator_name: indicator name
    :param source_symbols: multiple sources possible: course_selection_key / list symbol_names
    :param source_params: different sources possible - key_course_selection / list_params_combinations / None (default key_course_selection)
    :param study_type: for folder structure - params/symbols or symbols/params
    """
    # Prepare variables
    # Symbols
    symbol_paths = get_symbol_paths(source_symbols)
    # Param combinations
    if isinstance(source_params, str):  # key from yaml
        params_combinations = get_all_params_combinations_from_yaml(indicator_name, source_params)
    elif isinstance(source_params, list):  # already a list of params_combinations
        params_combinations = source_params
    elif source_params is None:  # default params
        params_combinations = get_all_params_combinations_from_yaml(indicator_name, 'default')
    else:
        raise ValueError(f'Wrong instance (not [str, list, None] of source_params: {source_params}')


    # Loop over symbols and params
    if study_type == 'params':
        i = 1
        l_p = len(params_combinations)
        l_s = len(symbol_paths)
        for i_p, params in enumerate(params_combinations):
            for i_s, symbol_path in enumerate(symbol_paths):
                print(f'{i}/{l_s * l_p}: \t\t {i_p + 1}/{l_p} {params} \t\t {i_s + 1}/{l_s}: {symbol_path.stem}')
                UnifiedVisualizeStrategy(symbol_path, indicator_name, params, study_type=study_type)
                i += 1
                print()
    elif study_type == 'symbols':
        i = 1
        l_s = len(symbol_paths)
        l_p = len(params_combinations)
        for i_s, symbol_path in enumerate(symbol_paths):
            for i_p, params in enumerate(params_combinations):
                print(f'{i}/{l_s * l_p}: \t\t {i_s + 1}/{l_s}: {symbol_path.stem} \t\t {i_p + 1}/{l_p} {params}')
                UnifiedVisualizeStrategy(symbol_path, indicator_name, params, study_type=study_type)
                i += 1
                print()
    else:
        raise ValueError(f'study_type must be [params, symbols]: {study_type}')



class UnifiedVisualizeStrategy:
    def __init__(self, symbol_path, indicator_name, params, study_type='params'):
        df = self._calc_indicator_and_invested(symbol_path, indicator_name, params)
        result_dict = self._calc_evaluation(df)
        file_path = self._calc_file_path(indicator_name, symbol_path.stem, params, study_type)
        title = self._calc_title(result_dict)

        VisualizeStrategy(df, 2, title, file_path, indicator_name)


    def _calc_indicator_and_invested(self, symbol_path, indicator_name, params):
        """ Calculate full df[close, <indicators>, signal, invested]
        :param symbol_path: path to symbol
        :param indicator_name: indicator name
        :param params: 1x params for the indicator
        :return:
        """
        # Local import to avoid circle imports between strategy_visualize.py and evaluate_invested.py
        from modules.strategy.strategy_invested import func_get_invested_from_indicator
        # Load symbol - df[close]
        df = load_pandas_from_file_path(symbol_path)[['close']]
        # Calculate signals and invested - df[<indicators>, signal, invested]
        df = func_get_invested_from_indicator(indicator_name, df, params)
        # print(df)
        return df


    def _calc_evaluation(self, df):
        from modules.strategy.evaluate_invested import get_evaluation_statistics
        result_dict = get_evaluation_statistics(df)
        return result_dict


    def _calc_params_to_str(self, params):
        """ Convert params dict to str (for folder name)
        :param params: params dict
        :return: params str

        Input:  {'m_fast': 14, 'm_slow': 30, 'm_signal': 70}
        Output: '14_30_70'
        """
        # Check
        if not isinstance(params, dict):
            raise TypeError(f'parameter is not a dict: {params}')
        # Calculate string - e.g. '5_1.5'
        params_str = '_'.join(str(value) for value in params.values())
        return params_str


    def _calc_file_path(self, indicator_name, symbol, params, study_type='params'):
        """ Calculate file path for the plot
        Aim: Centralized storage that creates a collection across different test runs

        :param indicator_name: indicator name
        :param symbol: symbol (course)
        :param params: params (1x dict)
        :param study_type: [params, symbols]
        :return:
        """
        params_str = self._calc_params_to_str(params) # params as string
        # Calculate folder path
        if study_type == 'params': # params oriented (for one param there are many symbols)
            file_path = get_path() / f'data/analyse/visualize/{study_type}/{indicator_name}/{params_str}/{symbol}.png'
        elif study_type == 'symbols': # symbols oriented (for one symbol there are many params
            file_path = get_path() / f'data/analyse/visualize/{study_type}/{indicator_name}/{symbol}/{params_str}.png'
        else:
            raise ValueError(f'study_type must be [params, symbols]: {study_type}')
        return file_path


    def _calc_title(self, result_dict):
        title = f"S = {result_dict['S']:.2f} | BaH = {result_dict['BaH']:.2f} | Diff = {result_dict['diff']:.2f}"
        return title



manager_visualize_strategy('MACD', 'default', 'visualize', study_type='symbols')

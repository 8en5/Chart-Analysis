
import itertools
import pandas as pd

from modules.file_handler import get_path
from modules.strategy.invested.study_indicator_invested import manager_study_indicator_invested
from modules.strategy.signals.study_indicator_signals import manager_study_indicator_signals

def meta_study(func):
    """ Meta study -> multiple studies
    :return: None
    """
    # Parameters for the study
    # Indicator
    indicator_names = ['BB', 'MACD', 'RSI']

    # Symbols
    sources_courses = ['default']

    # Params
    source_params = 'visualize'  # default, visualize, brute_force, optimization

    # Storage location
    base_folder = get_path('study') / f'Study_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    #base_folder = None

    # Start study over all combinations
    for indicator_name, source_courses in itertools.product(indicator_names, sources_courses):
        folder = base_folder / f'{indicator_name}_{source_courses}'
        func(
            indicator_name, source_courses, source_params,
            save_evaluation=True, save_plot=False, base_folder=folder
        )



def study(func):
    """ 1x study with specific selected parameters
    :return: None
    """
    # Parameters for the study
    # Save evaluation results
    save_evaluation = True

    # Save all plots
    save_plot = False

    # Indicator
    indicator_name = 'MACD'   # MACD, BB, RSI

    # Symbols
    source_courses = 'default'     # default
    #source_courses = 'BTC'
    #source_courses = ['BTC', 'ETH', 'ADA']

    # Params
    source_params = 'visualize'  # default, visualize, (brute_force, optimization)

    # Storage location
    base_folder = get_path('study') / f'Study_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    folder = base_folder / f'{indicator_name}_{source_courses}'
    #folder = None

    # Start study over all combinations
    func(
        indicator_name, source_courses, source_params,
        save_evaluation, save_plot, folder
    )




if __name__ == "__main__":

    study_type = 'signals' # invested

    if study_type == 'signals':
        function = manager_study_indicator_signals
    elif study_type == 'invested':
        function = manager_study_indicator_invested
    else:
        raise ValueError(f'Wrong key: {study_type}')

    study(function)
    #meta_study(function)

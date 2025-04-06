
import itertools
import pandas as pd

from modules.file_handler import get_path
from modules.study.study_indicator_invested import manager_study_indicator_invested, save_evaluation_results


def meta_study():
    """ Meta study -> multiple studies
    :return: None
    """
    # Parameters for the study
    # Indicator
    indicator_names = ['BB', 'MACD', 'RSI']

    # Symbols
    sources_courses = ['default']

    # Params
    source_params = 'brute_force'  # default, visualize, brute_force, optimization

    # Start study over all combinations
    base_folder = get_path('study') / f'Study_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    for indicator_name, source_courses in itertools.product(indicator_names, sources_courses):
        manager_study_indicator_invested(
            indicator_name, source_courses, source_params,
            save_evaluation=True, save_plot=False, base_folder=base_folder
        )



def study():
    """ 1x study with specific selected parameters
    :return: None
    """
    # Parameters for the study

    # Save evaluation results
    save_evaluation = True

    # Save all plots
    save_plot = False

    # Storage location
    base_folder = get_path('study') / f'Study_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    #base_folder = None

    # Indicator
    indicator_name = 'BB'   # MACD, BB, RSI

    # Symbols
    source_courses = 'default'     # default
    #source_courses = 'BTC'
    #source_courses = ['BTC', 'ETH', 'ADA']

    # Params
    source_params = 'visualize'  # default, visualize, (brute_force, optimization)

    # Start study over all combinations
    manager_study_indicator_invested(
        indicator_name, source_courses, source_params,
        save_evaluation, save_plot, base_folder
    )




if __name__ == "__main__":
    meta_study()
    #study()

from modules.meta_study.study_visualize import manager_visualize_strategy


def main():
    """ [loop fig] Study to visualize strategies (indicator params)
    :return: None
    """

    # Parameters for the study
      # Indicator
    indicator_name = 'BB'   # MACD, BB, RSI

      # Symbols - [course_selection_key, str, list]
    source_courses = 'default'     # default
    #source_courses = 'BTC'
    #source_courses = ['BTC', 'ETH', 'ADA']

      # Params
    source_params = 'visualize'    # default, visualize, (brute_force, optimization)

      # Study type
    study_type = 'params'   # params, symbols


    # Run
    manager_visualize_strategy(indicator_name, source_courses, source_params, study_type)


if __name__ == "__main__":
    main()
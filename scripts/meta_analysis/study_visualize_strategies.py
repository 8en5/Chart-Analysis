
from modules.meta_study.study_visualize import manager_visualize_strategy


def main():
    # Parameters for the study
      # Indicator
    indicator_name = 'BB'   # MACD, BB, RSI

      # Symbols - [course_selection_key, str, list]
    source_symbols = 'default'     # default
    #source_symbols = 'BTC'
    #source_symbols = ['BTC', 'ETH', 'ADA']

      # Params
    source_params = 'visualize'    # default, visualize, (brute_force, optimization)

      # Study type
    study_type = 'params'   # params, symbols


    # Run
    manager_visualize_strategy(indicator_name, source_symbols, source_params, study_type)


if __name__ == "__main__":
    main()
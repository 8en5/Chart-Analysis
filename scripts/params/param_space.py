
from modules.utils import pandas_print_width, pandas_print_all
from modules.file_handler import load_pandas_from_symbol
from modules.strategy.strategy_invested import func_get_invested_from_indicator
from modules.params import get_params_from_yaml
from modules.strategy.evaluate_invested import evaluate_invested_multiple_cycles, evaluate_invested


#pandas_print_width()
pandas_print_all()


def main():
    # Load course
    df = load_pandas_from_symbol('ADA')

    # Indicator
    indicator_name = 'MACD'
    params = get_params_from_yaml(indicator_name, 'default')

    # Invested
    df = func_get_invested_from_indicator(indicator_name, df, [20, 30, 20])
    #print(df)

    # Result dict
    result_dict = evaluate_invested_multiple_cycles(df)
    #result_dict = evaluate_invested(df)
    print(result_dict)


if __name__ == "__main__":
    main()
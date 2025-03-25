
from modules.utils import pandas_print_width, pandas_print_all
from modules.file_handler import load_pandas_from_symbol
from modules.indicators import func_indicator
from modules.strategy.strategy_invested import func_get_invested_from_indicator
from modules.params import get_params_from_yaml
from modules.strategy.evaluate_invested import evaluate_invested_multiple_cycles


#pandas_print_width()
pandas_print_all()


def main():
    # Load course
    df = load_pandas_from_symbol('BTC')

    # Indicator
    indicator_name = 'MACD'
    params = get_params_from_yaml(indicator_name, 'default')

    # Invested
    #df = func_indicator(indicator_name, df, None)
    df = func_get_invested_from_indicator(indicator_name, df, [5, 10, 5])
    print(df)

    # Result dict
    result_dict = evaluate_invested_multiple_cycles(df)
    print(result_dict)


if __name__ == "__main__":
    main()
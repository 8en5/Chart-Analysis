import pandas as pd


def get_df_from_list(list_data, col='close'):
    """ Convert a list into a df with date as index
    :param list_data: list[int]
    :param col: name
    :return: df[index, name]
    """
    # Daily dates with lengeth list_data
    dates = pd.date_range(start="2023-01-01", periods=len(list_data), freq="D")

    # Pandas Frame
    df = pd.DataFrame({
        'date': dates,
        col: list_data
    })

    # Set index
    df.set_index('date', inplace=True)
    #print(df)
    return df
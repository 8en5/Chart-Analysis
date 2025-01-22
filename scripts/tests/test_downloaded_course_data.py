
from modules.file_handler import *


def check_course_all_dates(file_path):
    """ Go through all the downloaded course data and check if the date is complete from start to finish
        and not duplicated
    """

    symbol = get_filename_from_path(file_path)

    # Load course
    df = load_pandas_from_file_path(file_path)
    #print(df.index)

    # Comparison
    comparison_dates = pd.date_range(df.index.min(), df.index.max())
    #print(comparison_dates)

    # Difference
    missing_dates = comparison_dates.difference(df.index)
    duplicates  = df.index[df.index.duplicated()]
    #print(missing_dates)
    #print(duplicates)
    #print(difference_dates)

    if not missing_dates.empty or not duplicates.empty:
        error_dict[symbol] = (missing_dates, duplicates)
        print(f'Dates not correct for "{symbol}"')


def routine_checking_all_dates():
    directory = get_path('course_cc')
    for root, dirs, files in os.walk(directory):
        if root == directory:  # skip directory (temp files), only sub folders
            continue
        #print(root, dirs, files)
        print(f'Folder: {root}')
        for file in files:
            if file.endswith('.csv'):   # only csv files
                file_path = os.path.join(root, file)
                #print(file_path)
                check_course_all_dates(file_path)


if __name__ == "__main__":
    error_dict = {}

    routine_checking_all_dates()

    print()
    if len(error_dict) == 0:
        print('For all courses dates correct')
    else:
        print('Errors:')
        print(f'Symbol: [missing_dates], [duplicates]')
        for key, value in error_dict.items():
            print(f'{key}: {list(value[0].strftime('%Y-%m-%d'))}, {list(value[1].strftime('%Y-%m-%d'))}')

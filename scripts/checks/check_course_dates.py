
from modules.file_handler import *


def check_course_all_dates(file_path):
    """
    Load course from file and check, that all dates are available and not duplicated
    """

    symbol = file_path.stem

    # Load course
    df = load_pandas_from_file_path(file_path)
    # print(df.index)

    # Check validity
    if not 'close' in df.columns:
        print(f'\tFile "{symbol}" is not a course')
        return

    # Comparison
    comparison_dates = pd.date_range(df.index.min(), df.index.max())
    #print(comparison_dates)

    # Get all differences
    missing_dates = comparison_dates.difference(df.index)
    duplicates = df.index[df.index.duplicated()]
    #print(missing_dates)
    #print(duplicates)
    #print(difference_dates)

    if not missing_dates.empty or not duplicates.empty:
        error_dict[symbol] = (missing_dates, duplicates)
        print(f'\tDates not correct for "{symbol}"')


def routine_checking_all_dates():
    """
    Go through all downloaded courses in a directory and check the data
    """
    directory = get_path('cc')
    for file in directory.rglob('*'):
        if file.is_dir():
            print(f'Folder: {file}')
        elif file.is_file() and file.suffix == '.csv':
            #print(f'File: {file}')
            check_course_all_dates(file)



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

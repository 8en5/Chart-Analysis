

from modules.file_handler import *


def test_path():
    tests = [None, 'ws', 'cc', 'wrong_key']
    for index, test in enumerate(tests):
        print(f'{index}: {test}')
        try:
            if test:
                print(get_path(test))
            else:
                print(get_path())
        except Exception as e:
            print('Exception:', e)
        print()


def test_create_dir():
    workspace_path = get_path()
    tests = [
        workspace_path / 'data',                        # folder exists
        str(workspace_path),                            # type string
        workspace_path / 'data/analyse/new_test',       # new folder
        workspace_path.parents[0] / 'not_in_workspace'  # folder not in workspace (1 folder structure above)
    ]
    for index, test in enumerate(tests):
        print(f'{index}: {test}')
        try:
            if test:
                create_dir(Path(test))
        except Exception as e:
            print('Exception:', e)
        print()


def test_find_file_in_directory():
    tests = [
        'BTC.csv',          # find
        'wrong_symbol.csv'  # not finding
    ]

    folder_path = get_path('cc')
    #folder_path = str(get_path('cc'))   # test type string
    for index, test in enumerate(tests):
        print(f'{index}: {test}')
        try:
            if test:
                filename = test
                file_path = get_file_in_directory(folder_path, filename)
                print('file_path:', file_path)
                print('type:', type(file_path))
        except Exception as e:
            print('Exception:', e)
        print()


def test_multiple_function():
    pass


if __name__ == "__main__":

    test_path()
    #test_create_dir()
    #test_find_file_in_directory()
    #test_multiple_function()
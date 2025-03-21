
from modules.file_handler import *
from modules.plot import *



def plot_all_courses():
    """ Loop over all symbols and plot them
    """
    # Input folder courses
    folder_path_courses = get_path() / 'data/course/crypto_compare/api'
    if not folder_path_courses.exists():
        raise ValueError(f'Error: Folder "{folder_path_courses}" does not exist')
    file_path_courses = list_file_paths_in_folder(folder_path_courses, '.csv')

    # Loop over all symbols
    for index, file_path in enumerate(file_path_courses):
        print(f'{index + 1}/{len(file_path_courses)}: {file_path.stem}')
        df = load_pandas_from_file_path(file_path)
        plot_course(df, file_path.stem)


def plot_course(df, symbol):
    # Figure
    fig, ax = plt.subplots(1, 1)
    # Plot 1 (Course)
    ax_course(ax, df)
    ax_properties(ax, symbol)

    # Save plot
    folder_path = get_path() / 'data/analyse/all_courses'
    save_matplotlib_figure(fig, folder_path, symbol)


if __name__ == "__main__":
    plot_all_courses()
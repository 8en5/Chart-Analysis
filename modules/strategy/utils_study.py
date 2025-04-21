
from pathlib import Path

from modules.file_handler import get_path


def calc_file_path(indicator_name:str, course:str, params: dict | list, study_type='params',
                   index=-1, base_folder:Path=None) -> Path:
    """ [fig] Calculate file path for the plot
    Aim: Targeted saving of the different variants

    :param indicator_name: indicator name
    :param course: symbol (course)
    :param params: params (1x dict or list)
    :param study_type: [params, symbols]
    :return: path to save the plot
    """
    params_str = calc_params_to_str(params) # params as string
    suffix = ''
    if index >= 0:
        suffix = f'_{index}'
    # Calculate folder path
    if not base_folder:
        base_folder = get_path() / f'data/analyse/visualize'
        if study_type == 'params': # params oriented (for one param there are many symbols)
            file_path = base_folder / f'{study_type}/{indicator_name}/{params_str}/{course}{suffix}.png'
        elif study_type == 'symbols': # symbols oriented (for one symbol there are many params
            file_path = base_folder / f'{study_type}/{indicator_name}/{course}/{params_str}{suffix}.png'
        else:
            raise ValueError(f'study_type must be [params, symbols, study]: {study_type}')
    else: # Study
        file_path = base_folder / f'{params_str}/{course}{suffix}.png'

    return file_path


def calc_params_to_str(params: dict | list) -> str:
    """ [fig] Convert params dict to str (for folder name)
    :param params: params dict
    :return: params str

    Input:  {'m_fast': 14, 'm_slow': 30, 'm_signal': 70} / [14, 30, 70]
    Output: '14_30_70'
    """
    # Check
    if isinstance(params, dict):
        params_str = '_'.join(str(value) for value in params.values())
    elif isinstance(params, list):
        params_str = '_'.join(str(value) for value in params)
    elif not params:
        params_str = 'None'
    else:
        raise TypeError(f'parameter is not a dict: {params}')
    return params_str
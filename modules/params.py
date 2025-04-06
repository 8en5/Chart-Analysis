import itertools
import ast

from modules.file_handler import get_path, load_yaml_from_file_path


def get_params_variation(indicator_name, source_params:str|list|dict|None) -> list[dict|list[float]]:
    """ Central function to get a list of params variations
    :param indicator_name: indicator name
    :param source_params: source [key, list, dict]
    :return: list of param variations
    """
    if isinstance(source_params, str):  # key from yaml (standard)
        # 'visualize' -> [{'m_fast': 10, 'm_slow': 20, 'm_signal': 30}, {'m_fast': 10, 'm_slow': 20, 'm_signal': 90}, ...]
        params_variations = get_all_params_variations_from_yaml(indicator_name, source_params)
    elif isinstance(source_params, list):
        if isinstance(source_params[0], dict): # already a list of params_variations
            # [{'m_fast': 10, 'm_slow': 20, 'm_signal': 30}, {'m_fast': 10, 'm_slow': 20, 'm_signal': 90}, ...] -> ==
            params_variations = source_params
        else:                                  # 1x params as list
            # [14, 30, 70] -> [[14, 30, 70]]
            params_variations = [source_params]
    elif isinstance(source_params, dict):      # 1x params as dict
        # {'m_fast': 14, 'm_slow': 30, 'm_signal': 70} -> [{'m_fast': 14, 'm_slow': 30, 'm_signal': 70}]
        params_variations = [source_params]
    elif source_params is None:            # 1x params default
        # None -> key 'default'
        params_variations = get_all_params_variations_from_yaml(indicator_name, 'default')
    else:
        raise ValueError(f'Wrong instance (not [str, list, None] of source_params: {source_params}')
    return params_variations


def get_params_from_yaml(indicator_name, key_variant):
    """ Return params defined in indicator_params.yaml
    :param indicator_name: dict[key]
    :param key_variant: dict[indicator_name][key]
    :return: dict of params
    """
    file_path = get_path('indicator_params_yaml')
    params_study_dict = load_yaml_from_file_path(file_path)

    if indicator_name not in params_study_dict:
        raise ValueError(f'key "{indicator_name}" not in {params_study_dict}')
    if key_variant not in params_study_dict[indicator_name]:
        raise ValueError(f'key "{key_variant}" not in {params_study_dict[indicator_name]}')
    if not params_study_dict[indicator_name][key_variant]:
        raise ValueError(f'{indicator_name}[{key_variant}] is None - define it in the yaml "indicator_params.yaml"')

    result = params_study_dict[indicator_name][key_variant]

    """
    There's a problem loading tuples from a YAML.
      Tuples are read from the yaml as strings and must be parsed as tuples here: '(2, 10, 1)' -> (2, 10, 1)
      Lists are transferred correctly from the yaml
    """
    for key, value in result.items():
        if isinstance(value, (list, tuple, int, float)):
            # no action - already a list item or a number
            continue
        else:
            # action needed - parse string to tuple
            try:
                result[key] = ast.literal_eval(value)
            except:
                raise ValueError(f'Wrong format (no list or tuple) for {indicator_name}[{key_variant}] - {key}: "{value}"')
    return result


def _set_param_variation(params_study: dict[str, list[float] | tuple[float, float, float]]) -> dict[str, list]:
    """ If present, converts a tuple (range) parameter set into a list.
    :param params_study: {key: [x,x,x], key: (start, end, step)}
    :return: dict all in format {key: [x,x,x]}

    [1, 5, 10, 15] -> [1, 5, 10, 15]
    (1, 10, 2)     -> [1, 3, 5, 7, 9]
    """
    for key, value in params_study.items():
        if isinstance(value, tuple) and len(value) == 3:
            start, end, step = float(value[0]), float(value[1]), float(value[2])
            params_study[key] = [round(start + i * step, 10) for i in range(int((end - start) / step) + 1)]

    return params_study


def get_all_params_variations_from_yaml(indicator_name, key_variant):
    """ Return list of all params variations
    :param indicator_name: dict[key]
    :param key_variant: dict[indicator_name][key]
    :return: list of all params variations

    Input: ('BB', 'visualize')
            visualize: {
              bb_l: [5, 6, 7]
              bb_std: [2.0, 2.5]
            }
    Output: [{'bb_l': 5, 'bb_std': 2.0}, {'bb_l': 5, 'bb_std': 2.5}, {'bb_l': 6, 'bb_std': 2.0}, {'bb_l': 6, 'bb_std': 2.5}, {'bb_l': 7, 'bb_std': 2.0}, {'bb_l': 7, 'bb_std': 2.5}]
    """
    # Get raw params and prepare it
    params = get_params_from_yaml(indicator_name, key_variant)
    params_study = _set_param_variation(params)
    # Make sure all elements are list elements
    for key, value in params_study.items():
        if isinstance(value, (int, float)):
            params_study[key] = [value]
    # Calculate all combinations
    keys = params_study.keys()
    values = params_study.values()
    combination = list(itertools.product(*values))
    combinations_list = [dict(zip(keys, combi)) for combi in combination]  # combination_list = [{self.params1}, {self.params2}, ... ]
    return combinations_list

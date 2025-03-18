import itertools
import ast

from modules.file_handler import get_path, load_yaml_from_file_path


def get_params_from_yaml(strategy_name, variant):
    """ Return params defined in indicator_params.yaml
    :param strategy_name: dict[key]
    :param variant: dict[strategy_name][key]
    :return: dict of params
    """
    file_path = get_path('indicator_params_yaml')
    params_study_dict = load_yaml_from_file_path(file_path)

    if strategy_name not in params_study_dict:
        raise ValueError(f'key "{strategy_name}" not in {params_study_dict}')
    if variant not in params_study_dict[strategy_name]:
        raise ValueError(f'key "{variant}" not in {params_study_dict[strategy_name]}')
    if not params_study_dict[strategy_name][variant]:
        raise ValueError(f'{strategy_name}[{variant}] is None - define it in the yaml "indicator_params.yaml"')

    result = params_study_dict[strategy_name][variant]

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
                raise ValueError(f'Wrong format (no list or tuple) for {strategy_name}[{variant}] - {key}: "{value}"')
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


def get_all_combinations_from_params_study(strategy_name, variant):
    """ Return list of all params variations
    :param strategy_name: dict[key]
    :param variant: dict[strategy_name][key]
    :return: list of all params variations

    Input: ('BB', 'visualize')
            bb_l: [5, 6, 7]
            bb_std: [2.0, 2.5]
    Output: [{'bb_l': 5, 'bb_std': 2.0}, {'bb_l': 5, 'bb_std': 2.5}, {'bb_l': 6, 'bb_std': 2.0}, {'bb_l': 6, 'bb_std': 2.5}, {'bb_l': 7, 'bb_std': 2.0}, {'bb_l': 7, 'bb_std': 2.5}]
    """
    # Get raw params and prepare it
    params = get_params_from_yaml(strategy_name, variant)
    params_study = _set_param_variation(params)
    # Calculate all combinations
    keys = params_study.keys()
    values = params_study.values()
    combination = list(itertools.product(*values))
    combinations_list = [dict(zip(keys, combi)) for combi in combination]  # combination_list = [{self.params1}, {self.params2}, ... ]
    return combinations_list

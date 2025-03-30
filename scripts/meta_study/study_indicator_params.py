import pandas as pd
import json

from modules.utils import json_dump_nicely
from modules.file_handler import get_path, create_dir, get_last_created_folder_in_dir, save_txt
from modules.meta_study.study_params import study_params_brute_force


def study_brute_force():
    indicator_names = ['MACD', 'BB', 'RSI']
    course_selection_keys = ['default']
    pre_test = True

    # Create result folder for the whole study
    folder_path = get_path('study') / f'Study_{pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    create_dir(folder_path)

    # Metadata and time estimation for the study
    file_path_meta_dict = folder_path / f'study_meta_dict.json'
    time_start = pd.Timestamp.now()
    meta_dict = {
        'meta': {
            'start': time_start.strftime('%Y/%m/%d %H:%M:%S'),
        },
        'study': {
            # fill dynamically
        }
    }

    # Pre test (estimate time, test for errors)
    if pre_test:
        for indicator_name in indicator_names:
            for course_selection_key in course_selection_keys:
                key, meta_sub_dict = study_params_brute_force(indicator_name, course_selection_key, True)
                meta_dict['study'][key] = meta_sub_dict

        meta_dict['meta']['time_estimated [h]'] = sum_time_estimated_from_dict(meta_dict)
        save_txt(json_dump_nicely(meta_dict), file_path_meta_dict)

    # Run study
    for indicator_name in indicator_names:
        for course_selection_key in course_selection_keys:
            key, meta_sub_dict = study_params_brute_force(indicator_name, course_selection_key, False)
            if key in meta_dict['study']:
                # There was a pre_test - update data
                meta_dict['study'][key].update(meta_sub_dict)
            else:
                # No pretest
                meta_dict['study'][key] = meta_sub_dict
    save_txt(json_dump_nicely(meta_dict), file_path_meta_dict)

    # Finish
    time_end = pd.Timestamp.now()
    meta_dict['meta']['time_real [h]'] = (time_end - time_start).total_seconds() / 3600
    meta_dict['meta']['end'] = time_end.strftime("%Y/%m/%d %H:%M:%S")
    save_txt(json_dump_nicely(meta_dict), file_path_meta_dict)



def sum_time_estimated_from_dict(meta_dict):
    estimated_time_total = 0
    for key in meta_dict['study'].keys():
        estimated_time = meta_dict['study'][key]['pre_study_estimation']['estimated_time [h]']
        estimated_time_total += estimated_time
    return estimated_time_total


if __name__ == "__main__":
    study_brute_force()
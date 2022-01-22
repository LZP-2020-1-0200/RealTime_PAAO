from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d

from RealTime_PAAO.common.constants import ALLOWED_REF_SPEKTRS_NAME, TXT_EXTENSION


def split_to_arrays(data, conversion=1):
    if data.shape[1] == 3:  # check if real or complex numbers are present
        return [data[:, 0] * conversion, data[:, 1] + np.complex(0, 1) * data[:, 2]]
    return [data[:, 0] * conversion, data[:, 1]]


def interpolate(x_data, y_data, new_x_data):
    return interp1d(x_data, y_data, kind='cubic')(new_x_data)


def get_spectra_paths(dict_of_name, number, starting_path):
    for key, value in dict_of_name.items():
        if number < key:
            current_file = value + str(number) + ".txt"
            next_file = value + str(number + 1) + ".txt" if number + 1 != key else value[:-1] + str(number + 1) + ".txt"
            return starting_path / current_file, starting_path / next_file


def construct_spectra_filenames_dict(name_of_first_spectrum):
    number_of_zeros = name_of_first_spectrum.count('0') - 1
    filename_start_letter = name_of_first_spectrum[:len(name_of_first_spectrum) - (number_of_zeros + 1)]

    list_of_strings = []
    list_of_keys = [10, 100, 1000, 10000, 100000, 1000000]
    dict_of_names = {}
    a = ""
    list_of_strings.append(a)
    for _ in range(0, number_of_zeros):
        a += "0"
        list_of_strings.append(a)

    list_of_ready_strings = [filename_start_letter + x for x in list_of_strings]

    for k, v in zip(list_of_keys, reversed(list_of_ready_strings)):
        dict_of_names[k] = v
    return dict_of_names


def get_anodizing_time(folder: Path) -> np.ndarray:
    time_history = []
    files = [file for file in folder.rglob(TXT_EXTENSION) if str(file.name) not in ALLOWED_REF_SPEKTRS_NAME]

    for file in files:
        modified_time = file.stat().st_mtime
        time_history.append(modified_time)

    time_history = np.diff(np.array(time_history))
    time_interval = np.insert(time_history, 0, 0., axis=0)
    # just in case
    if np.average(time_interval[:200]) < 0.1:
        time_interval = np.full(len(files), 0.25)
        time_interval[0] = 0
    return np.cumsum(time_interval)

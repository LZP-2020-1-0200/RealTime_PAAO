import numpy as np
import pandas as pd
import serial
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import shutil

def interpolate(x_data, y_data, new_x_data):
    return interp1d(x_data, y_data, kind='cubic')(new_x_data)


def split_to_arrays(data, conversion=1):
    if data.shape[1] == 3:
        return [data[:, 0] * conversion, data[:, 1] + np.complex(0, 1) * data[:, 2]]
    return [data[:, 0] * conversion, data[:, 1]]


# def connect_arduino(ports, description):
#     for port, desc, _ in ports:
#         if description in desc:
#             por = port
#             return serial.Serial(port=por, baudrate=9600, timeout=0.1)


def get_spectra_filenames(number):
    number_file = {10    : "R0000",
                   100   : "R000",
                   1000  : "R00",
                   10000 : "R0",
                   100000: "R"}
    for key, value in number_file.items():
        if number < key:
            current_file = value + str(number) + ".txt"
            next_file = value + str(number + 1) + ".txt" if number + 1 != key else value[:-1] + str(number + 1) + ".txt"
            return current_file, next_file


def get_spectra_filenames2(dict, number):
    for key, value in dict.items():
        if number < key:
            current_file = value + str(number) + ".txt"
            next_file = value + str(number + 1) + ".txt" if number + 1 != key else value[:-1] + str(number + 1) + ".txt"
            return current_file, next_file


def upgraded_get_spectra_filenames(number_of_zeros, leter_before_numbers):
    list_of_strings = []
    list_of_keys = [10, 100, 1000, 10000, 100000, 1000000]
    dict = {}
    a = ""
    list_of_strings.append(a)
    for i in range(0, number_of_zeros):
        a += "0"
        list_of_strings.append(a)

    list_of_ready_strings = [leter_before_numbers + k for k in list_of_strings]

    for k, v in zip(list_of_keys, reversed(list_of_ready_strings)):
        dict[k] = v
    # print(dict)
    return dict


def get_anodizing_time(folder):
    time_history = []
    files = [file for file in folder.rglob('*.txt') if file.name != 'ref_spektrs.txt']
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


def clear_fitting_figure(filename, thick, time):
    plt.clf()
    plt.xlim(480, 800)
    plt.ylim(0.75, 0.95)
    plt.yticks(np.arange(0.75, 0.90, 0.05))
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflection (a.u.)")
    plt.title("file={}  d={}  m={}  t={}".format(filename, *np.round(thick, 3), round(time, 3)))


def save_fitting_figure(x, y_real, y_fitted, path, filename):
    plt.plot(x, y_real, x, y_fitted)
    plt.grid()
    plt.savefig(path / (filename + '.png'))


def save_fitting_dat(x, y_real, y_fitted, path, filename):
    for_saving = pd.DataFrame({'Wavelength (nm)'  : x,
                               'Experimental data': y_real,
                               'Fitted data'      : y_fitted})
    for_saving.to_csv(path / (filename + '.dat'), sep='\t', index=False)


def save_anodizing_time_figure(voltage, thickness_hist, time, path):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(time, thickness_hist)
    ax2.plot(time, voltage, color='orange')

    ax1.set_xlabel("Time $(s)$")
    ax1.set_ylabel("Thickness $(nm)$")
    ax2.set_ylabel('Voltage $(V)$')
    ax2.set_ylim(-10, 50)

    ax1.grid()
    ax1.set_title("PAAO thickness dependence on anodization time")
    fig.savefig(path / 'Thickness_per_time.png')


def save_anodizing_time_dat(voltage, thickness_hist, time, path):
    thick_per_time = pd.DataFrame({'Time (s)'      : time[:len(thickness_hist)],
                                   'Thickness (nm)': thickness_hist,
                                   'Voltage (V)'   : voltage})
    thick_per_time.to_csv(path / 'Thickness_per_time.dat', sep='\t', index=False)


def get_real_data(current_file, reference_spectrum, lambda_range, R0):
    skip_lines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 3665, 3666]
    current_file_spectrum = pd.read_csv(current_file, delimiter='\t', skiprows=skip_lines,
                                        dtype=np.double, names=["Wavelength", "Intensity"])
    intensity_spectrum = interpolate(current_file_spectrum["Wavelength"], current_file_spectrum["Intensity"],
                                     lambda_range)

    return (intensity_spectrum / reference_spectrum) * R0


def get_reference_spectrum(path, lambda_range):
    reference_spectrum_from_file = np.genfromtxt(path, delimiter='\t', skip_header=17,
                                                 skip_footer=1, encoding='utf-8')
    reference_spectrum_data = split_to_arrays(reference_spectrum_from_file)
    return interpolate(*reference_spectrum_data, lambda_range)


def make_folder(path, folder_name):
    full_path = path / folder_name
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path


def copy_files(files, to_folder):
    for file in files:
        shutil.copy2(file, to_folder)


def move_file(old, new):
    for file in old:
        file.rename(new / file.name)

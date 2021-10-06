import enlighten
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d


def interpolate(x_data, y_data, new_x_data):
    return interp1d(x_data, y_data, kind='cubic')(new_x_data)


def split_to_arrays(data, conversion=1):
    if data.shape[1] == 3:
        return [data[:, 0] * conversion, data[:, 1] + np.complex(0, 1) * data[:, 2]]
    return [data[:, 0] * conversion, data[:, 1]]


def get_spectra_filename(i):
    number_file = {10    : "R0000",
                   100   : "R000",
                   1000  : "R00",
                   10000 : "R0",
                   100000: "R"}
    for key, value in number_file.items():
        if i < key:
            return value + str(i) + ".txt"


def save_plots(thickness_history, save_path, time_interval):
    real_data = np.load('real_data.npy')
    fitted_data = np.load('fitted_data.npy')
    time_fro_plot = np.round(np.arange(0, time_interval * 30000, time_interval),5)
    lambda_range = np.arange(480, 800 + 1)
    progress_bar = enlighten.Counter(total=len(fitted_data), desc='Saving', unit='plots')
    for i, (x, y, z) in enumerate(zip(real_data, fitted_data, thickness_history)):
        plt.clf()
        plt.plot(lambda_range, x, lambda_range, y)
        plt.xlim(480, 800)
        plt.ylim(0.75, 0.95)
        plt.yticks(np.arange(0.75, 0.90, 0.05))
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Reflection (a.u.)")
        spectra_filename = get_spectra_filename(i + 1)
        plt.title("file={}  d={}  m={}".format(spectra_filename, *z))
        plt.savefig(save_path / (spectra_filename[:-4] + '.png'))
        for_saving = pd.DataFrame({'Wavelength (nm)'  : lambda_range,
                                   'Experimental data': x,
                                   'Fitted data'      : y})
        for_saving.to_csv(save_path / (spectra_filename[:-4] + '.dat'), sep='\t', index=False)
        progress_bar.update()
    plt.clf()
    thickness_history_array = np.array(thickness_history)[:, 0]
    plt.plot(time_fro_plot[:len(thickness_history_array)], thickness_history_array)
    plt.xlabel("Time (s)")
    plt.ylabel("Thickness (nm)")
    plt.title("PAAO thickness dependence on anodization time")
    plt.savefig(save_path / ('Thickness_per_time.png'))
    anod_in_time = pd.DataFrame({'Time (s)'      : time_fro_plot[:len(thickness_history_array)],
                                 'Thickness (nm)': thickness_history_array})
    anod_in_time.to_csv(save_path / 'Thickness_per_time.dat', sep='\t', index=False)
    input('Finished!\nPress enter to exit\n')

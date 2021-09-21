import numpy as np
import pandas as pd
from time import perf_counter_ns
from pathlib import Path
from matplotlib import pyplot as plt
from scipy import optimize
from scipy.optimize import curve_fit
from functions import *
import serial
import time
from line_profiler_pycharm import profile
import functools

@profile
def multilayer(x: np.array, c: float, d: float):
    M_ = np.full((len(x), 2, 2), [[1, 0], [0, 1]])
    tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
    rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
    T = np.array([[np.ones(len(x)), rho], [rho, np.ones(len(x))]]) / tau
    M = M_ @ T.T
    k = ntilde[1] * 2 * np.pi / x
    P = np.array([[np.exp(j * k * c), np.zeros(len(x))], [np.zeros(len(x)), np.exp(-j * k * c)]])
    M = M @ P.T
    Ef = np.array([[np.ones(len(x))], [(ntilde[1] - ntilde[2]) / (ntilde[1] + ntilde[2])]]).T.reshape(len(x), 2, 1)
    E_0 = M @ Ef
    return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * d


if __name__ == '__main__':
    arduino = serial.Serial(port='COM3', baudrate=9600, timeout=0.1)
    arduino.write(bytes('2', 'utf-8'))
    arduino.write(bytes('3', 'utf-8'))

    # Starting variables
    lambda_start = 480
    lambda_end = 800
    lambda_range = np.arange(lambda_start, lambda_end + 1)
    time_interval = 0.28
    j = complex(0, 1)
    desirable_thickness = 253

    # Variables for paths
    path_to_refractive_info = Path("Refractive_info/")
    path_for_plots = Path("Plots/")
    path_to_files = Path("Anodesanas spektru dati/AJ-5-04-27 2nd anod/")

    # M. Daimon and A. Masumura. Measurement of the refractive index of distilled water from the near-infrared region
    # to the ultraviolet region, Appl. Opt. 46, 3811-3820 (2007)
    water_data = np.genfromtxt(path_to_refractive_info / "Water.txt", delimiter='\t')
    nk_water_from_data = split_to_arrays(water_data, 1e3)
    nk_water = interpolate(*nk_water_from_data, lambda_range)

    nk_al203 = np.full(len(nk_water), 1.65)

    # A. D. Rakić, A. B. Djurišic, J. M. Elazar, and M. L. Majewski. Optical properties of metallic films for
    # vertical-cavity optoelectronic devices, Appl. Opt. 37, 5271-5283 (1998)
    al_data = np.genfromtxt(path_to_refractive_info / "Rakic-BB.yml.txt", delimiter=' ', skip_header=9, skip_footer=3,
                            encoding='utf-8')
    nk_al_from_data = split_to_arrays(al_data, 1e3)
    nk_al = interpolate(*nk_al_from_data, lambda_range)

    # Array of arrays with all refractive indexes
    ntilde = np.array([nk_water, nk_al203, nk_al])
    # Zero thickness simulation
    R0 = multilayer(lambda_range, 0, 1)

    reference_spectrum_from_file = np.genfromtxt(path_to_files / "ref_spektrs.txt", delimiter='\t', skip_header=17,
                                                 skip_footer=1)
    reference_spectrum_data = split_to_arrays(reference_spectrum_from_file)
    reference_spectrum = interpolate(*reference_spectrum_data, lambda_range)

    fitted_values = [90, 1]
    real_data_history = []
    thickness_history = []
    skip_lines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 3665, 3666]

    i = 1
    time_Start = time.time()
    while fitted_values[0] < desirable_thickness:
        if i % 20 == 0:
            arduino.write(bytes('0', 'utf-8'))
        next_file = get_spectra_filename(i + 1)
        current_file = get_spectra_filename(i)
        if (path_to_files / next_file).is_file():
            spectrum_from_file = pd.read_csv(path_to_files / current_file, delimiter='\t', skiprows=skip_lines,
                                             dtype=np.double, names=["Wavelength", "Intensity"])
            intensity_spectrum = interpolate(spectrum_from_file["Wavelength"], spectrum_from_file["Intensity"],
                                             lambda_range)
            real_data = (intensity_spectrum / reference_spectrum) * R0
            real_data_history.append(real_data)
            fitted_values, pcov = curve_fit(multilayer, lambda_range, real_data, p0=fitted_values,
                                            bounds=((fitted_values[0], 0.9), (fitted_values[0] + 20, 1.1)))
            thickness_history.append(np.round(fitted_values, 3))
            if i % 20 == 0:
                arduino.write(bytes('3', 'utf-8'))
            i += 1
    time_end=time.time()
    print(((time_end-time_Start)/i)*1e3)

    # # Saving plots in disk after all data is collected
    # for counter, (data, values) in enumerate(zip(real_data_history, thickness_history)):
    #     plot_filename = get_spectra_filename(counter + 1)
    #     fitted_data = multilayer(lambda_range, *values)
    #     r_squared = calculate_r_squared(data, fitted_data)
    #     plot_data(lambda_range, data, fitted_data, plot_filename, values, r_squared)
    #     save_plot(path_for_plots, "{} d={:.2f} m={:.3f}.png".format(plot_filename[:-4], *values))

    arduino.write(bytes('1', 'utf-8'))
    thickness_history = np.array(thickness_history)
    anodizing_time = np.arange(0, time_interval * (i - 1), time_interval)

    plt.plot(anodizing_time, thickness_history[:, 0])
    plt.xlabel("Time (s)")
    plt.ylabel("Thickness (nm)")
    plt.title("PAAO thickness dependence on anodization time")
    save_plot(path_for_plots, "Thickness_per_time.png")

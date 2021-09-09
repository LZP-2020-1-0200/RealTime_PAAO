import glob
import os
import time
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy import stats
from functions import calculate_r_squared, get_filename, save_plot, interpolate, split_to_arrays


def multilayer(x: np.array, c: float, d: float):
    M_ = np.full((len(x), 2, 2), [[1, 0], [0, 1]])
    tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
    rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
    T = np.array([[np.ones(len(x)), rho], [rho, np.ones(len(x))]]) / tau
    M = M_ @ T.T
    k = ntilde[1] * 2 * np.pi / x
    P = np.array([[np.exp(j * k * c), np.zeros(len(x))], [np.zeros(len(x)), np.exp(-j * k * c)]])
    M = M @ P.T
    hey = (ntilde[1] - ntilde[2]) / (ntilde[1] + ntilde[2])
    Ef = np.array([[np.ones(len(x))], [hey]]).T.reshape(lambda_size, 2, 1)
    E_0 = M @ Ef
    return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * d


if __name__ == '__main__':
    j = complex(0, 1)
    lambda_min, lambda_max = 480, 800
    lambda_range = np.arange(lambda_min, lambda_max + 1)
    lambda_size = len(lambda_range)
    time_interval = 0.8

    # paths
    path_to_refractive_info = "C:\\Users\\Vladislavs\\PycharmProjects\\RealTime_PAAO\\Refractive_info\\"
    path_to_save = "S:\\Plots\\"
    path_to_files = 'C:\\Users\\Vladislavs\\Desktop\\Anodesanas spektru dati\\2 aleksandra paraugs\\'

    # M. Daimon and A. Masumura. Measurement of the refractive index of distilled water from the near-infrared region
    # to the ultraviolet region, Appl. Opt. 46, 3811-3820 (2007)
    water_data = np.genfromtxt(path_to_refractive_info + "Water.txt", delimiter='\t')
    nk_water_from_data = split_to_arrays(water_data, 1e3)
    nk_water = interpolate(*nk_water_from_data, lambda_range)

    nk_al203 = np.full(len(nk_water), 1.65)

    # A. D. Rakić, A. B. Djurišic, J. M. Elazar, and M. L. Majewski. Optical properties of metallic films for
    # vertical-cavity optoelectronic devices, Appl. Opt. 37, 5271-5283 (1998)
    al_data = np.genfromtxt(path_to_refractive_info + "Rakic-BB.yml.txt", delimiter=' ', skip_header=9, skip_footer=3)
    nk_al_from_data = split_to_arrays(al_data, 1e3)
    nk_al = interpolate(*nk_al_from_data, lambda_range)

    # Array of arrays with all refractive indexes
    ntilde = np.array([nk_water, nk_al203, nk_al])
    # Zero thickness simulation
    R0 = multilayer(lambda_range, 0, 1)

    reference_spectrum_from_file = np.genfromtxt(path_to_files + "ref_spektrs.txt", delimiter='\t', skip_header=17,
                                                 skip_footer=1)
    reference_spectrum_data = split_to_arrays(reference_spectrum_from_file)
    reference_spectrum = interpolate(*reference_spectrum_data, lambda_range)
    
    fitted_values = [80, 1]
    i = 1
    while fitted_values[0] < 150:
        next_file = get_filename(i + 1)
        current_file = get_filename(i)
        if os.path.exists(path_to_files + next_file):
            i += 1
            spectrum_data_from_file = np.genfromtxt(path_to_files + get_filename(i), delimiter='\t', skip_header=17,
                                                    skip_footer=1)
            intensity_spectrum = interpolate(reference_spectrum_data[0], spectrum_data_from_file[:, 1], lambda_range)
            real_data = (intensity_spectrum / reference_spectrum * R0)
            fitted_values, pcov = curve_fit(multilayer, lambda_range, real_data, p0=fitted_values,
                                            bounds=((fitted_values[0], 0.9), (fitted_values[0] + 10, 1.1)))
            fitted_data = multilayer(lambda_range, *fitted_values)
            r_squares = calculate_r_squared(real_data, fitted_data)
            save_plot(lambda_range, real_data, fitted_data, path_to_save, fitted_values, i)
        else:
            time.sleep(time_interval / 10)
            print("waiting...")

import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d


def interpolate(x_data, y_data, new_x_data):
    data = interp1d(x_data, y_data, kind='cubic')
    return np.round(data(new_x_data), 2)


# function to get info from txt file
def get_txt_data(file, lambda_range, reference_lambda=None, skip_header=0, skip_footer=0):
    # read txt file, skipping headers and footers if needed (for spectra files)
    data = np.genfromtxt(file, skip_header=skip_header, skip_footer=skip_footer)
    # first column is for wavelengths
    data_lambda = data[:, 0]
    # for refractive info data files from qm to nm
    if file == "ref_spektrs.txt" or skip_header == 0:
        data_lambda = data[:, 0] * 1e3
    # second column is for y axis
    nk_data = data[:, 1]
    # if there is more than 3 columns, then y is imaginary
    if data.shape[1] == 3:
        nk_data = data[:, 1] + np.complex(0, 1) * data[:, 2]
    if reference_lambda is not None:
        data_lambda = reference_lambda
    # get the range we need
    nk_data = interpolate(data_lambda, nk_data, lambda_range)
    # return the data
    return data_lambda, nk_data


# function to calculate R^2
def calculate_r_squared(real_data, predicted_data):
    return np.corrcoef(real_data, predicted_data)[0, 1] ** 2


# def get_spectrum_txt(file, lambda_range, reference_lambda, zero_thickness):
#     intensity_spectrum = get_txt_data(file, lambda_range, reference_lambda, skip_header=17, skip_footer=1)
#     print(reference_lambda)
#     return intensity_spectrum[1] / reference_lambda * zero_thickness
def save_plot(x_data,y_real,y_predicted,path,predictions,counter):
    plt.plot(x_data, y_real, x_data, y_predicted)
    plt.xlim(x_data[0], x_data[-1])
    plt.ylim(0.75, 0.95)
    plt.yticks(np.arange(0.75, 0.90, 0.05))
    plt.title("{} d={:.3f} m={:.3f}".format(("plot"+str(counter)), *predictions))
    plt.savefig(path + "plot{} d={:.3f} m={:.3f}.png".format(counter, *predictions))
    plt.clf()


def get_r_spectrum(file, lambda_reference, lambda_range, reference_intensity, zero_thickness):
    spectrum0 = np.genfromtxt(file, delimiter='\t', skip_header=17, skip_footer=1)
    intensity_spectrum = interpolate(lambda_reference, spectrum0[:, 1], lambda_range)
    return (intensity_spectrum / reference_intensity) * zero_thickness


def get_filename(i):
    a = {10: "R0000", 100: "R000", 1000: "R00", 10000: "R0", 100000: "R"}
    for key, value in a.items():
        if i < key:
            return value + str(i) + ".txt"

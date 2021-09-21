import numpy as np
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt


def interpolate(x_data, y_data, new_x_data):
    return interp1d(x_data, y_data, kind='cubic')(new_x_data)


def split_to_arrays(data, conversion=1):
    if data.shape[1] == 3:
        return [data[:, 0] * conversion, data[:, 1] + np.complex(0, 1) * data[:, 2]]
    return [data[:, 0] * conversion, data[:, 1]]


# function to calculate R^2
# def calculate_r_squared(real_data, predicted_data):
#     return np.mean(predicted_data-real_data)
#     # return np.corrcoef(real_data, predicted_data)[0, 1] ** 2


def plot_data(x_data, y_real, y_predicted, filename, predictions):
    plt.clf()
    plt.plot(x_data, y_real, x_data, y_predicted)
    plt.xlim(x_data[0], x_data[-1])
    plt.ylim(0.75, 0.95)
    plt.yticks(np.arange(0.75, 0.90, 0.05))
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflection (a.u.)")
    plt.title("file={}  d={:.2f}  m={:.3f}".format(
        filename, *predictions))


# def save_plot(path, title):
#     plt.savefig(path / title)



def get_spectra_filename(i):
    number_file = {10: "R0000", 100: "R000",
                   1000: "R00", 10000: "R0", 100000: "R"}
    for key, value in number_file.items():
        if i < key:
            return value + str(i) + ".txt"

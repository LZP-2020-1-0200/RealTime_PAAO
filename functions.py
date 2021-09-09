import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d


def interpolate(x_data, y_data, new_x_data):
    return interp1d(x_data, y_data, kind='cubic')(new_x_data)


def split_to_arrays(data, conversion=1):
    if data.shape[1] == 3:
        return [data[:, 0] * conversion, data[:, 1] + np.complex(0, 1) * data[:, 2]]
    return [data[:, 0] * conversion, data[:, 1]]


# function to calculate R^2
def calculate_r_squared(real_data, predicted_data):
    return np.corrcoef(real_data, predicted_data)[0, 1] ** 2


def save_plot(x_data, y_real, y_predicted, path, predictions, counter):
    plt.plot(x_data, y_real, x_data, y_predicted)
    plt.xlim(x_data[0], x_data[-1])
    plt.ylim(0.75, 0.95)
    plt.yticks(np.arange(0.75, 0.90, 0.05))
    plt.title("{} d={:.3f} m={:.3f}".format(("plot" + str(counter)), *predictions))
    plt.savefig(path + "plot{} d={:.3f} m={:.3f}.png".format(counter, *predictions))
    plt.clf()


def get_filename(i):
    a = {10: "R0000", 100: "R000", 1000: "R00", 10000: "R0", 100000: "R"}
    for key, value in a.items():
        if i < key:
            return value + str(i) + ".txt"

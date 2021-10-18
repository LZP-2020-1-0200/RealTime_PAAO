from pathlib import Path

import numpy as np

from functions import interpolate
from ntilde import create_ntilde, get_al203_data, get_al_data_from_file, get_water_data_from_file


def multilayer(x, thickness, normalization):
    P = np.array([[np.exp(complex(0, 1) * k * thickness), np.zeros(len(x))],
                  [np.zeros(len(x)), np.exp(-complex(0, 1) * k * thickness)]])
    S = M @ P.T
    Ef = np.array([[np.ones(len(x))], [(ntilde[1] - ntilde[2]) /
                                       (ntilde[1] + ntilde[2])]]).T.reshape(len(x), 2, 1)
    E_0 = S @ Ef
    return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * normalization


LAMBDA_RANGE = np.arange(480, 800 + 1)

path_to_refractive_info = Path("Refractive_info/")
nk_water = interpolate(*get_water_data_from_file(path_to_refractive_info, 1e3), LAMBDA_RANGE)
nk_al2o3 = get_al203_data(len(nk_water))
nk_al = interpolate(*get_al_data_from_file(path_to_refractive_info, 1e3), LAMBDA_RANGE)
ntilde = create_ntilde(nk_water, nk_al2o3, nk_al)

M_ = np.full((len(LAMBDA_RANGE), 2, 2), [[1, 0], [0, 1]])
tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
T = np.array([[np.ones(len(LAMBDA_RANGE)), rho], [rho, np.ones(len(LAMBDA_RANGE))]]) / tau
M = M_ @ T.T
k = ntilde[1] * 2 * np.pi / LAMBDA_RANGE

R0 = multilayer(LAMBDA_RANGE, 0, 1)

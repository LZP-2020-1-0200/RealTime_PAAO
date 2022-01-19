import numpy as np

from RealTime_PAOO.common.constants import INTERCEPT, LAMBDA, SLOPE
from RealTime_PAOO.multilayer.ntilde import ntilde


def theoretical_thickness(anod_time):
    return anod_time * SLOPE + INTERCEPT


def multilayer(x, thickness, normalization):
    P = np.array([[np.exp(complex(0, 1) * k * thickness), np.zeros(len(x))],
                  [np.zeros(len(x)), np.exp(-complex(0, 1) * k * thickness)]])
    S = M @ P.T
    Ef = np.array([[np.ones(len(x))], [(ntilde[1] - ntilde[2]) /
                                       (ntilde[1] + ntilde[2])]]).T.reshape(len(x), 2, 1)
    E_0 = S @ Ef
    return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * normalization


M_ = np.full((len(LAMBDA), 2, 2), [[1, 0], [0, 1]])
tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
T = np.array([[np.ones(len(LAMBDA)), rho], [rho, np.ones(len(LAMBDA))]]) / tau
M = M_ @ T.T
k = ntilde[1] * 2 * np.pi / LAMBDA

R0 = multilayer(LAMBDA, 0, 1)

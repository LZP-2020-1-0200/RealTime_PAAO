import numpy as np
from RealTime_PAAO.common.constants import INTERCEPT, LAMBDA, SLOPE
from RealTime_PAAO.multilayer.ntilde import nk


def theoretical_thickness(anod_time):
    return anod_time * SLOPE + INTERCEPT


def multilayer(wavelength, thickness, normalization):
    P = np.array([[np.exp(complex(0, 1) * k * thickness), np.zeros(len(wavelength))],
                  [np.zeros(len(wavelength)), np.exp(-complex(0, 1) * k * thickness)]])
    S = M @ P.T
    Ef = np.array([[np.ones(len(wavelength))], [(nk[1] - nk[2]) /
                                                (nk[1] + nk[2])]]).T.reshape(len(wavelength), 2, 1)
    E_0 = S @ Ef
    return (abs(E_0[0:len(wavelength), 1] / E_0[0:len(wavelength), 0]) ** 2)[:, 0] * normalization


tau = 2 * nk[0] / (nk[0] + nk[1])
rho = (nk[0] - nk[1]) / (nk[0] + nk[1])
T = np.array([[np.ones(len(LAMBDA)), rho], [
    rho, np.ones(len(LAMBDA))]]) / tau
M = np.full((len(LAMBDA), 2, 2), [[1, 0], [0, 1]]) @ T.T
k = nk[1] * 2 * np.pi / LAMBDA

R0 = multilayer(LAMBDA, 0, 1)

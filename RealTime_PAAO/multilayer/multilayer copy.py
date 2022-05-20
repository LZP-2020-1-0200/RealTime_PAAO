import sys
sys.path.append(r"C:\Users\Vladislavs\PycharmProjects\RealTime_PAAO")
import ctypes

import cmath
import math

from RealTime_PAAO.common.constants import INTERCEPT, LAMBDA, SLOPE
from RealTime_PAAO.multilayer.ntilde import nk, nk_water,nk_al,nk_al2o3


def theoretical_thickness(anod_time):
    return anod_time * SLOPE + INTERCEPT


# 3. parnesta no octaves tīrs python

def mat_mul(mat_a, mat_b):
    iterable_b = list(zip(*mat_b))
    return [[sum(a * b for a, b in zip(row_a, col_b)) for col_b in iterable_b] for row_a in mat_a]

nk = [list(nk_water), list(nk_al2o3), list(nk_al2o3)]

def multilayer(wavelength, thickness, normalization):
    R = []
    for a in range(len(wavelength)):
    # for a in range(2):
        nk = [complex(nk_water[a], 0), complex(nk_al2o3[a], 0), nk_al[a]]
        tau = 2 * nk[0] / (nk[0] + nk[1])
        rho = (nk[0] - nk[1]) / (nk[0] + nk[1])
        T = [[1 / tau, rho / tau], [rho / tau, 1 / tau]]
        M = mat_mul([[1, 0], [0, 1]], T)
        k = nk[1] * 2 * math.pi / wavelength[a]
        P = [[cmath.exp(complex(0, 1) * k * thickness), 0],
             [0, cmath.exp(-complex(0, 1) * k * thickness)]]
        M = mat_mul(M, P)
        Ef = [[1],
              [((nk[1] - nk[2]) / (nk[1] + nk[2]))]]
        E0 = mat_mul(M, Ef)
        E0 = [E0[0][0], E0[1][0]]
        R_calculated = abs(E0[1] / E0[0]) ** 2 * normalization
        R.append(R_calculated)
    return R

R0 = multilayer(LAMBDA, 0, 1)
print(R0)
# 4. Izmantojot Numpy
# import numpy as np
#
#
# def multilayer(wavelength, thickness, normalization):
#     R = np.zeros(len(wavelength))
#     for a in np.arange(len(wavelength)):
#         nk = np.array([nk_water[a], nk_al2o3[a], nk_al[a]])
#         tau = 2 * nk[0] / (nk[0] + nk[1])
#         rho = (nk[0] - nk[1]) / (nk[0] + nk[1])
#         T = np.array([[1, rho], [rho, 1]]) / tau
#         M = np.array([[1, 0], [0, 1]]) @ T
#         k = nk[1] * 2 * np.pi / wavelength[a]
#         P = np.array([[np.exp(complex(0, 1) * k * thickness), 0],
#                       [0, np.exp(-complex(0, 1) * k * thickness)]])
#         M = M @ P
#         Ef = np.array([[1],
#                        [(nk[1] - nk[2]) / (nk[1] + nk[2])]])
#         E_0 = M @ Ef
#         R[a] = (abs(E_0[1] / E_0[0])) ** 2 * normalization
#     return R

# 5. numpy + vektorizācija
# import numpy as np
# def multilayer(x, thickness, normalization):
#     M_ = np.full((len(LAMBDA), 2, 2), [[1, 0], [0, 1]])
#     tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
#     rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
#     T = np.array([[np.ones(len(LAMBDA)), rho], [rho, np.ones(len(LAMBDA))]]) / tau
#     M = M_ @ T.T
#     k = ntilde[1] * 2 * np.pi / LAMBDA
#     P = np.array([[np.exp(complex(0, 1) * k * thickness), np.zeros(len(x))],
#                   [np.zeros(len(x)), np.exp(-complex(0, 1) * k * thickness)]])
#     S = M @ P.T
#     Ef = np.array([[np.ones(len(x))], [(ntilde[1] - ntilde[2]) /
#                                        (ntilde[1] + ntilde[2])]]).T.reshape(len(x), 2, 1)
#     E_0 = S @ Ef
#     return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * normalization

# 6. numba
# import numpy as np
# from numba import njit
# #
# @njit(cache=True)
# def mat_mul(a,b):
#     c = []
#     for i in range(len(a)):
#         temp=[]
#         for j in range(len(b[0])):
#             s = 0
#             for k in range(len(a[0])):
#                 s += a[i][k]*b[k][j]
#             temp.append(s)
#         c.append(temp)
#     return c
#
#
# @njit(cache=True)
# def multilayer_helper(wavelength, thickness, normalization):
#     R = np.zeros(len(wavelength))
#     for a in range(len(wavelength)):
#         nk = np.array([nk_water[a], nk_al2o3[a], nk_al[a]])
#         tau = 2 * nk[0] / (nk[0] + nk[1])
#         rho = (nk[0] - nk[1]) / (nk[0] + nk[1])
#         T = np.array([[1, rho], [rho, 1]]) / tau
#         M = mat_mul(np.array([[1, 0], [0, 1]]) , T)
#         k = nk[1] * 2 * np.pi / wavelength[a]
#         P = np.array([[np.exp(complex(0, 1) * k * thickness), 0],
#                        [0, np.exp(-complex(0, 1) * k * thickness)]])
#         M = mat_mul(M , P)
#         temp = (nk[1] - nk[2]) / (nk[1] + nk[2])
#         Ef = np.array([[complex(1,0)], [temp]])
#         E0 = mat_mul(M , Ef)
#         E0 = [E0[0][0], E0[1][0]]
#         b = (abs(E0[1] / E0[0])) ** 2 * normalization
#         # print(a* normalization)
#         R[a] = b #(abs(E0[1] / E0[0])) ** 2 * normalization
#     return R
#
# def multilayer(wavelength, thickness, normalization):
#     return multilayer_helper(wavelength, thickness, normalization)
#
# print(np.matmul([[2,2],[2,2]] , [[1],[2]]))

# -----------------------------------------------------------

# 7. cython
from cython_multilayer import multilayer

R0 = multilayer(LAMBDA, 0, 1)
print(R0)

# 8 ctypes
# libObject = ctypes.CDLL("C:\\Users\\Vladislavs\\PycharmProjects\\RealTime_PAAO\\RealTime_PAAO\\multi.so", winmode=0)
# multilayer_ = libObject.multilayer
# multilayer_.argtypes = (ctypes.c_double * 321, ctypes.c_double * 321,
#                         (ctypes.c_double) * 321, (ctypes.c_double) * 321,
#                         (ctypes.c_double) * 321, (ctypes.c_double) * 321,
#                         (ctypes.c_double) * 321, (ctypes.c_double) * 321,
#                         ctypes.c_double, ctypes.c_double)
#
# multilayer_.restype = None
#
# zero_list = [0 for x in range(321)]
# n_water = [x.real for x in nk_water]
# k_water = [x.imag for x in nk_water]
# n_al203 = [x.real for x in nk_al2o3]
# k_al203 = [x.imag for x in nk_al2o3]
# n_al = [x.real for x in nk_al]
# k_al = [x.imag for x in nk_al]
# lambda_ = [x for x in LAMBDA]
#
# R = (ctypes.c_double * len(zero_list))(*zero_list)
# n_water_c_ = (ctypes.c_double * len(n_water))(*n_water)
# k_water_c_ = (ctypes.c_double * len(k_water))(*k_water)
#
# n_al203_c_ = (ctypes.c_double * len(n_al203))(*n_al203)
# k_al203_c = (ctypes.c_double * len(k_al203))(*k_al203)
#
# n_al_c_ = (ctypes.c_double * len(n_al))(*n_al)
# k_al_c_ = (ctypes.c_double * len(k_al))(*k_al)
#
# lambda_c = (ctypes.c_double * len(lambda_))(*lambda_)


# print(n_water)


# result = [R[x] for x in range(321)]

# def multilayer(wavelength, thickness, normalization):
#     lambda_ = [x for x in wavelength]
#     lambda_c = (ctypes.c_double * len(lambda_))(*lambda_)
#     zero_list = [0 for x in range(321)]
#     R = (ctypes.c_double * len(zero_list))(*zero_list)
#     multilayer_(n_water_c_, k_water_c_, n_al203_c_, k_al203_c, n_al_c_, k_al_c_, R, lambda_c, thickness, normalization)
#     return [R[x] for x in range(321)]


# print(multilayer_)
R0 = multilayer(LAMBDA, 0, 1)
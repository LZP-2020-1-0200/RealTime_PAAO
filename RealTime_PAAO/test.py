import sys

sys.path.append("C:\\Users\\Vladislavs\\PycharmProjects\\RealTime_PAAO\\")
import ctypes
import pathlib
from numpy.ctypeslib import ndpointer
from scipy.optimize import curve_fit
from time import time
import numpy as np
from numpy import ctypeslib

from RealTime_PAAO.common.constants import INTERCEPT, LAMBDA, SLOPE
from RealTime_PAAO.multilayer.ntilde import nk, nk_water, nk_al, nk_al2o3

# print(nk_water[:2], nk_al[:2], nk_al2o3[:2], LAMBDA[:2])

libObject = ctypes.CDLL("C:\\Users\\Vladislavs\\PycharmProjects\\RealTime_PAAO\\RealTime_PAAO\\multi.so", winmode=0)
multilayer_ = libObject.multilayer
multilayer_.argtypes = (ctypes.c_double * 321, ctypes.c_double * 321,
                        (ctypes.c_double) * 321, (ctypes.c_double) * 321,
                        (ctypes.c_double) * 321, (ctypes.c_double) * 321,
                        (ctypes.c_double) * 321, (ctypes.c_double) * 321,
                        ctypes.c_double, ctypes.c_double)

multilayer_.restype = None

zero_list = [0 for x in range(321)]
n_water = [x.real for x in nk_water]
k_water = [x.imag for x in nk_water]
n_al203 = [x.real for x in nk_al2o3]
k_al203 = [x.imag for x in nk_al2o3]
n_al = [x.real for x in nk_al]
k_al = [x.imag for x in nk_al]
lambda_ = [x for x in LAMBDA]

R = (ctypes.c_double * len(zero_list))(*zero_list)
n_water_c_ = (ctypes.c_double * len(n_water))(*n_water)
k_water_c_ = (ctypes.c_double * len(k_water))(*k_water)

n_al203_c_ = (ctypes.c_double * len(n_al203))(*n_al203)
k_al203_c = (ctypes.c_double * len(k_al203))(*k_al203)

n_al_c_ = (ctypes.c_double * len(n_al))(*n_al)
k_al_c_ = (ctypes.c_double * len(k_al))(*k_al)

lambda_c = (ctypes.c_double * len(lambda_))(*lambda_)


# print(n_water)


# result = [R[x] for x in range(321)]

def multilayer():
    multilayer_(n_water_c_, k_water_c_, n_al203_c_, k_al203_c, n_al_c_, k_al_c_, R, lambda_c, 0.0, 1.0)
    return [R[x] for x in range(321)]


print(multilayer_)

# print(r)

# addTwoNumbers = libObject.cmult
# addTwoNumbers.argtypes = [ctypes.POINTER(ctypes.c_int),ctypes.c_double]
# addTwoNumbers.restype = ctypes.POINTER(ctypes.c_double)

# X = [1,2,3,4]
# Y = [1,2,3,4]

# scribbled_Y = [0.5,1,1.5,2]

# def hujna(x,a):
#     # 
#     b = []
#     x = [int(x_) for x_ in x]
#     arr_c = (ctypes.c_int * 4)(*x)
#     print(x,a)
#     result = addTwoNumbers(arr_c,a)
#     for k in range(0,4):
#         b.append(result[k])

#     # print(b,a)

#     return  b


# def tas_pats_python (x,guess):
#     a = [0,0,0,0]
#     for i in range(0,4):
#         a[i] = x[i]*guess/0.6543+76

#     return a


#     # float * cmult(float int_param[4],float guess) {
#     # static float a[4];

#     # for (int i = 0; i < 4; i++) {
#     #     a[i] = int_param[i] * guess;
#     # }
#     # return  a;


# if __name__ == "__main__":

#     # print(hujna([1,2,3,4],3))

#     # print(tas_pats_python([1,2,3,4],3))

#     # # print(hujna([1,2,3,4],2)[0])
#     # # Load the shared library into ctypes


#     # # arr_c = (ctypes.c_float * 4)(*[1,2,3,4])


#     # # print(hujna([1,2,3,4],3,addTwoNumbers)[0])

#     start = time()
#     a,b = curve_fit(hujna,X,scribbled_Y,p0=[-3])
#     end = time()

#     print(f"c++ time = {(end-start)*1000} ms" )

#     start = time()
#     a,b = curve_fit(tas_pats_python,X,scribbled_Y,p0=[-3])
#     end = time()

#     print(f"python time = {(end-start)*1000} ms" )
#     # print("anser is: ", a) 


#     # print(arr_c)

#     # kekw = addTwoNumbers(arr_c,ctypes.c_int(5))
#     # print(kekw[0],kekw[1],kekw[2],kekw[3])

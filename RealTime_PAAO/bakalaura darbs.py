from scipy.optimize import curve_fit

from RealTime_PAAO.common.constants import LAMBDA
from RealTime_PAAO.common.shared import reference_spectrum
from RealTime_PAAO.multilayer.multilayer import multilayer, R0, theoretical_thickness
import matplotlib.pyplot as plt
import numpy as np
from RealTime_PAAO.data.read import get_real_data, get_reference_spectrum

# thickness = 300
#
#
reference_spectrum = get_reference_spectrum('C:\\Users\\Vladislavs\\PycharmProjects\\RealTime_PAAO\\RealTime_PAAO'
                                            '\\ref_spektrs.txt')
real_data = get_real_data('C:\\Users\\Vladislavs\\PycharmProjects\\RealTime_PAAO\\RealTime_PAAO\\R00611.txt',
                          reference_spectrum,R0)
for thickness in range(150,351,50):
    fitted_parameters, _ = curve_fit(multilayer, LAMBDA, real_data, p0=(thickness, 1))
    # print(thickness)
    # a = multilayer(LAMBDA, thickness, 1)

    x_axis = 'Viļņa garums, nm'
    y_axis = 'Atstarošanas koeficents, a.u.'
    legend = ['Eksperimentāli iegūtais spektrs',f'Teorētiskais spektrs PAAO biezums {fitted_parameters[0]:.0f} nm']

    plt.plot(LAMBDA, real_data, LAMBDA, multilayer(LAMBDA, *fitted_parameters))
    # plt.show()
    # plt.plot(LAMBDA, a)

    plt.yticks(np.arange(0.75, 0.96, 0.05))
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.legend(legend)

    plt.savefig(f"C:\\Users\\Vladislavs\\Desktop\\{thickness}nm_plot.png")
    plt.cla()




print(fitted_parameters)


import glob
import os
import time
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy import stats
from data_loading import get_txt_data
from data_loading import calculate_r_squared
from data_loading import get_r_spectrum, get_filename, save_plot

# from sklearn.metrics import mean_squared_error
# from line_profiler_pycharm import profile


# def multilay(nm: np.array, p1: np.array):
#     R = np.zeros(len(nm))
#     l = np.array([p1]) * 1e-9
#     lambda_0 = nm * 1e-9
#     # print(lambda_0)
#     L = len(lambda_0)
#     for a in range(L):
#         # n = ntilde[:, 0][:, a]
#         n = np.array([n0[a], nal203[a], nkal[a]])
#         M = np.array([[1, 0], [0, 1]])
#         for m in range(1):
#             tau = 2 * n[m] / (n[m] + n[m + 1])
#             rho = (n[m] - n[m + 1]) / (n[m] + n[m + 1])
#             T = np.array([[1, rho], [rho, 1]]) / tau
#
#             M = np.matmul(M, T)
#             k = n[m + 1] * 2 * np.pi / lambda_0[a]
#             P = np.array([[np.exp(j * k * l[m]), 0],
#                           [0, np.exp(-j * k * l[m])]])
#             M = np.matmul(M, P)
#         Ef = np.array([[1], [(n[m + 1] - n[m + 2]) /
#                              (n[m + 1] + n[m + 2])]])
#         E_0 = np.matmul(M, Ef)
#         R[a] = (abs(E_0[1] / E_0[0])) ** 2
#     # print(Ef)
#     return R

np.set_printoptions(threshold=40)


##

def new_multilay(x: np.array, c: float, d: float):
    M_ = np.full((len(x), 2, 2), [[1, 0], [0, 1]])
    tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
    rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
    T = np.array([[np.ones(len(x)), rho],
                  [rho, np.ones(len(x))]]) / tau
    M = M_ @ T.T
    k = ntilde[1] * 2 * np.pi / x
    P = np.array([[np.exp(j * k * c), np.zeros(len(x))],
                  [np.zeros(len(x)), np.exp(-j * k * c)]])
    M = M @ P.T

    hey = (ntilde[1] - ntilde[2]) / (ntilde[1] + ntilde[2])
    Ef = np.array([[np.ones(len(x))],
                   [hey]]).T.reshape(lambda_size, 2, 1)
    E_0 = M @ Ef
    return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * d


if __name__ == '__main__':
    j = complex(0, 1)
    lambda_min, lambda_max = 480, 800
    lambda_range = np.arange(lambda_min, lambda_max + 1)
    lambda_size = len(lambda_range)
    # os.chdir("C:\\Users\\Vladislavs\\PycharmProjects\\test_leastsquares\\Teksta dati2")
    # file_names = glob.glob('*.txt')
    # number_files = len(file_names)
    time_interval = 0.8

    # Load reference file
    reference_intensity = get_txt_data("C:\\Users\\Vladislavs\\PycharmProjects\\test_leastsquares\\"
                                       "Teksta dati2\\ref_spektrs.txt", lambda_range, skip_header=17,
                                       skip_footer=1)
    # Loading H20 complex refractive index
    nk_water = get_txt_data("C:\\Users\\Vladislavs\\PycharmProjects\\Real_Time_Thickness\\"
                            "Refractive_info\\water_new.txt", lambda_range)

    # Loading Aluminium Oxide complex refractive index
    nk_al203 = get_txt_data("C:\\Users\\Vladislavs\\PycharmProjects\\Real_Time_Thickness\\Refractive_info\\"
                            "al2036.txt", lambda_range)

    nk_al203 = np.full(len(nk_water[1]), 1.65)

    # Loading Aluminium complex refractive index
    nk_al = get_txt_data("C:\\Users\\Vladislavs\\PycharmProjects\\Real_Time_Thickness\\Refractive_info\\"
                         "ALRAKIC_VECIE.txt", lambda_range)
    # Array of arrays with all refractive indexes
    ntilde = np.array([nk_water[1], nk_al203, nk_al[1]])
    # Zero thickness simulation
    R0 = new_multilay(lambda_range, 0.000001, 1)

    # guess = [60, 1]
    # R_spectrum = get_r_spectrum('C:\\Users\\Vladislavs\\PycharmProjects\\test_leastsquares\\Teksta dati\\'
    #                             + get_filename(1), reference_intensity[0], lambda_range, reference_intensity[1], R0)
    #
    # popt, pcov = curve_fit(new_multilay, lambda_range, R_spectrum, p0=guess, bounds=((guess[0], 0.9), (600, 1.1)))
    # guess = popt
    # print(popt, R_spectrum, new_multilay(lambda_range, *popt))

    # plt.plot(lambda_range, R_spektrs, 'y--')
    # plt.legend(["new method", "old"])
    # plt.xlim(480, 800)
    # plt.ylim(0.75, 0.95)
    # plt.yticks(np.arange(0.75, 0.95, 0.05))
    # plt.show()

    ## the process

    # popt,pcov = curve_fit(new_multilay,lambda_range,R0,p0=[470,0.5])
    # plt.plot(lambda_range,R0,lambda_range,new_multilay(lambda_range,*popt),'y--')
    # plt.show()
    # print(popt)
    # corr_matrix = np.corrcoef(R0,new_multilay(lambda_range,*popt))
    # corr = corr_matrix[0,1]
    # R_sq = corr**2

    # print(R_sq,calculate_r_squared(R0,new_multilay(lambda_range,*popt)))
    path_to_save = "S:\\Plots\\"
    path_to_files = 'C:\\Users\\Vladislavs\\PycharmProjects\\test_leastsquares\\Teksta dati2\\'
    i = 0
    error = []
    plot_filename = "plot"
    fitted_values = [80, 1]
    while fitted_values[0] < 210:
        i += 1
        try:
            file = get_filename(i)
            real_data = get_r_spectrum(path_to_files + file, reference_intensity[0],
                                       lambda_range, reference_intensity[1], R0)
            fitted_values, pcov = curve_fit(new_multilay, lambda_range, real_data, p0=fitted_values,
                                            bounds=((fitted_values[0], 0.9), (fitted_values[0] + 10, 1.1)))
            fitted_data = new_multilay(lambda_range, *fitted_values)
            error.append(calculate_r_squared(real_data, fitted_data))
            save_plot(lambda_range, real_data, fitted_data, path_to_save, fitted_values, i)
            # print(round(popt,2), calculate_r_squared(R_spectrum, new_multilay(lambda_range, *popt)))
            # if i == 356:
            # plt.plot(lambda_range, R_spectrum, lambda_range, new_multilay(lambda_range, *popt))
            # plt.xlim(lambda_min, lambda_max)
            # plt.ylim(0.75, 0.95)
            # plt.yticks(np.arange(0.75, 0.90, 0.05))
            # plt.title("{} d={:.3f} m={:.3f}".format(file, *popt))
            # #plt.show()
            #
            # plt.savefig("S:\\Plots\\plot{} d={:.3f} m={:.3f}.png".format(i, *popt))
            # plt.clf()
        except IOError as e:
            break
            time.sleep(time_interval / 10)
            print(str(e)[-21:] + "waiting...")

    print("R^2 average: ", np.average(error))

    # if i > 400:
    #     break

    # hey = []
    # times = np.arange(0, 0.8 * len(file_names) - 1, 0.8)
    #
    # guess = [100, 1]
    # guess_history = [70]
    #
    # # gueses = np.arange(83.4298688846777, 83.4298688846777 + (0.8746416877 * (len(times))), 0.8746416877)
    # gueses = np.arange(66.55, 66.55 + (0.4 * (len(times))), 0.4)
    #
    # avg_time = np.empty(len(file_names) - 1)
    # avg_error = np.empty(len(file_names) - 1)
    # for i, file in enumerate(file_names):
    #     start_time = time.time()
    #     if file == "ref_spektrs.txt" or file == "R00599.txt":
    #         continue
    #     # spectrum0 = np.genfromtxt(file, delimiter='\t', skip_header=17, skip_footer=1)
    #     # intens_spektrs = spectrum0[:, 1]
    #     # intenst_spektrs_int = interp1d(reference_intensity[0], intens_spektrs, kind='cubic')
    #     # intenst_spektrs_interp = intenst_spektrs_int(lambda_range)
    #     # R_spektrs = intenst_spektrs_interp / reference_intensity[1] * R0
    #     # plt.plot(lambda_range,R_spektrs)
    #     # plt.show()
    #     R_spektrs = get_r_spectrum(file, reference_intensity[0], lambda_range, reference_intensity[1], R0)
    #     # print(R_spektrs)
    #
    #     # guess_history.append(guess[0])
    #     # minimal_guess = min(guess_history)
    #
    #     # if i == 0:
    #     #     popt, pcov = curve_fit(new_multilay, lambda_range, R_spektrs, p0=guess,
    #     #                            bounds=((40, 0.95), (120, 1.1)))
    #     # else:
    #
    #     popt, pcov = curve_fit(new_multilay, lambda_range, R_spektrs, p0=guess,
    #                            bounds=((guess[0], 0.9), (600, 1.1)))
    #     # avg_error[i] = mean_squared_error(R_spektrs, new_multilay(lambda_range, *popt), squared=False)
    #
    #     guess_history.append(popt[0])
    #     print(file, round(times[i], 1), round(avg_error[i], 4), round(popt[0], 2))
    #     guess = popt
    #     # guess[0] = popt[0]
    #
    #     hey.append(popt[0])
    #
    #     plt.plot(lambda_range, R_spektrs, lambda_range, new_multilay(lambda_range, *popt))
    #     plt.title("{} d={:.3f} m={:.3f}".format(file, *popt))
    #     plt.xlim(480, 800)
    #     plt.ylim(0.75, 0.95)
    #     plt.yticks(np.arange(0.75, 0.95, 0.05))
    #     plt.savefig("S:\\Plots\\plot{} d={:.3f} m={:.3f}.png".format(i + 1, *popt))
    #     plt.clf()
    #
    #     # print(avg_error[i])
    #     # time_end = time.time()
    #     # avg_time[i] = time_end - start_time
    #
    # # plt.close()
    # # plt.plot(times, hey)
    # # plt.savefig("S:\\Plots\\layerintime.png")
    # # print(np.average(avg_error))
    # #
    # # plt.close()
    # # res = stats.linregress(times, hey)
    # # print(res)
    # # plt.plot(times, hey, times, res.intercept + res.slope * times)
    # # plt.savefig("S:\\Plots\\layerintime1.png")
    # #
    # # plt.close()
    # # plt.plot(times, avg_error)
    # # plt.savefig("S:\\Plots\\errorintime.png")
    # # print(np.average(avg_time))
    # # plt.show()
    #
    # # nmaltab = data[0:len(data), 0] * 1000
    # # nkaltab = np.array(data[0:len(data), 1] + j * (data[0:len(data), 2]))
    # # nkal_inter = interp1d(nmaltab, nkaltab, kind='cubic')
    # # nkal = nkal_inter(lambd)

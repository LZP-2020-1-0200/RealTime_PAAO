import os
import threading
from pathlib import Path

import numpy as np
import pandas as pd
import PySimpleGUI as sg
import serial.tools.list_ports
from scipy.optimize import curve_fit

from functions import get_spectra_filename, interpolate, save_plots, split_to_arrays
from ntilde import create_ntilde, get_al203_data, get_al_data_from_file, get_water_data_from_file
from window import clear_axis, GraphicalInterface, set_plot_labels, update_validation_image


def connect_arduino(ports, description):
    for port, desc, _ in ports:
        if description in desc:
            por = port
            return serial.Serial(port=por, baudrate=9600, timeout=0.1)


def multilayer(x: np.array, thickness: float, normalization: float):
    M_ = np.full((len(x), 2, 2), [[1, 0], [0, 1]])
    tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
    rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
    T = np.array([[np.ones(len(x)), rho], [rho, np.ones(len(x))]]) / tau
    M = M_ @ T.T
    k = ntilde[1] * 2 * np.pi / x
    P = np.array([[np.exp(j * k * thickness), np.zeros(len(x))],
                  [np.zeros(len(x)), np.exp(-j * k * thickness)]])
    M = M @ P.T
    Ef = np.array([[np.ones(len(x))], [(ntilde[1] - ntilde[2]) /
                                       (ntilde[1] + ntilde[2])]]).T.reshape(len(x), 2, 1)
    E_0 = M @ Ef
    return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * normalization


def get_time_intervals(times):
    history = np.array(times)
    intervals = np.diff(history)
    intervals = np.insert(intervals, 0, 0., axis=0)
    return np.cumsum(intervals)


def draw_last_plots():
    global real_data, current_file, plotting, thickness_history, i, real_data_history, fitted_data
    clear_axis(gui.ax, 0, 350, 0, desired_thickness + 20)
    clear_axis(gui.ax2, lambda_range[0], lambda_range[-1], 0.75, 0.95)

    thickness_history_plotting = np.array(thickness_history)[:, 0]

    gui.ax.plot(time_history[:len(thickness_history_plotting)], thickness_history_plotting)
    gui.ax2.plot(lambda_range, real_data, lambda_range, fitted_data)

    set_plot_labels(gui.ax, 'Time (s)', 'Thickness (nm)')
    set_plot_labels(gui.ax2, 'Wavelength (nm)', 'Reflection (a.u.)')

    gui.ax2.set_xticks(np.arange(480, 820, 40))
    gui.ax2.set_yticks(np.arange(0.75, 1.0, 0.05))

    anodizing_time_title = 'Thickness:{}$nm$  Time:{}$s$'.format(str((round(fitted_values[0], 3))),
                                                                 str((round(time_history[i], 3))))
    gui.ax.set_title(anodizing_time_title)

    gui.ax2.set_title(current_file)

    gui.fig_agg.draw()
    gui.fig_agg2.draw()


def plotting1():
    global real_data, current_file, plotting, thickness_history, i, real_data_history, fitted_data, time_history
    while plotting:
        try:
            clear_axis(gui.ax, 0, 350, 0, desired_thickness + 20)
            clear_axis(gui.ax2, lambda_range[0], lambda_range[-1], 0.75, 0.95)

            thickness_history_plotting = np.array(thickness_history)[:, 0]
            gui.ax.plot(time_history[:len(thickness_history_plotting)], thickness_history_plotting)
            gui.ax2.plot(lambda_range, real_data, lambda_range, fitted_data)

            set_plot_labels(gui.ax, 'Time (s)', 'Thickness (nm)')
            set_plot_labels(gui.ax2, 'Wavelength (nm)', 'Reflection (a.u.)')

            anodizing_time_title = 'Thickness:{}$nm$  Time:{}$s$'.format(str((round(fitted_values[0], 3))),
                                                                         str((round(time_history[i], 3))))
            gui.ax.set_title(anodizing_time_title)
            gui.ax2.set_title(current_file.name)

            gui.ax2.set_xticks(np.arange(480, 820, 40))
            gui.ax2.set_yticks(np.arange(0.75, 1.0, 0.05))

            gui.fig_agg.draw()
            gui.fig_agg2.draw()
        except:
            pass


def fitting():
    global fitted_values, plotting, i, real_data, current_file, thickness_history, fitted_history, fitted_data, time_history
    skip_lines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 3665, 3666]
    plotting = True
    first_file, second_file = True, True
    time_history = [0]
    ref_time = 0
    threading.Thread(target=plotting1, daemon=True).start()
    gui.window['START'].update(text='Waiting for the files...')
    while fitted_values[0] < desired_thickness and fittings:
        next_file = data_folder / get_spectra_filename(i + 1)
        current_file = data_folder / get_spectra_filename(i)
        if next_file.is_file():

            if first_file:
                ref_time = os.path.getmtime(current_file)
                first_file = False
            elif second_file:
                interval = os.path.getmtime(current_file) - ref_time
                time_history = np.arange(0, interval * round(500 / interval, 0), interval)
                second_file = False

            gui.window['START'].update(text='Working...')
            spectrum_from_file = pd.read_csv(current_file, delimiter='\t', skiprows=skip_lines,
                                             dtype=np.double, names=["Wavelength", "Intensity"])
            intensity_spectrum = interpolate(spectrum_from_file["Wavelength"], spectrum_from_file["Intensity"],
                                             lambda_range)
            real_data = (intensity_spectrum / reference_spectrum) * R0
            real_data_history.append(real_data)
            bound = 2 * (time_history[i - 1] + 0.00001)
            low_bound = fitted_values[0] - bound if fitted_values[0] - bound > 65 else 65
            up_bound = fitted_values[0] + bound

            fitted_values, _ = curve_fit(multilayer, lambda_range, real_data, p0=fitted_values,
                                         bounds=((low_bound, 0.9), (up_bound, 1.1)))

            fitted_data = multilayer(lambda_range, *fitted_values)
            fitted_history.append(fitted_data)

            thickness_history.append(np.round(fitted_values, 3))
            i += 1

    if desired_thickness - fitted_values[0] < 4:
        np.save('real_data', real_data_history)
        np.save('fitted_data', fitted_history)
        gui.window['PAUSE'].update(disabled=True)
        gui.window['START'].update(disabled=True, text='Done', button_color='green')
        gui.window['SAVE-PLOTS'].update(disabled=False)
        gui.window['+10'].update(disabled=True)
        gui.window['-10'].update(disabled=True)
        draw_last_plots()
        plotting = False


fitted_values = [90, 1]
real_data_history = []
fitted_history = []
i = 1
save_path = None
plotting, fittings = False, False
real_data, current_file = None, None
time_history = []
fitted_data = None
lambda_range = np.arange(480, 801)
thickness_history = []
path_to_refractive_info = Path("Refractive_info/")
j = complex(0, 1)

nk_water = interpolate(*get_water_data_from_file(path_to_refractive_info, 1e3), lambda_range)
nk_al2o3 = get_al203_data(len(nk_water))
nk_al = interpolate(*get_al_data_from_file(path_to_refractive_info, 1e3), lambda_range)
ntilde = create_ntilde(nk_water, nk_al2o3, nk_al)

R0 = multilayer(lambda_range, 0, 1)

available_ports = serial.tools.list_ports.comports()

gui = GraphicalInterface(available_ports)

correct_thickness, correct_time_int, correct_ref_file, correct_folder, arduino_connected = False, False, False, False, False
while True:
    event, values = gui.window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == 'ARDUINO':
        try:
            arduino = connect_arduino(available_ports, values['ARDUINO'])
            arduino.write(bytes('2', 'utf-8'))
            arduino.write(bytes('3', 'utf-8'))
            arduino_connected = True
        except:
            arduino_connected = False
        update_validation_image(gui.window['COM-PORT-IMG'], arduino_connected)

    if event == 'DESIRED-THICK':
        try:
            desired_thickness = np.double(values['DESIRED-THICK'])
            if desired_thickness < 100:
                raise ValueError('Thickness must be at least 100nm!')
            correct_thickness = True
        except ValueError as error:
            correct_thickness = False
        update_validation_image(gui.window['DESIRED-THICK-IMG'], correct_thickness)

    # if event == 'TIME-INTERVAL':
    #     try:
    #         time_interval = np.double(values['TIME-INTERVAL'])
    #         if time_interval < 100:
    #             raise ValueError('Time interval must be at least 100ms!')
    #         time_interval /= 1e3
    #         anodizing_time = np.arange(0, time_interval * 10000, time_interval)
    #         correct_time_int = True
    #     except ValueError:
    #         correct_time_int = False
    #     update_validation_image(gui.window['TIME-INTERVAL-IMG'], correct_time_int)

    if event == 'INC-DATA':
        correct_ref_file = False
        data_folder = Path(sg.popup_get_folder('', no_window=True))
        if data_folder.name and (data_folder / 'ref_spektrs.txt').is_file():
            ref_spectrum_path = Path(data_folder / 'ref_spektrs.txt')
            reference_spectrum_from_file = np.genfromtxt(ref_spectrum_path, delimiter='\t', skip_header=17,
                                                         skip_footer=1, encoding='utf-8')
            reference_spectrum_data = split_to_arrays(reference_spectrum_from_file)
            reference_spectrum = interpolate(*reference_spectrum_data, lambda_range)
            correct_ref_file = True
        update_validation_image(gui.window['INC-DATA-IMG'], correct_ref_file)

    if event == 'START':
        if correct_thickness and correct_ref_file:
            gui.disable_or_enable_buttons(True)
            fittings = True
            threading.Thread(target=fitting, daemon=True).start()
        else:
            sg.popup_error('Check your inputs', title='Input error')

    if event == 'PAUSE':
        gui.disable_or_enable_buttons(False)
        fittings = False
        plotting = False

    if event == '+10':
        fitted_values[0] += 10

    if event == '-10':
        fitted_values[0] -= 10

    if event == 'SAVE-PLOTS':
        save_path = Path(sg.popup_get_folder('', no_window=True))
        if save_path.name:
            break

if save_path:
    gui.exit()
    files = data_folder.rglob('*.txt')
    files = [x for x in files if x.name != 'ref_spektrs.txt']
    time_history = []
    for file in files:
        mttime = file.stat().st_mtime
        # timestamp = datetime.fromtimestamp(mttime)
        # tym = timestamp.strftime("%H:%M:%S.%f")
        time_history.append(mttime)

    time_history = np.array(time_history)
    time_interval = np.diff(time_history)
    print(np.average(time_interval), i)
    time_interval = np.insert(time_interval, 0, 0., axis=0)
    print(time_interval)

    # pd_series = pd.DataFrame({'time': time_history})
    # avg_time_interval = pd_series.diff().fillna(0)
    # print(avg_time_interval)
    save_plots(thickness_history, save_path, time_interval)

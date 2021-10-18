import threading
from pathlib import Path

import numpy as np
import PySimpleGUI as sg
from enlighten import Counter
from scipy.optimize import curve_fit

from functions import clear_fitting_figure, connect_arduino, get_anodizing_time, \
    get_real_data, get_reference_spectrum, get_spectra_filenames, \
    save_anodizing_time_dat, save_anodizing_time_figure, save_fitting_dat, save_fitting_figure
from multilayer import LAMBDA_RANGE, multilayer, R0
from window import clear_axis, GraphicalInterface, set_plot_labels, validation_check


def plotting_process():
    global current_real_data, current_file, plotting, thickness_history, i, current_fitted_data, approx_anodizing_time
    while plotting:
        try:
            clear_axis(gui.ax, 0, 350, 0, desired_thickness + 20)
            clear_axis(gui.ax2, LAMBDA_RANGE[0], LAMBDA_RANGE[-1], 0.75, 0.95)

            thickness_history_plot_title = 'Thickness:{:.3f}$nm$  Time: {:.3f}$s$'.format(current_thickness[0],
                                                                                          approx_anodizing_time[i])
            gui.ax.set_title(thickness_history_plot_title)
            gui.ax2.set_title(current_file.name)

            set_plot_labels(gui.ax, 'Time (s)', 'Thickness (nm)')
            set_plot_labels(gui.ax2, 'Wavelength (nm)', 'Reflection (a.u.)')

            gui.ax2.set_yticks(np.arange(0.75, 1.0, 0.05))

            thickness_history_data = np.array(thickness_history)[:, 0]
            gui.ax.plot(approx_anodizing_time[:len(thickness_history_data)], thickness_history_data)
            gui.ax2.plot(LAMBDA_RANGE, current_real_data, LAMBDA_RANGE, current_fitted_data)

            gui.fig_agg.draw()
            gui.fig_agg2.draw()
        except:
            pass


def fitting_process():
    global current_thickness, plotting, i, current_real_data, current_file, thickness_history, fitted_data_history, \
        current_fitted_data, approx_anodizing_time, real_data_history

    gui.window['START'].update(text='Waiting for the files...')
    while fitting:
        filenames = get_spectra_filenames(i)
        current_file, next_file = data_folder / filenames[0], data_folder / filenames[1]
        if next_file.is_file():

            if i == 0:
                ref_time = current_file.stat().st_mtime
                gui.window['START'].update(text='Working...')
                plotting = True
                threading.Thread(target=plotting_process, daemon=True).start()

            if i == 1:
                interval = current_file.stat().st_mtime - ref_time
                interval = interval if interval > 0.1 else 0.25
                approx_anodizing_time = np.arange(0, interval * round(500 / interval, 0), interval)

            current_real_data = get_real_data(current_file, reference_spectrum, LAMBDA_RANGE, R0)
            real_data_history.append(current_real_data)

            current_thickness, _ = curve_fit(multilayer, LAMBDA_RANGE, current_real_data, p0=current_thickness)
            current_thickness[0] = current_thickness[0] if current_thickness[0] > 90 else 90
            thickness_history.append(current_thickness)

            current_fitted_data = multilayer(LAMBDA_RANGE, *current_thickness)
            fitted_data_history.append(current_fitted_data)
            i += 1
            if desired_thickness - current_thickness[0] <= 5:
                gui.window['PAUSE'].update(button_color='orange')

    if desired_thickness - current_thickness[0] <= 1:
        gui.window['PAUSE'].update(disabled=True)
        gui.window['START'].update(disabled=True, text='Done', button_color='green')


# Global variables
current_thickness = [90, 1]
real_data_history, fitted_data_history = [], []
approx_anodizing_time = [0]
thickness_history = []
current_real_data, current_fitted_data = [], []
i = 0
plotting, fitting = False, False
current_file = None

# Validation variables
correct_thickness, correct_ref_file, arduino_connected = False, False, False
gui = GraphicalInterface()
saving = False

while True:
    event, values = gui.window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == 'ARDUINO':
        try:
            arduino = connect_arduino(gui.ports, values['ARDUINO'])
            arduino.write(bytes('2', 'utf-8'))
            arduino.write(bytes('3', 'utf-8'))
            arduino_connected = True
        except:
            arduino_connected = False
        validation_check(gui.window['COM-PORT-IMG'], arduino_connected)

    if event == 'DESIRED-THICK':
        try:
            desired_thickness = float(values['DESIRED-THICK'])
            if desired_thickness < 100:
                raise ValueError('Thickness must be at least 100nm!')
            correct_thickness = True
        except ValueError as error:
            correct_thickness = False
        validation_check(gui.window['DESIRED-THICK-IMG'], correct_thickness)

    if event == 'INC-DATA':
        correct_ref_file = False
        data_folder = Path(sg.popup_get_folder('', no_window=True))
        if data_folder.name and (data_folder / 'ref_spektrs.txt').is_file():
            ref_spectrum_path = Path(data_folder / 'ref_spektrs.txt')
            reference_spectrum = get_reference_spectrum(ref_spectrum_path, LAMBDA_RANGE)
            correct_ref_file = True
        validation_check(gui.window['INC-DATA-IMG'], correct_ref_file)

    if event == 'START':
        if correct_thickness and correct_ref_file:
            gui.disable_buttons()
            fitting = True
            threading.Thread(target=fitting_process, daemon=True).start()
        else:
            sg.popup_error('Check your inputs', title='Input error')

    if event == 'PAUSE':
        gui.window['SAVE-PLOTS'].update(disabled=False)
        fitting, plotting = False, False

    if event == 'SAVE-PLOTS':
        save_path = data_folder / 'Plots'
        save_path.mkdir(parents=True, exist_ok=True)
        saving = True
        break

if saving:
    gui.exit()
    anodizing_time = get_anodizing_time(data_folder)
    progress_bar = Counter(total=len(real_data_history), desc='Saving...', unit='files')

    for i, (real, fitted, thick) in enumerate(zip(real_data_history, fitted_data_history, thickness_history)):
        spectra_filename = get_spectra_filenames(i)[0]
        clear_fitting_figure(spectra_filename, thick, anodizing_time[i])
        save_fitting_figure(LAMBDA_RANGE, real, fitted, save_path, spectra_filename[:-4])
        save_fitting_dat(LAMBDA_RANGE, real, fitted, save_path, spectra_filename[:-4])
        progress_bar.update()

    thickness_history_array = np.array(thickness_history)[:, 0]
    save_anodizing_time_figure(thickness_history_array, anodizing_time, save_path)
    save_anodizing_time_dat(thickness_history_array, anodizing_time, save_path)

    input('Finished!\nPress enter to exit\n')

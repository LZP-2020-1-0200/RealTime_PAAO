import threading
from datetime import datetime
from getpass import getuser
from pathlib import Path

import numpy as np
import pandas as pd
import PySimpleGUI as sg
from enlighten import Counter
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

from functions import copy_files, get_anodizing_time, get_real_data, \
    get_reference_spectrum, make_folder, move_file,save_fitting_dat, save_fitting_figure
from multilayer import LAMBDA_RANGE, multilayer, R0
from window import GraphicalInterface, update_info_element, validation_check


def clear_fitting_figure(filename, thick, time):
    plt.clf()
    plt.xlim(480, 800)
    plt.ylim(0.75, 0.95)
    plt.yticks(np.arange(0.75, 0.90, 0.05))
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflection (a.u.)")
    plt.title("file={}  d={}  t={}".format(filename, np.round(thick, 3), round(time, 3)))


def save_anodizing_time_figure(current_hist, current_time, thickness_hist, thickness_time, path):
    fig, ax1 = plt.subplots()
    ax1.plot(thickness_time, thickness_hist, label='Thickness per time')
    ax1.set_xlabel("Time $(s)$")
    ax1.set_ylabel("Thickness $(nm)$")
    fig.legend()
    ax1.grid()
    ax1.set_title("PAAO thickness dependence on anodization time")
    fig.savefig(path / 'Thickness_per_time.png')

def save_anodizing_time_dat(current, thickness_hist, time, path):
    thick_per_time = pd.DataFrame({'Time(s)'      : time[:len(thickness_hist)],
                                   'Thickness(nm)': thickness_hist})
    thick_per_time.to_csv(path / 'Thickness_per_time.dat', sep='\t', index=False)


def make_folders_and_move_files(pre_end_index, post_start_index):
    global anod_folder, plot_folder, calculated_data_folder, organized_folder
    window['PAUSE'].update(text="Reorganizing files, Please wait... ")
    original_folder = make_folder(data_folder, 'Originals')
    organized_folder = make_folder(data_folder, 'Organized files')

    pre_anod_folder = make_folder(organized_folder, '1. Pre anodizing spectrum')
    anod_folder = make_folder(organized_folder, '2. Anodizing spectrum')
    post_anod_folder = make_folder(organized_folder, '3. Post anodizing spectrum')
    plot_folder = make_folder(organized_folder, '4. Anodizing Plots')
    calculated_data_folder = make_folder(organized_folder, '5. Anodizing Data')

    all_files = data_folder.rglob(TXT_EXTENSION)
    files = [x for x in all_files if x.is_file()]
    copy_files([files[-1]], anod_folder)
    move_file([files[-1]], original_folder)
    files.pop()

    pre_anod_files = files[:pre_end_index]
    anod_files = files[pre_end_index:post_start_index]
    post_anod_files = files[post_start_index:]

    copy_files(pre_anod_files, pre_anod_folder)
    copy_files(anod_files, anod_folder)
    copy_files(post_anod_files, post_anod_folder)

    move_file(pre_anod_files, original_folder)
    move_file(anod_files, original_folder)
    move_file(post_anod_files, original_folder)
    window['PAUSE'].update(text="Done reorganizing files", disabled=True)
    window['SAVE-PLOTS'].update(disabled=False)


def fitting_thread():
    global current_thickness, current_real_data, current_file, thickness_history, fitted_data_history, \
        current_fitted_data, approx_anodizing_time, real_data_history, milli_amp_history, pre_anod_ending_index, \
        post_anod_starting_index, current_flowing, ref_spectrum_name, thickness_per_time_line, LOG_FILE, \
        start_plotting, start_ploting_time

    all_txt_files = data_folder.glob(TXT_EXTENSION)
    files = [x for x in all_txt_files]
    spektri = files[:-1]
    anodizing_time = np.round(get_anodizing_time(data_folder), 2)
    theoretical = anodizing_time * 0.8108188540050140 + 70.3530639434863000

    for i, (spektrs, time) in enumerate(zip(spektri, anodizing_time)):

        current_real_data = get_real_data(spektrs, reference_spectrum, LAMBDA_RANGE, R0)
        real_data_history.append(current_real_data)
        current_thickness, _ = curve_fit(multilayer, LAMBDA_RANGE, current_real_data,
                                         p0=(theoretical[i], current_thickness[1]))
        current_thickness[0] = current_thickness[0] if current_thickness[0] >= 90 else 90
        thickness_history.append(current_thickness[0])
        current_fitted_data = multilayer(LAMBDA_RANGE, *current_thickness)
        fitted_data_history.append(current_fitted_data)
        update_info_element(window, INFO_THICKNESS, round(current_thickness[0], 2), 'nm')
        update_info_element(window, INFO_ANOD_TIME, round(time, 3), 's')
        update_info_element(window, INFO_FILE, spektrs.name)
        thickness_per_time_line.set_xdata(anodizing_time[:i])
        thickness_per_time_line.set_ydata(thickness_history[:i])
        real_spectra_line.set_ydata(current_real_data)
        fitted_spectra_line.set_ydata(current_fitted_data)

        if (gui.ax.get_xlim()[1]) - anodizing_time[i] < 30:
            gui.ax.set_xlim(0, gui.ax.get_xlim()[1] + 50)

        if (gui.ax.get_ylim()[1]) - current_thickness[0] < 20:
            gui.ax.set_ylim(gui.ax.get_ylim()[0], gui.ax.get_ylim()[1] + 30)


        gui.fig_agg.draw()
        gui.fig_agg2.draw()
        gui.fig_agg.flush_events()
        gui.fig_agg2.flush_events()


current_thickness = [90, 1]
real_data_history, fitted_data_history = [], []
approx_anodizing_time = [0]
milli_amp_history = []
thickness_history = []
current_real_data, current_fitted_data = [], []
i = 0
fitting = False
current_file = Path()
pre_anod_ending_index, post_anod_starting_index = 0, 0
current_flowing = False
ref_spectrum_name = ''
anod_folder, plot_folder, calculated_data_folder, organized_folder = Path(), Path(), Path(), Path()

# Validation variables
correct_thickness, correct_ref_file, arduino_connected = False, False, False

saving = False

TXT_EXTENSION = '*.txt'
NI_VOLTAGE_TO_MA_COEFFICIENT = 0.986203059047487
ALLOWED_REF_SPEKTRS_NAME = ['ref_spektrs.txt', 'ref spektrs.txt', 'rf_spektrs.txt', 'r_spektrs.txt',
                            'r spektrs.txt']
PATH_TO_DESKTOP = Path(f'C:\\users\\{getuser()}\\Desktop\\')
LOG_FILE = PATH_TO_DESKTOP / (str(datetime.now().strftime("%d.%m.%Y %H.%M.%S")) + ' log.txt')
# Info elements
INFO_ANOD_TIME = 'ANOD-TIME'
INFO_THICKNESS = 'ANOD-THICK'
INFO_CURRENT = 'ANOD-CURRENT'
INFO_FILE = 'ANOD-FILE'
INFO_ERROR = 'ANOD-ERROR'
start_plotting = False
start_ploting_time = 0

if __name__ == '__main__':
    gui = GraphicalInterface()
    window = gui.window

    thickness_per_time_line, = gui.ax.plot([0], [0], color='tab:blue', label='Thickness')
    gui.ax.set_ylim(0, 300)
    fitted_spectra_line = gui.ax2.plot([0], [0], color='orange', label='Fitted', linewidth=2)[0]
    real_spectra_line = gui.ax2.plot([0], [0], color='tab:blue', label='Real', alpha=0.8)[0]
    theoretical = gui.ax.plot(np.arange(0, 500), np.arange(0, 500) * 0.8108188540050140 + 70.3530639434863000,
                              color='b', ls=':', label='Theoretical')
    real_spectra_line.set_xdata(LAMBDA_RANGE)
    fitted_spectra_line.set_xdata(LAMBDA_RANGE)

    gui.fig.legend(loc="upper left", bbox_to_anchor=(0, 1), bbox_transform=gui.ax.transAxes)
    gui.ax2.legend()

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'INC-DATA':
            correct_ref_file = False
            data_folder = Path(sg.popup_get_folder('', no_window=True))
            files = [file.name for file in data_folder.rglob(TXT_EXTENSION)]
            ref_spectrum_name = ''
            if str(files[-1]).lower() in ALLOWED_REF_SPEKTRS_NAME:
                ref_spectrum_name = str(files[-1])
            elif str(files[0]).lower() in ALLOWED_REF_SPEKTRS_NAME:
                ref_spectrum_name = str(files[0])

            if ref_spectrum_name and data_folder.name and (data_folder / ref_spectrum_name).is_file():
                ref_spectrum_path = Path(data_folder / ref_spectrum_name)
                reference_spectrum = get_reference_spectrum(ref_spectrum_path, LAMBDA_RANGE)
                correct_ref_file = True
            validation_check(window['INC-DATA-IMG'], correct_ref_file)
            all_txt_files = data_folder.glob(TXT_EXTENSION)
            files = [x for x in all_txt_files]
            spektri = files[:-1]

        if event == 'START':

            if correct_ref_file:
                gui.disable_buttons()
                fitting = True
                threading.Thread(target=fitting_thread, daemon=True).start()

            else:
                sg.popup_error('Check your inputs', title='Input error')

        if event == 'PAUSE':
            window['START'].update(text='Done', disabled=True)
            fitting = False
            threading.Thread(target=make_folders_and_move_files, daemon=True,
                             args=(0, len(spektri))).start()

        if event == 'SAVE-PLOTS':
            saving = True
            break

    if saving:
        gui.exit()
        anodizing_time = get_anodizing_time(anod_folder)
        progress_bar = Counter(total=len(anodizing_time), desc='Saving...', unit='files')
        # get anodotaion data
        real_data_history_anod = real_data_history
        fitted_data_history_anod = fitted_data_history
        thickness_history_anod = thickness_history

        spectrum_files = [file.name for file in anod_folder.rglob(TXT_EXTENSION) if file.name != 'ref_spektrs.txt']

        save_anodizing_time_figure([], [], thickness_history_anod, anodizing_time, organized_folder)
        save_anodizing_time_dat({}, thickness_history_anod, anodizing_time, organized_folder)

        for i, file in enumerate(spectrum_files):
            clear_fitting_figure(str(file), thickness_history_anod[i], anodizing_time[i])
            save_fitting_figure(LAMBDA_RANGE, real_data_history_anod[i],
                                fitted_data_history_anod[i], plot_folder, str(file)[:-4])
            save_fitting_dat(LAMBDA_RANGE, real_data_history_anod[i],
                             fitted_data_history_anod[i], calculated_data_folder, str(file)[:-4])
            progress_bar.update()
        input('Finished!\nPress enter to exit\n')

import threading
import time
from pathlib import Path

import numpy as np
import PySimpleGUI as sg
from enlighten import Counter
from scipy.optimize import curve_fit

from functions import clear_fitting_figure, copy_files, get_anodizing_time, get_real_data, get_reference_spectrum, \
    get_spectra_filenames2, make_folder, move_file, save_anodizing_time_dat, save_anodizing_time_figure, \
    save_fitting_dat, save_fitting_figure, upgraded_get_spectra_filenames
from multilayer import LAMBDA_RANGE, multilayer, R0
from national_instruments import close_all_tasks, digital_output_task, read_voltage_task, \
    reset_tasks
from window import clear_axis, GraphicalInterface, set_plot_labels, validation_check

TXT_FILES = '*.txt'


def make_folders_and_move_files(pre_end_index, post_start_index):
    global anod_folder, plot_folder, calculated_data_folder, organized_folder
    gui.window['PAUSE'].update(text="Reorganizing files, Please wait... ")
    original_folder = make_folder(data_folder, 'Originals')
    organized_folder = make_folder(data_folder, 'Organized files')

    pre_anod_folder = make_folder(organized_folder, '1. Pre anodizing spectrum')
    anod_folder = make_folder(organized_folder, '2. Anodizing spectrum')
    post_anod_folder = make_folder(organized_folder, '3. Post anodizing spectrum')
    plot_folder = make_folder(organized_folder, '4. Anodizing Plots')
    calculated_data_folder = make_folder(organized_folder, '5. Anodizing Data')

    all_files = data_folder.rglob(TXT_FILES)
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
    gui.window['PAUSE'].update(text="Done reorganizing files", disabled=True)
    gui.window['SAVE-PLOTS'].update(disabled=False)


def plotting_process():
    global current_real_data, current_file, plotting, thickness_history, i, current_fitted_data, \
        approx_anodizing_time, voltage_history
    while plotting:
        try:
            clear_axis(gui.ax, 0, 400, 0, desired_thickness + 20)
            clear_axis(gui.ax2, LAMBDA_RANGE[0], LAMBDA_RANGE[-1], 0.75, 0.95)
            gui.ax3.cla()
            gui.ax3.set_ylim(-1, 1)

            thickness_history_plot_title = 'Thickness:{:.3f}$nm$  Time:{:.3f}$s$  Current:{:.3f}$A$'.format(
                current_thickness[0], approx_anodizing_time[i], voltage_history[i])
            gui.ax.set_title(thickness_history_plot_title)
            gui.ax2.set_title(current_file.name)

            set_plot_labels(gui.ax, 'Time (s)', 'Thickness (nm)')
            gui.ax3.set_ylabel('Current (A)')
            set_plot_labels(gui.ax2, 'Wavelength (nm)', 'Reflection (a.u.)')

            # set_plot_labels(gui.ax3, 'Voltage (V)', 'Reflection (a.u.)')

            gui.ax2.set_yticks(np.arange(0.75, 1.0, 0.05))
            thickness_history_data = np.array(thickness_history)[:, 0]
            gui.ax.plot(approx_anodizing_time[:len(thickness_history_data)], thickness_history_data)
            gui.ax3.plot(approx_anodizing_time[:len(thickness_history_data)], voltage_history[:len(
                thickness_history_data)], color='orange')
            gui.ax2.plot(LAMBDA_RANGE, current_real_data, LAMBDA_RANGE, current_fitted_data)

            gui.fig_agg.draw()
            gui.fig_agg2.draw()
        except Exception as e:
            pass


def fitting_process():
    global current_thickness, plotting, i, current_real_data, current_file, thickness_history, fitted_data_history, \
        current_fitted_data, approx_anodizing_time, real_data_history, voltage_history, pre_anod_ending_index, \
        post_anod_starting_index, current_flowing, ref_spectrum_name

    getting_file = True
    gui.window['START'].update(text='Waiting for the files...')
    start_time = time.time()
    while fitting:

        if getting_file:
            files = [str(x.name) for x in data_folder.rglob(TXT_FILES)]
            files.remove(ref_spectrum_name.lower())
            if len(files) > 0:
                name = str(files[0])[:-4]
                number_of_zeros = name.count('0') - 1
                begining = name[:len(name) - (number_of_zeros + 1)]
                dict = upgraded_get_spectra_filenames(number_of_zeros, begining)
                getting_file = False
            continue

        # if getting_file:
        #     filenames = get_spectra_filenames(i)
        # else:
        filenames = get_spectra_filenames2(dict, i)
        current_file, next_file = data_folder / filenames[0], data_folder / filenames[1]
        if next_file.is_file():
            # testing purposes
            # if i == 70:
            #     create_voltage_task.write(3)
            #     print((time.time() - start_time) / i)
            # real life no needs

            current_voltage = read_voltage_task.read()
            voltage_history.append(current_voltage)

            if current_flowing and pre_anod_ending_index == 0:
                pre_anod_ending_index = i
                # current_flowing = True
                # print(pre_anod_ending_index)

            # print(f'Pirms anodesanas no 0 lidz {pre_anod_ending_index} Anodesana no {pre_anod_ending_index} lidz {
            # post_anod_starting_index}')

            if i == 0:
                ref_time = current_file.stat().st_mtime
                gui.window['START'].update(text='Working...')
                plotting = True
                threading.Thread(target=plotting_process, daemon=True).start()

            if i == 1:
                interval = current_file.stat().st_mtime - ref_time
                interval = interval if interval > 0.1 else 0.25
                approx_anodizing_time = np.arange(0, interval * round(1000 / interval, 0), interval)

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

            if desired_thickness <= current_thickness[0] and current_flowing:
                post_anod_starting_index = i

                current_flowing = False
                # testing purposes
                # create_voltage_task.write(0)
                # digital_output_task.write(True)
                # real life
                digital_output_task.write(True)


    if desired_thickness - current_thickness[0] <= 1:
        gui.window['PAUSE'].update(disabled=True)
        gui.window['START'].update(disabled=True, text='Done', button_color='green')


# Global variables
current_thickness = [90, 1]
real_data_history, fitted_data_history = [], []
approx_anodizing_time = [0]
voltage_history = []
thickness_history = []
current_real_data, current_fitted_data = [], []
i = 0
plotting, fitting = False, False
current_file = Path()
pre_anod_ending_index, post_anod_starting_index = 0, 0
current_flowing = False
ref_spectrum_name = ''
anod_folder, plot_folder, calculated_data_folder, organized_folder = Path(), Path(), Path(), Path()
allowed_name_ref_spektrs = ['ref_spektrs.txt', 'ref spektrs.txt', 'rf_spektrs.txt', 'r_spektrs.txt', 'r spektrs.txt']

# Validation variables
correct_thickness, correct_ref_file, arduino_connected = False, False, False
gui = GraphicalInterface()
saving = False

while True:
    event, values = gui.window.read()

    if event == sg.WIN_CLOSED:
        reset_tasks()
        close_all_tasks()
        break

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
        files = [file.name for file in data_folder.rglob(TXT_FILES)]
        ref_spectrum_name = ''
        if str(files[-1]).lower() in allowed_name_ref_spektrs:
            ref_spectrum_name = str(files[-1])
        elif str(files[0]).lower() in allowed_name_ref_spektrs:
            ref_spectrum_name = str(files[0])

        if ref_spectrum_name and data_folder.name and (data_folder / ref_spectrum_name).is_file():
            ref_spectrum_path = Path(data_folder / ref_spectrum_name)
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
    # else:
    #     sg.popup_error('National instruments not connected', title='Input error')

    if event == 'PAUSE':
        gui.window['START'].update(text='Done', disabled=True)
        # gui.window['SAVE-PLOTS'].update(disabled=False)
        fitting, plotting = False, False
        try:
            reset_tasks()
            close_all_tasks()
        except:
            pass

        threading.Thread(target=make_folders_and_move_files, daemon=True,
                         args=(pre_anod_ending_index, post_anod_starting_index)).start()

    if event == 'SAVE-PLOTS':
        saving = True
        break

    if event == 'START-ELECTRICITY':
        print(current_flowing)
        current_flowing = True
        digital_output_task.write(False)

    if event == 'STOP-ELECTRICITY':
        print(current_flowing)
        current_flowing = False
        digital_output_task.write(True)



if saving:
    gui.exit()
    anodizing_time = get_anodizing_time(anod_folder)
    progress_bar = Counter(total=len(anodizing_time), desc='Saving...', unit='files')
    # get anodotaion data
    real_data_history_anod = real_data_history[pre_anod_ending_index:post_anod_starting_index]
    fitted_data_history_anod = fitted_data_history[pre_anod_ending_index:post_anod_starting_index]
    thickness_history_anod = thickness_history[pre_anod_ending_index:post_anod_starting_index]
    voltage_history_anod = voltage_history[pre_anod_ending_index:post_anod_starting_index]

    spectrum_files = [file.name for file in anod_folder.rglob(TXT_FILES) if file.name != 'ref_spektrs.txt']

    for i, file in enumerate(spectrum_files):
        clear_fitting_figure(str(file), thickness_history_anod[i], anodizing_time[i])
        save_fitting_figure(LAMBDA_RANGE, real_data_history_anod[i],
                            fitted_data_history_anod[i], plot_folder, str(file)[:-4])
        save_fitting_dat(LAMBDA_RANGE, real_data_history_anod[i],
                         fitted_data_history_anod[i], calculated_data_folder, str(file)[:-4])
        progress_bar.update()

    thickness_history_anod = np.array(thickness_history_anod)[:, 0]

    # for i, (real, fitted, thick) in enumerate(zip(real_data_history_anod, fitted_data_history_anod,
    # thickness_history_anod)):
    #     spectra_filename = get_spectra_filenames(i)[0]
    #     clear_fitting_figure(spectra_filename, thick, anodizing_time[i])
    #     save_fitting_figure(LAMBDA_RANGE, real, fitted, plot_folder, spectra_filename[:-4])
    #     save_fitting_dat(LAMBDA_RANGE, real, fitted, calculated_data_folder, spectra_filename[:-4])
    #     progress_bar.update()

    save_anodizing_time_figure(voltage_history_anod, thickness_history_anod, anodizing_time,
                               organized_folder)
    save_anodizing_time_dat(voltage_history_anod, thickness_history_anod, anodizing_time, organized_folder)

    input('Finished!\nPress enter to exit\n')

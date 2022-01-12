import csv
import threading
import time
from datetime import datetime
from getpass import getuser
from multiprocessing import Manager, Process, Value
from pathlib import Path

import nidaqmx
import numpy as np
import PySimpleGUI as sg
from enlighten import Counter
from scipy.optimize import curve_fit

from functions import clear_fitting_figure, copy_files, emergency_save, get_anodizing_time, get_real_data, \
    get_reference_spectrum, \
    get_spectra_filenames2, make_folder, move_file, save_anodizing_time_and_current_plots, save_anodizing_time_dat, \
    save_anodizing_time_figure, save_fitting_dat, save_fitting_figure, upgraded_get_spectra_filenames
from multilayer import LAMBDA_RANGE, multilayer, R0
from national_instruments import close_all_tasks, digital_output_task, reset_tasks
from window import enable_or_disable_power_button, GraphicalInterface, update_info_element, validation_check


def get_milli_volts(log_file, power_off, display_value, time_and_measurment_dict, window_open):
    reader_counter = 0
    # read_voltage_task = nidaqmx.Task()
    # read_voltage_task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=-0.01, max_val=0.01)
    with nidaqmx.Task() as read_voltage_task:
        read_voltage_task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=-0.01, max_val=0.01)
        while window_open.value:
            if power_off.value:
                try:

                    milli_voltage = (
                                            read_voltage_task.read() * 1000) / NI_VOLTAGE_TO_MA_COEFFICIENT  #
                    # volts to milli-amps
                    # print(power_off.value, milli_voltage)
                    # milli_voltage = random.random()
                    display_value.value = round(milli_voltage, 3)
                except:
                    with open(log_file, 'a') as f:
                        f.write(f'\nFailed to read voltage at: {datetime.now().strftime("%H:%M:%S.%f")[:-3]}')
            else:
                try:
                    milli_voltage = (
                                            read_voltage_task.read() * 1000) / NI_VOLTAGE_TO_MA_COEFFICIENT  #
                    # volts to milli-amps
                    # milli_voltage = random.random()
                    display_value.value = round(milli_voltage, 3)
                    if reader_counter == 0:
                        reference = time.time()

                    time_and_measurment_dict[time.time() - reference] = milli_voltage
                    reader_counter += 1
                except:
                    with open(log_file, 'a') as f:
                        f.write(f'\nFailed to read voltage at: {datetime.now().strftime("%H:%M:%S.%f")[:-3]}')

        # time.sleep(0.005)


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
    global current_fitted_data, i, current_real_data, current_file, thickness_history, fitted_data_history, \
        current_fitted_data, approx_anodizing_time, real_data_history, milli_amp_history, pre_anod_ending_index, \
        post_anod_starting_index, current_flowing, ref_spectrum_name, thickness_per_time_line, LOG_FILE, \
        start_plotting, start_ploting_time, current_thickness, fitted_parameters

    getting_file = True
    window['START'].update(text='Waiting for the files...')
    start_time = 0
    times = []
    while fitting:
        # todo change to real milli_amp
        # milli_amp_history.append(random.random() / 5)
        update_info_element(window, INFO_THICKNESS, round(current_thickness, 2), 'nm')
        if start_time != 0 and not power_off.value:
            update_info_element(window, INFO_ANOD_TIME, round(time.time() - start_time, 3), 's')
        # update_info_element(window, INFO_CURRENT, round(milli_amp_history[-1], 2), 'mA')
        update_info_element(window, INFO_FILE, current_file.name)
        if getting_file:
            files = [str(x.name) for x in data_folder.rglob(TXT_EXTENSION)]
            files.remove(ref_spectrum_name.lower())
            if len(files) > 0:
                name = str(files[0])[:-4]
                number_of_zeros = name.count('0') - 1
                filename_start_letter = name[:len(name) - (number_of_zeros + 1)]
                dict_of_filenames = upgraded_get_spectra_filenames(number_of_zeros, filename_start_letter)
                getting_file = False
            continue

        filenames = get_spectra_filenames2(dict_of_filenames, i)
        current_file, next_file = data_folder / filenames[0], data_folder / filenames[1]
        if next_file.is_file():

            if current_flowing and pre_anod_ending_index == 0:
                pre_anod_ending_index = i
                start_time = time.time()

            if i == 0:
                ref_time = current_file.stat().st_mtime
                window['START'].update(text='Working...')
                with open(LOG_FILE, 'w', encoding="utf-8") as f:
                    starting_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    f.write(f'File reading started at: {starting_time}')

            if i == 1:
                interval = current_file.stat().st_mtime - ref_time
                interval = interval if interval > 0.1 else 0.25
                approx_anodizing_time = np.arange(0, interval * round(1000 / interval, 0), interval)
                with open(LOG_FILE, 'a') as f:
                    f.write(f'\nEstimated interval between files: {round(interval, 4)}')

            current_real_data = get_real_data(current_file, reference_spectrum, LAMBDA_RANGE, R0)
            real_data_history.append(current_real_data)

            if start_ploting_time != 0:
                aaa = (time.time() - start_ploting_time)
                theoretical_thickness = aaa * 0.8108188540050140 + 70.3530639434863000
                fitted_parameters, var_matrix = curve_fit(multilayer, LAMBDA_RANGE, current_real_data,
                                                          p0=(theoretical_thickness, fitted_parameters[1]))
                thickness_history.append(fitted_parameters[0])
                times.append(aaa)
            else:
                fitted_parameters, var_matrix = curve_fit(multilayer, LAMBDA_RANGE, current_real_data,
                                                          p0=fitted_parameters)

            current_thickness = fitted_parameters[0]
            standard_error = round(np.sqrt(np.diagonal(var_matrix))[0], 3)
            update_info_element(window, INFO_ERROR, standard_error)

            current_fitted_data = multilayer(LAMBDA_RANGE, current_thickness, fitted_parameters[1])
            fitted_data_history.append(current_fitted_data)

            if start_plotting:
                thickness_per_time_line.set_xdata(times)
                thickness_per_time_line.set_ydata(np.array(thickness_history)[:, 0])
                current_per_time_line.set_data(time_and_measurement_dict.keys(), time_and_measurement_dict.values())

            real_spectra_line.set_ydata(current_real_data)
            fitted_spectra_line.set_ydata(current_fitted_data)

            if (gui.ax.get_xlim()[1]) - approx_anodizing_time[i] < 30:
                gui.ax.set_xlim(0, gui.ax.get_xlim()[1] + 50)

            if (gui.ax.get_ylim()[1]) - current_thickness[0] < 20:
                gui.ax.set_ylim(gui.ax.get_ylim()[0], gui.ax.get_ylim()[1] + 30)

            try:
                gui.fig_agg.draw()
                gui.fig_agg2.draw()
                gui.fig_agg.flush_events()
                gui.fig_agg2.flush_events()
            except Exception as e:
                print(e)

            if desired_thickness <= current_thickness[0] and current_flowing:
                post_anod_starting_index = i
                current_flowing = False
                with open(LOG_FILE, 'a') as f:
                    end_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    f.write(f'\nSample reached desired thickness at: {end_time}')
                    f.write(f'\nEnd of annodization on file: {current_file.name}')
                digital_output_task.write(True)
                power_off.value = True
                window['PAUSE'].update(disabled=False)
                window['START'].update(disabled=True, text='Done', button_color='green')
                # window['SAVE-PLOTS'].update(disabled=False)
                enable_or_disable_power_button(window)
            i += 1

fitted_parameters = [90, 1]
current_thickness = 0
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
EMERG_THICKNESS = PATH_TO_DESKTOP / 'thickness.txt'
EMERG_CURRENT = PATH_TO_DESKTOP / 'current.txt'
LOG_FILE = PATH_TO_DESKTOP / (str(datetime.now().strftime("%m.%d.%Y %H.%M.%S")) + ' log.txt')
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
    current_per_time_line = gui.ax3.plot([0], [0], color='orange', label='Current', alpha=0.7)[0]
    fitted_spectra_line = gui.ax2.plot([0], [0], color='orange', label='Fitted', linewidth=2)[0]
    real_spectra_line = gui.ax2.plot([0], [0], color='tab:blue', label='Real', alpha=0.8)[0]
    theoretical = gui.ax.plot(np.arange(0, 500), np.arange(0, 500) * 0.8108188540050140 + 70.3530639434863000,
                              color='b',
                              ls=':', label='Theoretical')
    real_spectra_line.set_xdata(LAMBDA_RANGE)
    fitted_spectra_line.set_xdata(LAMBDA_RANGE)

    gui.fig.legend(loc="upper left", bbox_to_anchor=(0, 1), bbox_transform=gui.ax.transAxes)
    gui.ax2.legend()

    start_process = True
    if start_process:
        power_off = Value('i', True)
        display_value = Value('f', 0)
        time_and_measurement_dict = Manager().dict()
        window_open = Value('i', True)
        p = Process(target=get_milli_volts, args=(LOG_FILE, power_off, display_value, time_and_measurement_dict,
                                                  window_open,))
        p.daemon = True
        p.start()
        start_process = False

    update_counter = 0
    while True:
        event, values = window.read(timeout=40)
        update_counter += 1
        if update_counter % 2 == 0:
            update_info_element(window, INFO_CURRENT, round(display_value.value, 3), 'mA')

        #
        if event == sg.WIN_CLOSED:
            window_open.value = False
            reset_tasks()
            close_all_tasks()
            emergency_save(EMERG_THICKNESS, thickness_history[0])
            # emergency_save(EMERG_CURRENT, (time_and_measurement_dict.keys(),time_and_measurement_dict.values()))
            with open(EMERG_CURRENT, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow((['Anod Time', 'Milliamp']))
                for x, y in time_and_measurement_dict.items():
                    writer.writerow([x, y])
            break

        if event == 'DESIRED-THICK':
            try:
                desired_thickness = float(values['DESIRED-THICK'])
                if desired_thickness < 100:
                    raise ValueError('Thickness must be at least 100nm!')
                correct_thickness = True
            except ValueError as error:
                correct_thickness = False
            validation_check(window['DESIRED-THICK-IMG'], correct_thickness)

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

        if event == 'START':

            if correct_thickness and correct_ref_file:
                gui.disable_buttons()
                fitting = True
                threading.Thread(target=fitting_thread, daemon=True).start()

            else:
                sg.popup_error('Check your inputs', title='Input error')

        if event == 'PAUSE':
            window['START'].update(text='Done', disabled=True)
            fitting = False
            try:
                reset_tasks()
                close_all_tasks()
            except:
                pass

            threading.Thread(target=make_folders_and_move_files, daemon=True,
                             args=(pre_anod_ending_index, post_anod_starting_index)).start()

        if event == 'SAVE-PLOTS':
            window_open.value = False
            saving = True
            try:
                reset_tasks()
                close_all_tasks()
            except:
                pass

            break

        if event == 'START-ELECTRICITY':
            digital_output_task.write(False)
            current_flowing = True
            with open(LOG_FILE, 'a') as f:
                f.write(f'\nBeginning of annodization on file: {current_file.name}')
            enable_or_disable_power_button(window)
            power_off.value = False
            start_plotting = True
            start_ploting_time = time.time()

        if event == 'STOP-ELECTRICITY':
            digital_output_task.write(True)
            current_flowing = False
            enable_or_disable_power_button(window)
            power_off.value = True

    if saving:
        gui.exit()
        anodizing_time = get_anodizing_time(anod_folder)
        progress_bar = Counter(total=len(anodizing_time), desc='Saving...', unit='files')
        # get anodotaion data
        real_data_history_anod = real_data_history[pre_anod_ending_index:post_anod_starting_index]
        fitted_data_history_anod = fitted_data_history[pre_anod_ending_index:post_anod_starting_index]
        thickness_history_anod = thickness_history[pre_anod_ending_index:post_anod_starting_index]

        # milli_amp_history_anod = milli_amp_history[pre_anod_ending_index:post_anod_starting_index]

        spectrum_files = [file.name for file in anod_folder.rglob(TXT_EXTENSION) if file.name != 'ref_spektrs.txt']

        for i, file in enumerate(spectrum_files):
            clear_fitting_figure(str(file), thickness_history_anod[i], anodizing_time[i])
            save_fitting_figure(LAMBDA_RANGE, real_data_history_anod[i],
                                fitted_data_history_anod[i], plot_folder, str(file)[:-4])
            save_fitting_dat(LAMBDA_RANGE, real_data_history_anod[i],
                             fitted_data_history_anod[i], calculated_data_folder, str(file)[:-4])
            progress_bar.update()

        thickness_history_anod = np.array(thickness_history_anod)[:, 0]

        save_anodizing_time_figure(time_and_measurement_dict.values(), time_and_measurement_dict.keys(),
                                   thickness_history_anod, anodizing_time, organized_folder)
        save_anodizing_time_and_current_plots(time_and_measurement_dict.values(), time_and_measurement_dict.keys(),
                                              thickness_history_anod, anodizing_time,
                                              organized_folder)
        save_anodizing_time_dat(time_and_measurement_dict, thickness_history_anod, anodizing_time, organized_folder)

        try:
            EMERG_THICKNESS.unlink()
            EMERG_CURRENT.unlink()
        except:
            pass
        input('Finished!\nPress enter to exit\n')

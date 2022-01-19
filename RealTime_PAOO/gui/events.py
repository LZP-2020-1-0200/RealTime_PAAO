import csv
import threading
import time
from pathlib import Path

import PySimpleGUI as sg

import RealTime_PAOO.common.paths as path
import RealTime_PAOO.common.shared as shared
from RealTime_PAOO.common import paths
from RealTime_PAOO.common.constants import ALLOWED_REF_SPEKTRS_NAME, TXT_EXTENSION
from RealTime_PAOO.data.directories import get_data_directory, make_folders_and_move_files, zip_files
from RealTime_PAOO.data.helpers import get_anodizing_time
from RealTime_PAOO.data.national_instruments import close_all_tasks, ni_stop_the_power
from RealTime_PAOO.data.read import get_reference_spectrum
from RealTime_PAOO.data.save import save_current_per_time_data, save_fitting_data, save_thickness_per_time_data
from RealTime_PAOO.gui.helpers import disable_buttons, enable_or_disable_power_button, validation_check
from RealTime_PAOO.multilayer.fitting import fitting_thread_post_factum, fitting_thread_real_time


def desired_thickness_event(window, values):
    shared.correct_thickness = False
    try:
        shared.desired_thickness = float(values['DESIRED-THICK'])
    except ValueError:
        return

    if shared.desired_thickness < 100:
        shared.correct_thickness = False
    else:
        shared.correct_thickness = True

    validation_check(window['DESIRED-THICK-IMG'], shared.correct_thickness)


def choose_data_dir_event(window):
    path.data_folder = get_data_directory()
    shared.list_of_files = [file.name for file in path.data_folder.rglob(TXT_EXTENSION)]

    if not shared.list_of_files:
        validation_check(window['INC-DATA-IMG'], shared.correct_ref_file)
        return

    if str(shared.list_of_files[-1]).lower() in ALLOWED_REF_SPEKTRS_NAME:
        shared.ref_spectrum_name = str(shared.list_of_files[-1])
    elif str(shared.list_of_files[0]).lower() in ALLOWED_REF_SPEKTRS_NAME:
        shared.ref_spectrum_name = str(shared.list_of_files[0])

    if shared.ref_spectrum_name and path.data_folder.name and (path.data_folder / shared.ref_spectrum_name).is_file():
        path.ref_spectrum_path = Path(path.data_folder / shared.ref_spectrum_name)
        shared.reference_spectrum = get_reference_spectrum(path.ref_spectrum_path)
        shared.correct_ref_file = True
    else:
        shared.correct_ref_file = False
    validation_check(window['INC-DATA-IMG'], shared.correct_ref_file)


def start_fitting_event(window, gui, power_on=None, current_dict=None, real_time=True):
    if not shared.correct_ref_file or not shared.correct_thickness:
        sg.popup_error('Check your inputs', title='Input error')
        return

    disable_buttons(window)
    shared.fitting = True
    if real_time:
        threading.Thread(target=fitting_thread_real_time, daemon=True,
                         args=(window, power_on, gui, current_dict)).start()
    else:
        threading.Thread(target=fitting_thread_post_factum, daemon=True,
                         args=(shared.reference_spectrum, gui, path.data_folder)).start()


def stop_fitting_event(window,digital_output_task,list_of_tasks, pre_anod_index=0, post_anod_index=0):
    window['START'].update(text='Done', disabled=True)
    shared.fitting = False
    try:
        ni_stop_the_power(digital_output_task)
        close_all_tasks(list_of_tasks)
    except:
        pass
    threading.Thread(target=make_folders_and_move_files, daemon=True,
                     args=(pre_anod_index, post_anod_index, path.data_folder, window)).start()


def saving_event(window, current_dict,window_open):
    threading.Thread(target=saving_data, args=(window, current_dict,window_open), daemon=True).start()


def saving_data(window, current_dict,window_open):
    window['SAVE'].update(disabled=True)
    window_open.value = False
    window['START-ELECTRICITY'].update(disabled=True)

    anodizing_time = get_anodizing_time(paths.data_folder / paths.anod_folder_name)
    spectrum_files = [file.name for file in (paths.data_folder / paths.anod_folder_name).rglob(TXT_EXTENSION)
                      if str(file.name) not in ALLOWED_REF_SPEKTRS_NAME]
    save_thickness_per_time_data(shared.thickness_history, anodizing_time, (paths.data_folder /
                                                                            paths.organized_folder))
    save_fitting_data(spectrum_files, shared.real_data_history, shared.fitted_data_history, paths.data_folder /
                      paths.fitted_plot_folder_name, paths.data_folder / paths.fitted_data_folder_name, window)
    save_current_per_time_data(current_dict, (paths.data_folder / paths.organized_folder))

    zip_files(paths.data_folder, paths.data_folder.name, window)


def window_close_event(window_open, current_dict, window, digital_output_task, list_of_tasks):
    window.close()
    window_open.value = False
    try:
        ni_stop_the_power(digital_output_task)
        close_all_tasks(list_of_tasks)
    except:
        pass
    time.sleep(1)
    with open(path.emerg_current, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow((['Anod Time', 'Milliamp']))
        for x, y in current_dict.items():
            writer.writerow([x, y])


def start_electricity_event(window, power_on):
    power_on.value = True
    enable_or_disable_power_button(window)


def emergency_stop_event(window, power_on):
    power_on.value = False
    shared.emergency_stop = True
    enable_or_disable_power_button(window)

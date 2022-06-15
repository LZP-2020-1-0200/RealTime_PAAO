import csv
import threading
import time
from pathlib import Path

import PySimpleGUI as sg
import RealTime_PAAO.common.shared as shared
from RealTime_PAAO.common import paths
from RealTime_PAAO.common.constants import ALLOWED_REF_SPEKTRS_NAME, TXT_EXTENSION
from RealTime_PAAO.data.current_control import start_power, stop_power
from RealTime_PAAO.data.directories import get_data_directory, make_folders_and_move, move_spectrums, zip_dir
from RealTime_PAAO.data.helpers import get_anodizing_time
from RealTime_PAAO.data.read import get_reference_spectrum
from RealTime_PAAO.data.save import save_current_per_time_data, save_fitting_data, save_thickness_per_time_data
from RealTime_PAAO.data.upload import upload_to_zenodo
from RealTime_PAAO.gui.main_gui.helpers import disable_buttons, enable_or_disable_power_button, validation_check
from RealTime_PAAO.multilayer.fitting import fitting_thread_post_factum, fitting_thread_real_time


def desired_thickness_event(window, values):
    shared.correct_thickness = False
    try:
        shared.desired_thickness = float(values["DESIRED-THICK"])
    except ValueError:
        return

    if shared.desired_thickness < 100:
        shared.correct_thickness = False
    else:
        shared.correct_thickness = True

    validation_check(window["DESIRED-THICK-IMG"], shared.correct_thickness)


def choose_data_dir_event(window):
    paths.data_folder = get_data_directory()
    shared.list_of_files = [file.name for file in paths.data_folder.rglob(TXT_EXTENSION)]

    if not shared.list_of_files:
        validation_check(window["INC-DATA-IMG"], shared.correct_ref_file)
        return

    if str(shared.list_of_files[-1]).lower() in ALLOWED_REF_SPEKTRS_NAME:
        shared.ref_spectrum_name = str(shared.list_of_files[-1])
    elif str(shared.list_of_files[0]).lower() in ALLOWED_REF_SPEKTRS_NAME:
        shared.ref_spectrum_name = str(shared.list_of_files[0])

    if (
        shared.ref_spectrum_name
        and paths.data_folder.name
        and (paths.data_folder / shared.ref_spectrum_name).is_file()
    ):
        paths.ref_spectrum_path = Path(paths.data_folder / shared.ref_spectrum_name)
        shared.reference_spectrum = get_reference_spectrum(paths.ref_spectrum_path)
        shared.correct_ref_file = True
    else:
        shared.correct_ref_file = False
    validation_check(window["INC-DATA-IMG"], shared.correct_ref_file)


def check_for_reference_spectrum(window):
    paths.ref_spectrum_path = ""
    shared.list_of_files = [file.name for file in paths.path_to_original_folder.rglob(TXT_EXTENSION)]
    if not shared.list_of_files:
        shared.correct_ref_file = False
        validation_check(window["INC-DATA-IMG"], shared.correct_ref_file)
        return

    if str(shared.list_of_files[-1]).lower() in ALLOWED_REF_SPEKTRS_NAME:
        shared.ref_spectrum_name = str(shared.list_of_files[-1])
    elif str(shared.list_of_files[0]).lower() in ALLOWED_REF_SPEKTRS_NAME:
        shared.ref_spectrum_name = str(shared.list_of_files[0])
    else:
        shared.correct_ref_file = False
        validation_check(window["INC-DATA-IMG"], shared.correct_ref_file)
        return

    if paths.path_to_original_folder.name and (paths.path_to_original_folder / shared.ref_spectrum_name).is_file():
        paths.ref_spectrum_path = Path(paths.path_to_original_folder / shared.ref_spectrum_name)
        shared.reference_spectrum = get_reference_spectrum(paths.ref_spectrum_path)
        shared.correct_ref_file = True
    else:
        shared.correct_ref_file = False
    validation_check(window["INC-DATA-IMG"], shared.correct_ref_file)

    with open(paths.ref_spectrum_path, "r") as file:
        datafile = file.readlines()
        for line in datafile:
            if "Integration Time" in line:
                shared.integration_time = line.split(":")[1].split(" ")[1]

                shared.integration_time_units = line.split(":")[0].split(" ")[2].replace("(", "").replace(")", "")
            elif "Spectra Averaged" in line:
                shared.spectra_average = line.split(":")[1].split(" ")[1]

    with open(paths.anodization_parameters, "a", newline="") as file:
        writer = csv.writer(file, delimiter=":")
        writer.writerow(["INTEGRATION TIME", shared.integration_time + " " + shared.integration_time_units])
        writer.writerow(["SPECTRA AVERAGED", shared.spectra_average])


def start_fitting_event(
    window,
    gui,
    power_on=None,
    current_dict=None,
    real_time=True,
):
    if not shared.correct_ref_file or not shared.correct_thickness:
        sg.popup_error("Check your inputs", title="Input error")
        return

    disable_buttons(window)
    shared.fitting = True
    if real_time:
        threading.Thread(
            target=fitting_thread_real_time,
            daemon=True,
            args=(window, power_on, gui, current_dict),
        ).start()
    else:
        threading.Thread(
            target=fitting_thread_post_factum, daemon=True, args=(shared.reference_spectrum, gui, paths.data_folder)
        ).start()


def stop_fitting_event(window, pre_anod_index: int = 0, post_anod_index: int = 0, real_time=True):
    window["START"].update(text="Done", disabled=True)
    shared.fitting = False
    if real_time:
        stop_power()
    if pre_anod_index:
        threading.Thread(
            target=move_spectrums,
            daemon=True,
            args=(pre_anod_index, post_anod_index, paths.path_to_original_folder, window),
        ).start()
    else:
        threading.Thread(target=make_folders_and_move, daemon=True, args=(paths.data_folder, window)).start()


def saving_event(window, current_dict, window_open):
    if current_dict:
        window_open.value = False
    window["SAVE"].update(disabled=True)
    window["START-ELECTRICITY"].update(disabled=True)
    threading.Thread(target=saving_data, args=(window, current_dict), daemon=True).start()


def saving_data(window, current_dict):
    anodizing_time = get_anodizing_time(paths.path_to_anod_folder)

    spectrum_files = [
        file.name for file in paths.path_to_anod_folder.rglob(TXT_EXTENSION) if file.name != shared.ref_spectrum_name
    ]
    save_thickness_per_time_data(shared.thickness_history, anodizing_time, paths.path_to_organized_folder)
    save_fitting_data(
        spectrum_files,
        shared.real_data_history,
        shared.fitted_data_history,
        paths.path_to_fitted_plot_folder,
        paths.path_to_fitted_data_folder,
        window,
    )

    if current_dict:
        save_current_per_time_data(current_dict, paths.path_to_organized_folder)
        a = shared.filename.split(" ")
        a.insert(3, str(round(shared.thickness_history[-1], 2)) + "nm")
        a.insert(4, str(int(anodizing_time[-1])) + "s")
        shared.filename = " ".join(a)
        with open(paths.anodization_parameters, "a", newline="") as file:
            writer = csv.writer(file, delimiter=":")
            writer.writerow(["FITTED THICKNESS", str(round(shared.thickness_history[-1], 2)) + " nm"])
            writer.writerow(["ANODIZATION TIME", str(round(anodizing_time[-1], 2)) + " s"])
        paths.path_to_data_folder = paths.path_to_data_folder.rename(paths.path_to_desktop / shared.filename)
        zip_path = zip_dir(paths.path_to_data_folder, paths.path_to_desktop / shared.filename, window)
        upload_to_zenodo(zip_path.name, zip_path, window)


def window_close_event(window_open, current_dict, window):
    window.close()
    window_open.value = False
    stop_power()
    time.sleep(1)
    with open(paths.emerg_current, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow((["Anod Time", "Milliamp"]))
        for x, y in current_dict.items():
            writer.writerow([x, y])


def start_electricity_event(window, power_on):
    start_power()
    power_on.value = True
    enable_or_disable_power_button(window)


def emergency_stop_event(window, power_on):
    stop_power()
    power_on.value = False
    shared.emergency_stop = True
    enable_or_disable_power_button(window)

import time
from datetime import datetime

import numpy as np
from RealTime_PAAO.common import paths
from RealTime_PAAO.common import shared as shared
from RealTime_PAAO.common.constants import INFO_ANOD_TIME, INFO_FILE, INFO_THICKNESS, LAMBDA, TXT_EXTENSION
from RealTime_PAAO.data.current_control import stop_power
from RealTime_PAAO.data.helpers import construct_spectra_filenames_dict, get_anodizing_time, get_spectra_paths
from RealTime_PAAO.data.read import get_real_data
from RealTime_PAAO.gui.main_gui.helpers import enable_or_disable_power_button, update_info_element
from RealTime_PAAO.gui.main_gui.plots import redraw_plots
from RealTime_PAAO.multilayer.multilayer import R0, multilayer, theoretical_thickness
from scipy.optimize import curve_fit


def fitting_thread_post_factum(reference_spectrum, gui, data_folder):
    files = data_folder.rglob(TXT_EXTENSION)
    files = [x for x in files if x.is_file()]
    spektri = files[:-1]
    anodizing_time = np.round(get_anodizing_time(data_folder), 2)
    for i, (spektrs, time2) in enumerate(zip(spektri, anodizing_time)):

        shared.current_real_data = get_real_data(spektrs, reference_spectrum, R0)
        shared.real_data_history.append(shared.current_real_data)

        shared.fitted_parameters, _ = curve_fit(
            multilayer,
            LAMBDA,
            shared.current_real_data,
            p0=(theoretical_thickness(time2), shared.fitted_parameters[1]),
        )

        current_thickness = shared.fitted_parameters[0]

        shared.thickness_history.append(current_thickness)
        shared.current_fitted_data = multilayer(LAMBDA, current_thickness, shared.fitted_parameters[1])
        shared.fitted_data_history.append(shared.current_fitted_data)

        update_info_element(gui.window, INFO_THICKNESS, round(current_thickness), "nm")
        update_info_element(gui.window, INFO_ANOD_TIME, round(time2, 2), "s")
        update_info_element(gui.window, INFO_FILE, spektrs.name)

        gui.thickness_per_time_line.set_xdata(anodizing_time[:i])
        gui.thickness_per_time_line.set_ydata(shared.thickness_history[:i])
        gui.real_spectra_line.set_ydata(shared.current_real_data)
        gui.fitted_spectra_line.set_ydata(shared.current_fitted_data)

        if (gui.ax.get_xlim()[1]) - anodizing_time[i] < 30:
            gui.ax.set_xlim(0, gui.ax.get_xlim()[1] + 50)

        if (gui.ax.get_ylim()[1]) - current_thickness < 20:
            gui.ax.set_ylim(gui.ax.get_ylim()[0], gui.ax.get_ylim()[1] + 30)

        redraw_plots(gui.fig_agg, gui.fig_agg2)


def fitting_thread_real_time(window, power_on, gui, time_and_measurement_dict):
    window["START"].update(text="Waiting for the files...")
    dict_of_filenames = {}
    start_anod_time = 0
    anod_time_history = []
    current_thickness = 0
    current_anod_time = 0
    i = 0

    while shared.fitting:
        # if anodization is in progress update info panel with time
        if start_anod_time != 0 and power_on.value:
            update_info_element(window, INFO_ANOD_TIME, round(time.time() - start_anod_time, 2), "s")

        # we get the first spectrum filename and construct the dictionary with possible spectrum names
        if not dict_of_filenames:
            files = [str(x.name) for x in paths.path_to_original_folder.rglob(TXT_EXTENSION)]
            files.remove(shared.ref_spectrum_name)

            if len(files) <= 0:
                continue

            dict_of_filenames = construct_spectra_filenames_dict(str(files[0])[:-4])

        current_file, next_file = get_spectra_paths(dict_of_filenames, i, paths.path_to_original_folder)

        if next_file.is_file():
            update_info_element(window, INFO_FILE, current_file.name)
            # write to log file time when first file arrived
            if i == 0:
                window["START"].update(text="Working...")
                with open(paths.log_file, "w", encoding="utf-8") as f:
                    starting_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    f.write(f"File reading started at: {starting_time}")

            # if power is on get the file number and anodization starting time
            if power_on.value and shared.anod_starting_index == 0:
                shared.anod_starting_index = i
                start_anod_time = time.time()

            current_real_data = get_real_data(current_file, shared.reference_spectrum, R0)
            shared.real_data_history.append(current_real_data)

            shared.fitted_parameters, _ = curve_fit(
                multilayer,
                LAMBDA,
                current_real_data,
                p0=(theoretical_thickness(current_anod_time if current_anod_time else 0), shared.fitted_parameters[1]),
            )
            current_thickness = shared.fitted_parameters[0]
            current_fitted_data = multilayer(LAMBDA, *shared.fitted_parameters)
            update_info_element(window, INFO_THICKNESS, round(current_thickness), "nm")

            if (gui.ax.get_xlim()[1]) - current_anod_time < 30:
                gui.ax.set_xlim(0, gui.ax.get_xlim()[1] + 50)

            if (gui.ax.get_ylim()[1]) - current_thickness < 20:
                gui.ax.set_ylim(gui.ax.get_ylim()[0], gui.ax.get_ylim()[1] + 30)

            gui.fitted_spectra_line.set_ydata(current_fitted_data)

            # if anodizing is not started yet, just plot spectrums
            if start_anod_time != 0 and power_on.value:
                current_anod_time = time.time() - start_anod_time
                anod_time_history.append(current_anod_time)

                shared.thickness_history.append(current_thickness)
                shared.fitted_data_history.append(current_fitted_data)

                gui.thickness_per_time_line.set_xdata(anod_time_history)
                gui.thickness_per_time_line.set_ydata(shared.thickness_history)
                gui.current_per_time_line.set_data(
                    time_and_measurement_dict.keys()[::15], time_and_measurement_dict.values()[::15]
                )

            gui.real_spectra_line.set_ydata(current_real_data)

            try:
                redraw_plots(gui.fig_agg, gui.fig_agg2)
            except Exception:
                pass

            if (current_thickness >= shared.desired_thickness and power_on.value) or shared.emergency_stop:
                shared.emergency_stop = False
                shared.anod_ending_index = i + 1
                power_on.value = False
                stop_power()

                with open(paths.log_file, "a") as f:
                    end_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    f.write(f"\nSample approximate thickness: {current_thickness}")
                    f.write(f"\nSample reached desired thickness at: {end_time}")
                    f.write(f"\nEnd of anodization on file: {current_file.name}")

                window["STOP"].update(disabled=False)
                window["START"].update(disabled=True, text="Done", button_color="green")
                # window['SAVE'].update(disabled=False)
                enable_or_disable_power_button(window)
                # gui.fitted_spectra_line.set_ydata(ZEROS)

            i += 1

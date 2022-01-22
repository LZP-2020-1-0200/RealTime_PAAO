import sys
sys.path.append('C:\\Users\\Vladislavs\\PycharmProjects\\RealTime_PAAO\\')
from multiprocessing import freeze_support, Manager, Process, Value

import PySimpleGUI as sg

from RealTime_PAAO.common import shared
from RealTime_PAAO.common.constants import INFO_CURRENT
from RealTime_PAAO.data.national_instruments import get_milli_volts, initialize_national_instruments
from RealTime_PAAO.gui.main_gui.events import check_for_reference_spectrum, emergency_stop_event, \
    saving_event, start_electricity_event, start_fitting_event, stop_fitting_event, window_close_event
from RealTime_PAAO.gui.main_gui.helpers import update_info_element
from RealTime_PAAO.gui.main_gui.main_layout import GraphicalInterface
from RealTime_PAAO.gui.metadata_gui.events import begin_event_loop
from RealTime_PAAO.gui.metadata_gui.metadata_layout import DescriptionGraphicalInterface

if __name__ == '__main__':
    freeze_support()
    metadata_gui = DescriptionGraphicalInterface()
    begin_event_loop(metadata_gui)

    digital_output_task, list_of_tasks = initialize_national_instruments()
    gui = GraphicalInterface()
    window = gui.window

    time_and_measurement_dict = Manager().dict()
    window_open = Value('i', True)
    display_value = Value('f', 0)
    power_on = Value('i', False)
    Process(target=get_milli_volts, args=(power_on, display_value, time_and_measurement_dict,
                                          window_open,), daemon=True).start()
    while True:
        event, values = window.read(timeout=100)
        update_info_element(window, INFO_CURRENT, round(display_value.value, 3), 'mA')

        if event == sg.WIN_CLOSED:
            window_close_event(window_open=window_open, current_dict=time_and_measurement_dict, window=window,
                               digital_output_task=digital_output_task, list_of_tasks=list_of_tasks)
            break

        if event == 'INC-DATA':
            check_for_reference_spectrum(window=window)

        if event == 'START':
            start_fitting_event(window=window, gui=gui, digital_output_task=digital_output_task, power_on=power_on,
                                current_dict=time_and_measurement_dict)

        if event == 'STOP':
            stop_fitting_event(window=window, digital_output_task=digital_output_task, list_of_tasks=list_of_tasks,
                               pre_anod_index=shared.anod_starting_index, post_anod_index=shared.anod_ending_index)

        if event == 'SAVE':
            saving_event(window=window, current_dict=time_and_measurement_dict, window_open=window_open)

        if event == 'START-ELECTRICITY':
            start_electricity_event(window=window, power_on=power_on)

        if event == 'EMERGENCY_STOP_ELECTRICITY':
            emergency_stop_event(window=window, power_on=power_on)

import PySimpleGUI as sg

import RealTime_PAOO.common.shared as shared
from RealTime_PAOO.gui.main_gui.events import choose_data_dir_event, saving_event, start_fitting_event, stop_fitting_event
from RealTime_PAOO.gui.main_gui.main_layout import GraphicalInterface

if __name__ == '__main__':
    gui = GraphicalInterface()
    window = gui.window
    shared.correct_thickness = True
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'INC-DATA':
            choose_data_dir_event(window=window)

        if event == 'START':
            start_fitting_event(window=window, gui=gui, real_time=False)

        if event == 'STOP':
            stop_fitting_event(window=window, pre_anod_index=0, post_anod_index=len(shared.list_of_files) - 1)

        if event == 'SAVE':
            saving_event(window)

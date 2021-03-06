import PySimpleGUI as sg

import RealTime_PAAO.common.shared as shared
from RealTime_PAAO.gui.main_gui.events import (
    choose_data_dir_event,
    saving_event,
    start_fitting_event,
    stop_fitting_event,
)
from RealTime_PAAO.gui.main_gui.main_layout import GraphicalInterface


def main():
    gui = GraphicalInterface()
    window = gui.window
    window["START-ELECTRICITY"].update(disabled=True)

    shared.correct_thickness = True
    while True:
        event, _ = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "INC-DATA":
            choose_data_dir_event(window=window)

        if event == "START":
            start_fitting_event(window=window, gui=gui, real_time=False)

        if event == "STOP":
            stop_fitting_event(
                window=window,
                pre_anod_index=0,
                post_anod_index=len(shared.list_of_files) - 1,
                real_time=False,
            )

        if event == "SAVE":
            saving_event(window, {}, None)


if __name__ == "__main__":
    main()

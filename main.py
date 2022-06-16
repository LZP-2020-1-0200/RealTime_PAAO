from multiprocessing import freeze_support

import PySimpleGUI as sg

from PostFactumPAAO import main as post_factum
from RealTimePAAO import main as real_time


def main():
    program_to_launch = 0
    sg.theme("Reddit")
    layout = [
        [
            sg.B("RealTime PAAO", key="-REALTIME-", expand_x=True),
            sg.B("PostFactum PAAO", key="-POSTFACTUM-", expand_x=True),
        ],
    ]
    window = sg.Window("PAAO", layout=layout, finalize=True, font=("Verdana", "12"))

    while 1:
        event, _ = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "-REALTIME-":
            program_to_launch = 1
            break

        if event == "-POSTFACTUM-":
            program_to_launch = 2
            break

    window.close()

    if program_to_launch == 1:
        real_time()
    elif program_to_launch == 2:
        post_factum()


if __name__ == "__main__":
    freeze_support()
    main()

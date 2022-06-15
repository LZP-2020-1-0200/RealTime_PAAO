import sys

import PySimpleGUI as sg
from requests import get


def get_millivolts(power_on, display_value, time_and_measurement_dict, window_open):
    reference_time = 0
    while window_open.value:
        response_text = get("http://192.168.5.226/").text
        response_list = response_text.split(",")

        milliamps, timestamp = float(response_list[0]), float(response_list[1])

        display_value.value = round(milliamps, 2)

        if power_on.value:

            if not reference_time:
                reference_time = timestamp

            time_and_measurement_dict[timestamp - reference_time] = milliamps


def stop_power():
    get("http://192.168.5.226/stop")


def start_power():
    get("http://192.168.5.226/start")


def check_server_status():
    response = get("http://192.168.5.226/")
    if response.status_code != 200:
        sg.popup_error("Microcontroller not found", "Closing application...")
        sys.exit(1)

import sys

import PySimpleGUI as sg
from requests import exceptions, get


def get_millivolts(power_on, display_value, time_and_measurement_dict, window_open):
    reference_time = 0
    while window_open.value:
        response = get("http://192.168.5.226/")

        if response.status_code != 200:
            continue

        response_text = response.text
        response_list = response_text.split(",")

        milliamps, timestamp = float(response_list[0]), float(response_list[1])

        display_value.value = round(milliamps, 2)

        if not power_on.value:
            continue

        if reference_time == 0:
            reference_time = timestamp

        time_and_measurement_dict[timestamp - reference_time] = milliamps


def stop_power():
    get("http://192.168.5.226/stop")


def start_power():
    get("http://192.168.5.226/start")


def check_server_status():

    try:
        get("http://192.168.5.226/", timeout=5)
    except exceptions.RequestException as e:
        sg.popup_error(e, "Closing application...")
        sys.exit(1)
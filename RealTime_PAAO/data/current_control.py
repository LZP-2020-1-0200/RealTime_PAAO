import json
import sys
import time
from ipaddress import ip_address

import PySimpleGUI as sg
from requests import exceptions, get

with open("config.json") as file:
    data = json.load(file)
    ip_address = "http://" + data["Arduino IP"]


def get_millivolts(power_on, display_value, time_and_measurement_dict, window_open):
    reference_time = 0
    ip_address_ = ip_address
    while window_open.value:
        response = get(ip_address_)

        if response.status_code != 200:
            continue

        response_json: dict[str, dict[str, list[float]]] = response.json()

        if not response_json:
            time.sleep(0.05)
            continue

        for key in response_json:
            timestamp, milli_amperes = response_json[key]["data"]
            timestamp /= 1000

            if reference_time == 0 and power_on.value:
                reference_time = timestamp

            if reference_time and power_on.value:
                time_and_measurement_dict[timestamp - reference_time] = milli_amperes

        display_value.value = round(milli_amperes, 2)


def stop_power():
    get(f"{ip_address}/off")


def start_power():
    get(f"{ip_address}/on")


def check_server_status():
    try:
        get(ip_address, timeout=5)
        get(f"{ip_address}/off")
    except exceptions.RequestException as e:
        sg.popup_error(e, "Closing application...")
        sys.exit(1)

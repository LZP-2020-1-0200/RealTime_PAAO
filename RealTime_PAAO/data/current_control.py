import json
import sys
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

import random
import sys
import time
from datetime import datetime

from RealTime_PAOO.common.constants import NI_VOLTAGE_TO_MA_COEFFICIENT
from RealTime_PAOO.common.paths import log_file

import nidaqmx
import nidaqmx.system
import PySimpleGUI as sg


def get_ni_device_name():
    system = nidaqmx.system.System.local()
    if system.devices:
        return system.devices[0].name


def get_milli_volts(power_on, display_value, time_and_measurment_dict, window_open):
    reference_time = 0
    with nidaqmx.Task() as read_voltage_task:
        read_voltage_task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=-0.01, max_val=0.01)
        while window_open.value:
            try:
                milli_voltage = (read_voltage_task.read() * 1000) / NI_VOLTAGE_TO_MA_COEFFICIENT
            except:
                with open(log_file, 'a') as f:
                    f.write(f'\nFailed to read voltage at: {datetime.now().strftime("%H:%M:%S.%f")[:-3]}')
                continue

            display_value.value = round(milli_voltage, 3)

            if reference_time == 0 and power_on.value:
                reference_time = time.time()

            if power_on:
                time_and_measurment_dict[time.time() - reference_time] = milli_voltage


def get_mili_volts_test(power_on, display_value, time_and_measurment_dict, window_open):
    reference_time = 0
    while window_open.value:
        try:
            milli_voltage = random.random()
        except:
            with open(log_file, 'a') as f:
                f.write(f'\nFailed to read voltage at: {datetime.now().strftime("%H:%M:%S.%f")[:-3]}')
            continue

        display_value.value = round(milli_voltage, 3)

        if power_on.value:
            if not reference_time:
                reference_time = time.time()
            time_and_measurment_dict[time.time() - reference_time] = milli_voltage

        time.sleep(0.02)


def ni_stop_the_power(digital_output_task):
    # reversed
    digital_output_task.write(True)


def close_all_tasks(list_of_tasks):
    for task in list_of_tasks:
        task.close()


def initialize_national_instruments():
    digital_output_task, list_of_tasks = None, None
    # name = get_ni_device_name()
    # if name:
    #     digital_output_task = nidaqmx.Task()
    #     digital_output_task.do_channels.add_do_chan(f"{name}/port1/line4")
    #     digital_output_task.write(True)
    #     list_of_tasks = [digital_output_task]
    # else:
    #     sg.popup_error('Error', 'No National instruments device found', 'Closing application...')
    #     sys.exit(1)
    return digital_output_task, list_of_tasks

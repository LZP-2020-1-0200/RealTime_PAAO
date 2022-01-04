import random
import sys
import time
from datetime import datetime
import nidaqmx
import nidaqmx.system


def get_ni_device_name():
    system = nidaqmx.system.System.local()
    if system.devices:
        return system.devices[0].name
    return ''


# def get_milli_volts(task_name,log_file):
#     try:
#         voltage = task_name.read()
#     except:
#         with open(log_file, 'a') as f:
#             f.write(f'\nFailed to read voltage at: {datetime.now().strftime("%H:%M:%S.%f")[:-3]}')
#         return
#     return voltage * 1000  # volts to milli-volts


def get_milli_volts(task_name,log_file,power_on,display_value,time_and_measurment_dict):
    i = 0
    while True:
        if power_on.value:
            try:
                # mili_voltage = task_name.read()*1000 # volts to milli-volts
                milli_voltage = random.random()
                display_value.value = milli_voltage
            except:
                with open(log_file, 'a') as f:
                    f.write(f'\nFailed to read voltage at: {datetime.now().strftime("%H:%M:%S.%f")[:-3]}')
        else:
            try:
                # mili_voltage = task_name.read()*1000 # volts to milli-volts
                milli_voltage = random.random()
                if i == 0:
                    reference = time.time()

                time_and_measurment_dict[time.time()-reference] = milli_voltage
                i += 1
            except:
                with open(log_file, 'a') as f:
                    f.write(f'\nFailed to read voltage at: {datetime.now().strftime("%H:%M:%S.%f")[:-3]}')



def reset_tasks():
    # testing
    # create_voltage_task.write(0, auto_start=True)
    # digital_output_task.write(False)
    # real life
    digital_output_task.write(True)


def close_all_tasks():
    for task in list_of_tasks:
        task.close()


name = get_ni_device_name()
if name:
    # only for testing
    # create_voltage_task = nidaqmx.Task()
    # create_voltage_task.ao_channels.add_ao_voltage_chan(f"{name}/ao0", min_val=0, max_val=1)
    # create_voltage_task.write(0, auto_start=True)

    read_voltage_task = nidaqmx.Task()
    read_voltage_task.ai_channels.add_ai_voltage_chan(f"{name}/ai0", min_val=-0.01, max_val=0.01)

    digital_output_task = nidaqmx.Task()
    digital_output_task.do_channels.add_do_chan(f"{name}/port1/line4")

    # testing
    # digital_output_task.write(False)

    # real life
    digital_output_task.write(True)

    # list_of_tasks = [create_voltage_task, read_voltage_task, digital_output_task]
    list_of_tasks = [read_voltage_task, digital_output_task]

else:
    sys.exit('No National instruments device connected! Try connecting it first and then launch program again')

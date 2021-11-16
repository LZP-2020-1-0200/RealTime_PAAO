import sys
import nidaqmx
import nidaqmx.system


def get_ni_device_name():
    system = nidaqmx.system.System.local()
    if system.devices:
        return system.devices[0].name
    return ''


def get_voltage(read_task):
    return read_task.read()


def reset_tasks():
    create_voltage_task.write(0, auto_start=True)
    digital_output_task.write(False)


def close_all_tasks():
    for task in list_of_tasks:
        task.close()


name = get_ni_device_name()
if name:
    create_voltage_task = nidaqmx.Task()
    create_voltage_task.ao_channels.add_ao_voltage_chan(f"{name}/ao0", min_val=0, max_val=3.2)
    create_voltage_task.write(0, auto_start=True)

    read_voltage_task = nidaqmx.Task()
    read_voltage_task.ai_channels.add_ai_voltage_chan(f"{name}/ai0")

    digital_output_task = nidaqmx.Task()
    digital_output_task.do_channels.add_do_chan(f"{name}/port0/line14")
    digital_output_task.write(False)

    list_of_tasks = [create_voltage_task, read_voltage_task, digital_output_task]

else:
    sys.exit('No National instruments device connected! Try connecting it first and then launch program again')


from scipy.optimize import curve_fit
from functions import (get_spectra_filename, interpolate,
                       split_to_arrays)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib import pyplot as plt
import serial.tools.list_ports
import serial
import PySimpleGUI as sg
import pandas as pd
import numpy as np
from pathlib import Path
import time
import threading




def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def multilayer(x: np.array, thickness: float, normalization: float):
    M_ = np.full((len(x), 2, 2), [[1, 0], [0, 1]])
    tau = 2 * ntilde[0] / (ntilde[0] + ntilde[1])
    rho = (ntilde[0] - ntilde[1]) / (ntilde[0] + ntilde[1])
    T = np.array([[np.ones(len(x)), rho], [rho, np.ones(len(x))]]) / tau
    M = M_ @ T.T
    k = ntilde[1] * 2 * np.pi / x
    P = np.array([[np.exp(j * k * thickness), np.zeros(len(x))],
                  [np.zeros(len(x)), np.exp(-j * k * thickness)]])
    M = M @ P.T
    Ef = np.array([[np.ones(len(x))], [(ntilde[1] - ntilde[2]) /
                                       (ntilde[1] + ntilde[2])]]).T.reshape(len(x), 2, 1)
    E_0 = M @ Ef
    return (abs(E_0[0:len(x), 1] / E_0[0:len(x), 0]) ** 2)[:, 0] * normalization


def clear_axis(ax, x_from, x_to, y_from, y_to):
    ax.cla()
    ax.grid()
    ax.set_xlim(x_from, x_to)
    ax.set_ylim(y_from, y_to)


def set_plot_labels(ax, x_label, y_label):
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)


def plotting():
    global stop
    while not stop:
        global i, real_data, fitted_values, thickness_history, current_file
        try:
            clear_axis(ax, 0, 350, 80, desired_thickness + 20)
            clear_axis(ax2, lambda_range[0], lambda_range[-1], 0.75, 0.95)
            # Get data for plotting
            thickness_history_plotting = np.array(thickness_history)[:, 0]
            fitted_data = multilayer(lambda_range, *fitted_values)
            # Plot data
            ax.plot(anodizing_time[:i - 1], thickness_history_plotting)
            ax2.plot(lambda_range, real_data, lambda_range, fitted_data)

            set_plot_labels(ax, 'Time (s)', 'Thickness (nm)')
            set_plot_labels(ax2, 'Wavelength (nm)', 'Reflection (a.u.)')

            ax2.set_xticks(np.arange(480, 820, 40))
            ax2.set_yticks(np.arange(0.75, 1.0, 0.05))

            anodizing_time_title = 'Thickness:{}$nm$  Time:{}$s$'.format(str((round(fitted_values[0], 3))),
                                                                         str((round(anodizing_time[i], 3))))
            ax.set_title(anodizing_time_title)

            ax2.set_title(current_file)

            fig_agg.draw()
            fig_agg2.draw()

        except Exception as e:
            time.sleep(0.166)


def save_plots():
    global real_data_history, fitted_history, save_path
    for i, (x, y) in enumerate(zip(real_data_history, fitted_history)):
        print(i, x, y)
        plt.clf()
        plt.plot(lambda_range, x, lambda_range, y)
        plt.savefig(save_path / (str(i + 1) + '.png'))


def fitting():
    global i, real_data, fitted_values, thickness_history, stop, current_file, finish, fitted_history

    t1 = threading.Thread(target=plotting)
    t1.daemon = True
    t1.start()

    fitted_history = []
    while fitted_values[0] < float(values['DESIRED-THICK']) and not stop:

        next_file = get_spectra_filename(i + 1)
        current_file = get_spectra_filename(i)
        if (data_folder / next_file).is_file():
            # Every fifth file turn on red led
            if i % 5 == 0:
                arduino.write(bytes('0', 'utf-8'))
                window['START'].update(text='Working...')

            # Read new file
            spectrum_from_file = pd.read_csv(data_folder / current_file, delimiter='\t', skiprows=skip_lines,
                                             dtype=np.double, names=["Wavelength", "Intensity"], encoding='utf-8')
            # Interpolate with new x axis
            intensity_spectrum = interpolate(spectrum_from_file["Wavelength"], spectrum_from_file["Intensity"],
                                             lambda_range)
            # Get real data
            real_data = (intensity_spectrum / reference_spectrum) * R0
            # Append real data to list
            real_data_history.append(real_data)
            # Curve fit
            fitted_values, _ = curve_fit(multilayer, lambda_range, real_data, p0=fitted_values,
                                         bounds=((fitted_values[0], 0.9), (fitted_values[0] + 20, 1.1)))

            fitted_history.append(multilayer(lambda_range, *fitted_values))
            # Append fitted values to list
            thickness_history.append(np.round(fitted_values, 3))
            # Every fifth file turn off red led
            if i % 5 == 0:
                arduino.write(bytes('3', 'utf-8'))
            # Increment
            i += 1
    # If while loop is interupted check if finish condition is met
    if desired_thickness - fitted_values[0] < 5:
        window['PAUSE'].update(disabled=True)
        window['START'].update(
            disabled=True, text='Done', button_color='green')
        # Turn on blue led
        arduino.write(bytes('1', 'utf-8'))
        finish = True
    # save_plots()


def update_window_color(key, color):
    window[key].update(text_color=color)


def update_validation_image(key, state):
    image = good_image if state else bad_image
    window[key].update(source=image)


def get_all_ports():
    ports = serial.tools.list_ports.comports()
    return ports


def connect_arduino(ports, description):
    for port, desc, hwid in ports:
        if description in desc:
            por = port
            return serial.Serial(port=por, baudrate=9600, timeout=0.1)


# Starting global variables
good_image, bad_image = "good.png", "bad.png"
lambda_range = np.arange(480, 800 + 1)
j = complex(0, 1)
all_ports = get_all_ports()
i = 1
real_data = []
real_data_history = []
fitted_values = [90, 1]
thickness_history = []
fitted_history = []
current_file = ''
save_path = ''
# lines to skip when read spectrum files
skip_lines = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
              10, 11, 12, 13, 14, 15, 16, 3665, 3666]
# Validation booleans
correct_thickness, correct_time_int = False, False
correct_ref_file, correct_folder = False, False
arduino_connected = False
ref_spectrum_path, data_folder, time_interval = None, None, None
finish = False
#
path_to_refractive_info = Path("Refractive_info/")

# M. Daimon and A. Masumura. Measurement of the refractive index of distilled water from the near-infrared region
# to the ultraviolet region, Appl. Opt. 46, 3811-3820 (2007)
water_data = np.genfromtxt(path_to_refractive_info /
                           "Water.txt", delimiter='\t', encoding='utf-8')
nk_water_from_data = split_to_arrays(water_data, 1e3)
nk_water = interpolate(*nk_water_from_data, lambda_range)

# AL203 refractive index
nk_al203 = np.full(len(nk_water), 1.65)

# A. D. Rakić, A. B. Djurišic, J. M. Elazar, and M. L. Majewski. Optical properties of metallic films for
# vertical-cavity optoelectronic devices, Appl. Opt. 37, 5271-5283 (1998)
al_data = np.genfromtxt(path_to_refractive_info / "Rakic-BB.yml.txt", delimiter=' ', skip_header=9, skip_footer=3,
                        encoding='utf-8')
nk_al_from_data = split_to_arrays(al_data, 1e3)
nk_al = interpolate(*nk_al_from_data, lambda_range)

# Array of arrays with all refractive indexes
ntilde = np.array([nk_water, nk_al203, nk_al])
# Zero thickness simulation
R0 = multilayer(lambda_range, 0, 1)

# Window layout customization
text_font = ('Verdana', 12)
button_font = ('Verdana', 14)

sg.theme('Reddit')

col1 = sg.Canvas(key='-CANVAS-', expand_y=True, expand_x=True)
col2 = sg.Canvas(key='-CANVAS2-', expand_y=True, expand_x=True)

canvas_frame1 = sg.Frame(layout=[[col1]], title='', element_justification='top', pad=0, expand_y=True, expand_x=True,
                         border_width=0)
canvas_frame2 = sg.Frame(layout=[[col2]], title='', element_justification='top', expand_y=True, expand_x=True,
                         border_width=0)

canvas_layout = sg.Frame(layout=[[canvas_frame1, canvas_frame2]], title='',
                         expand_y=True, expand_x=True, border_width=4)

layout = [[sg.Text('Choose COM Port:', font=text_font, s=25),
           sg.Combo([port.description for port in all_ports], font=(
               'Verdana', 12), key='ARDUINO', enable_events=True, s=(25, 2)), sg.Image(bad_image, key='COM-PORT-IMG')],
          [sg.Text('Desired Thickness (nm):', font=text_font, s=25),
           sg.Input('', key='DESIRED-THICK', s=(12, 2), enable_events=True, justification='c',
                    font=text_font,
                    pad=((5, 9), (0, 0))),
           sg.Image(bad_image, key='DESIRED-THICK-IMG')],
          [sg.Text('Time Interval (ms):', font=text_font, s=25),
           sg.Input('', key='TIME-INTERVAL', enable_events=True, s=12, font=text_font, justification='c',
                    pad=((5, 9), (0, 0))),
           sg.Image(bad_image, key='TIME-INTERVAL-IMG')],
          [sg.Text('Reference spectrum:', font=text_font, s=25),
           sg.Button('Choose file', key='REF-SPECTRUM',
                     font=text_font, s=12),
           sg.Image(bad_image, key='REF-SPECTRUM-IMG')],
          [sg.Text('Folder with data:', font=text_font, s=25),
           sg.Button('Choose folder', key='INC-DATA',
                     font=text_font, s=12),
           sg.Image(bad_image, key='INC-DATA-IMG')],
          [sg.Button('Start', key='START', font=button_font,
                     expand_x=True, disabled_button_color='white')],
          [sg.Button('Pause', key='PAUSE', expand_x=True, font=button_font, disabled=True)]]

input_layout = sg.Frame(layout=layout, title='',
                        expand_x=True, element_justification='left', expand_y=True)

save_layout = [[sg.Text('Realtime fitness correction', justification='c', expand_x=True, font=text_font)],
               [sg.Button('+10nm', expand_x=True,
                          key='+10', font=button_font, disabled=True)],
               [sg.Button('-10nm', expand_x=True, key='-10', font=button_font, disabled=True)
                ],[sg.Button('Save plots and Exit', key='SAVE-PLOTS',font=button_font,expand_x=True,expand_y=True)]]

save_layout = sg.Frame(layout=save_layout, title='',
                       expand_y=True, expand_x=True, font=button_font)

final_layout = [[canvas_layout], [input_layout, save_layout]]

window = sg.Window('Realtime_PAOO', final_layout, finalize=True,
                   resizable=True, auto_size_text=True, debugger_enabled=True)

# Canvas drwaing
canvas_elem = window['-CANVAS-']
canvas_elem2 = window['-CANVAS2-']

canvas = canvas_elem.TKCanvas
canvas2 = canvas_elem2.TKCanvas

fig, ax = plt.subplots(figsize=(5, 4))
fig2, ax2 = plt.subplots(figsize=(5, 4))

ax.grid(True)
ax2.grid(True)

ax.set_xlabel('Time (s)')
ax.set_ylabel('Thickness (nm)')

ax2.set_xlabel('Wavelength (nm)')
ax2.set_ylabel('Reflection (a.u.)')

fig_agg = draw_figure(canvas, fig)
fig_agg2 = draw_figure(canvas2, fig2)

# Main loop
while True:

    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == 'DESIRED-THICK':
        try:
            desired_thickness = np.double(values['DESIRED-THICK'])
            if desired_thickness < 100:
                raise ValueError('Thickness must be at least 100nm!')
            correct_thickness = True
        except ValueError as error:
            correct_thickness = False
        update_validation_image('DESIRED-THICK-IMG', correct_thickness)

    if event == 'TIME-INTERVAL':
        try:
            time_interval = np.double(values['TIME-INTERVAL'])
            if time_interval < 50:
                raise ValueError('Time interval must be at least 50ms!')
            time_interval /= 1e3
            anodizing_time = np.arange(0, time_interval * 10000, time_interval)
            correct_time_int = True
        except ValueError:
            correct_time_int = False
        update_validation_image('TIME-INTERVAL-IMG', correct_time_int)

    if event == 'REF-SPECTRUM':
        ref_spectrum_path = Path(sg.popup_get_file(
            '', no_window=True, file_types=(("Text files", ".txt"),)))

        if ref_spectrum_path.name == 'ref_spektrs.txt':
            reference_spectrum_from_file = np.genfromtxt(ref_spectrum_path, delimiter='\t', skip_header=17,
                                                         skip_footer=1, encoding='utf-8')
            reference_spectrum_data = split_to_arrays(
                reference_spectrum_from_file)
            reference_spectrum = interpolate(
                *reference_spectrum_data, lambda_range)
            correct_ref_file = True
        elif ref_spectrum_path.name:
            sg.popup_error(
                'You must choose file ref_spektrs.txt', title='Error')
            correct_ref_file = False
        else:
            sg.popup_error('You didnt choose anything!', title='Error')
            correct_ref_file = False
        update_validation_image('REF-SPECTRUM-IMG', correct_ref_file)

    if event == 'INC-DATA':
        data_folder = Path(sg.popup_get_folder('', no_window=True))
        if data_folder.name:
            correct_folder = True
        else:
            sg.popup_error('Data folder was not chosen', title='Error')
            correct_folder = False
        update_validation_image('INC-DATA-IMG', correct_folder)

    if event == 'START':
        if correct_thickness and correct_time_int and correct_ref_file and correct_folder and arduino_connected:
            stop = False
            window.perform_long_operation(lambda: fitting(), '-END KEY-')
            window['START'].update(text='Waiting for files...')
            window['START'].update(disabled=True)
            window['PAUSE'].update(disabled=False)

            window['DESIRED-THICK'].update(disabled=True)
            window['TIME-INTERVAL'].update(disabled=True)
            window['REF-SPECTRUM'].update(disabled=True)
            window['INC-DATA'].update(disabled=True)
            window['ARDUINO'].update(disabled=True)
            window['+10'].update(disabled=False)
            window['-10'].update(disabled=False)

        else:
            sg.popup('Check your inputs', title='Warning')

    if event == 'PAUSE':
        window['START'].update(text='Start')
        window['START'].update(disabled=False)
        window['PAUSE'].update(disabled=True)
        stop = True
        window['DESIRED-THICK'].update(disabled=False)
        window['TIME-INTERVAL'].update(disabled=False)
        window['REF-SPECTRUM'].update(disabled=False)
        window['INC-DATA'].update(disabled=False)
        window['ARDUINO'].update(disabled=False)
        window['+10'].update(disabled=True)
        window['-10'].update(disabled=True)

    if event == '+10':
        fitted_values[0] += 10

    if event == '-10':
        fitted_values[0] -= 10

    if event == 'ARDUINO':
        try:
            arduino = connect_arduino(all_ports, values['ARDUINO'])
            arduino.write(bytes('2', 'utf-8'))
            arduino.write(bytes('3', 'utf-8'))
            arduino_connected = True
        except:
            arduino_connected = False
        update_validation_image('COM-PORT-IMG', arduino_connected)
    if event == 'SAVE-PLOTS':
        save_path = Path(sg.popup_get_folder('', no_window=True))
        save_plots()

window.close()

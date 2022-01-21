import csv
import re
import sys

import PySimpleGUI as sg

from RealTime_PAAO.common import paths, shared
from RealTime_PAAO.data.directories import make_folder

dictionary_with_units = {
    'DATE'             : '',
    'TIME'             : '',
    'DESIRED-THICKNESS': 'nm',
    'TEMPERATURE'      : '°C',
    'VOLTAGE'          : 'V',
    'SOLUTION'         : '',
    'MATERIAL'         : '',
    'COMMENT'          : ''
}


def begin_event_loop(gui):
    while True:
        event, values = gui.window.read(timeout=100)

        if event == sg.WIN_CLOSED:
            sys.exit(-1)

        if event == 'SUBMIT':
            try:
                shared.desired_thickness = int(values['DESIRED-THICKNESS'].strip())
                int(values['VOLTAGE'].strip())
                int(values['TEMPERATURE'].strip())
                shared.correct_thickness = True
            except:
                sg.popup_error('Thickness, voltage and temperature must be set and must be an integer', title='Input '
                                                                                                              'error')
                shared.correct_thickness = False
                continue

            new_values_wtih_comment = [x.strip().capitalize() + y for (x, y) in zip(values.values(),
                                                                                    dictionary_with_units.values())
                                       if x]
            shared.filename = [b.strip().capitalize() + d for (a, b), (c, d) in zip(values.items(),
                                                                                    dictionary_with_units.items()) if
                               b and a != 'COMMENT']
            shared.filename = " ".join(shared.filename)
            shared.filename = shared.filename.replace(':','꞉')
            shared.filename = re.sub(' +', ' ', shared.filename)

            paths.path_to_data_folder = paths.path_to_desktop / shared.filename
            paths.path_to_original_folder = make_folder(paths.path_to_data_folder, 'Originals')
            paths.path_to_organized_folder = make_folder(paths.path_to_data_folder, 'Organized files')

            paths.path_to_pre_anod_folder = make_folder(paths.path_to_organized_folder, '1. Pre anodizing spectrum')
            paths.path_to_anod_folder = make_folder(paths.path_to_organized_folder, '2. Anodizing spectrum')
            paths.path_to_post_anod_folder = make_folder(paths.path_to_organized_folder, '3. Post anodizing spectrum')
            paths.path_to_fitted_plot_folder = make_folder(paths.path_to_organized_folder, '4. Anodizing Plots')
            paths.path_to_fitted_data_folder = make_folder(paths.path_to_organized_folder, '5. Anodizing Data')

            paths.anodization_parameters = paths.path_to_organized_folder / 'Anodization_parameters.txt'
            with open(paths.anodization_parameters, 'w', newline='') as file:
                writer = csv.writer(file, delimiter=':')
                for x, y in zip(values.keys(), new_values_wtih_comment):
                    writer.writerow([x, y])

            break

    gui.window.close()

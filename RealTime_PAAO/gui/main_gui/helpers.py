import time

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from RealTime_PAAO.common import shared
from RealTime_PAAO.common.paths import path_to_bad_image, path_to_good_image


def validation_check(window_with_key, state):
    image = path_to_good_image if state else path_to_bad_image
    window_with_key.update(source=image)


def update_info_element(window, element, new_value, units=''):
    window[element].update(str(new_value) + ' ' + units)


def enable_or_disable_power_button(window):
    if window['START-ELECTRICITY'].Widget['state'] == 'disabled':
        window['EMERGENCY_STOP_ELECTRICITY'].update(disabled=True)
        window['START-ELECTRICITY'].update(disabled=False)
    else:
        window['START-ELECTRICITY'].update(disabled=True)
        window['EMERGENCY_STOP_ELECTRICITY'].update(disabled=False)


def disable_buttons(window):
    window['START'].update(disabled=True)
    window['STOP'].update(disabled=False)
    window['SAVE'].update(disabled=True)
    # window['DESIRED-THICK'].update(disabled=True)
    window['INC-DATA'].update(disabled=True)


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def update_zipping(window):
    i = 0
    list_of_texts = ['Zipping files', 'Zipping files.', 'Zipping files..', 'Zipping files...']
    while shared.zipper_animation:
        if i == 4:
            i = 0
        window['START'].update(text=list_of_texts[i])
        time.sleep(0.8)
        i += 1

def update_uploading(window):
    i = 0
    list_of_texts = ['Uploading to Zenodo', 'Uploading to Zenodo.', 'Uploading to Zenodo..', 'Uploading to Zenodo...']
    while shared.uploader_animation:
        if i == 4:
            i = 0
        window['START'].update(text=list_of_texts[i])
        time.sleep(0.8)
        i += 1

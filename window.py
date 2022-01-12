import PySimpleGUI as sg
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

TEXT_FONT = ('Verdana', 12)
BUTTON_FONT = ('Verdana', 14)
BAD_IMAGE = "assets\\bad.png"
GOOD_IMAGE = "assets\\good.png"
ICON = 'assets\\icon2.ico'


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def clear_axis(ax, x_from, x_to, y_from, y_to):
    ax.cla()
    ax.grid()
    ax.set_xlim(x_from, x_to)
    ax.set_ylim(y_from, y_to)


def set_plot_labels(ax, x_label, y_label):
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)


def validation_check(window_with_key, state):
    image = GOOD_IMAGE if state else BAD_IMAGE
    window_with_key.update(source=image)


def update_info_element(window,element, new_value, units=''):
    window[element].update(str(new_value) + ' ' + units)

def enable_or_disable_power_button(window):

    if window['START-ELECTRICITY'].Widget['state'] == 'disabled':
        window['STOP-ELECTRICITY'].update(disabled=True)
        window['START-ELECTRICITY'].update(disabled=False)
    else:
        window['START-ELECTRICITY'].update(disabled=True)
        window['STOP-ELECTRICITY'].update(disabled=False)



class GraphicalInterface:

    def __init__(self):
        self.window = None
        self.fig_agg, self.fig_agg2 = None, None
        self.ax, self.ax2, self.ax3 = None, None, None
        self.fig, self.fig2 = None, None
        self.create_window()
        self.set_labels_lim_etc()

    def set_labels_lim_etc(self):
        self.ax.set_xlim(0, 300)
        self.ax.set_ylim(80, 300)
        self.ax.set_title('PAAO thickness and current dependence on anodization time', pad=15)
        self.ax.grid(True)
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Thickness (nm)')

        self.ax2.set_xlim(480, 800)
        self.ax2.set_ylim(0.70, 0.9)
        self.ax2.set_yticks(np.arange(0.7, 0.9, 0.05))
        self.ax2.set_xticks(np.arange(480, 801, 40))
        self.ax2.set_xlabel('Wavelength (nm)')
        self.ax2.set_ylabel('Reflection (a.u.)')
        self.ax2.set_title('Real and fitted spectrum', pad=15)
        self.ax2.grid(True)
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")

        self.ax3.set_ylim(-2, 10)
        self.ax3.set_ylabel('Current (mA)')

    def create_window(self):
        sg.theme('Reddit')

        col1 = sg.Canvas(key='-CANVAS-', expand_y=True, expand_x=True)
        col2 = sg.Canvas(key='-CANVAS2-', expand_y=True, expand_x=True)

        canvas_frame1 = sg.Frame(layout=[[col1]], title='', expand_y=True, expand_x=True, border_width=0)
        canvas_frame2 = sg.Frame(layout=[[col2]], title='', expand_y=True, expand_x=True, border_width=0)

        canvas_layout = sg.Frame(layout=[[canvas_frame1, canvas_frame2]], title='',
                                 expand_y=True, expand_x=True, border_width=2)

        info_layout = [
            [sg.Text('Info Panel', font=('Roboto', 14, 'bold'), expand_x=True, justification='center', p=(0, 15))],
            [sg.Text('Anodizing time:', font=TEXT_FONT, s=13), sg.Text('-', font=TEXT_FONT, key='ANOD-TIME')],
            [sg.Text('Thickness:', font=TEXT_FONT, s=13), sg.Text('-', font=TEXT_FONT, key='ANOD-THICK')],
            [sg.Text('Current:', font=TEXT_FONT, s=13), sg.Text('-', font=TEXT_FONT, key='ANOD-CURRENT')],
            [sg.Text('Standard Error:', font=TEXT_FONT, s=13), sg.Text('-', font=TEXT_FONT, key='ANOD-ERROR')],
            [sg.Text('File:', font=TEXT_FONT, s=13), sg.Text('-', font=TEXT_FONT, key='ANOD-FILE')]]

        input_layout = [
            # Desired thickness input
            [sg.Text('Desired Thickness (nm):', font=TEXT_FONT, s=25),
             sg.Input('', key='DESIRED-THICK', s=(14, 2), enable_events=True, justification='c', font=TEXT_FONT,
                      pad=((5, 9), (0, 0))),
             sg.Image(BAD_IMAGE, key='DESIRED-THICK-IMG')],

            # Directory with data picker
            [sg.Text('Data directory:', font=TEXT_FONT, s=25),
             sg.Button('Choose directory', key='INC-DATA', font=TEXT_FONT, s=14),
             sg.Image(BAD_IMAGE, key='INC-DATA-IMG')],

            # Start button
            [sg.Button('Start file reading', key='START', font=BUTTON_FONT, disabled_button_color='white', s=(36, 1))],

            # Electricity start button


            # Stop button
            [sg.Button('Stop', key='PAUSE', font=BUTTON_FONT, disabled=True, s=(36, 1))],

            # Exit and save button
            [sg.Button('Save plots and Exit', key='SAVE-PLOTS', font=BUTTON_FONT,
                       disabled=True, s=(36, 1))],
            [sg.Button('Power ON', key='START-ELECTRICITY', s=(17, 1), font=BUTTON_FONT, expand_x=True,
                       button_color='green'),
             sg.Button('Power OFF', key='STOP-ELECTRICITY', s=(17, 1), font=BUTTON_FONT, button_color='red',
                       disabled=True)]]

        a = sg.Frame(layout=input_layout, title='', expand_y=True)
        b = sg.Frame(layout=info_layout, title='', expand_y=True)

        input_layout = sg.Frame(layout=[[a, b]], title='', element_justification='center', expand_x=True)

        final_layout = [[canvas_layout], [input_layout]]

        self.window = sg.Window('Realtime_PAOO', final_layout, finalize=True, resizable=True, auto_size_text=True,
                                debugger_enabled=False, icon=ICON, titlebar_icon=ICON)

        # Canvas drawing
        canvas_elem = self.window['-CANVAS-']
        canvas_elem2 = self.window['-CANVAS2-']

        canvas = canvas_elem.TKCanvas
        canvas2 = canvas_elem2.TKCanvas

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.fig2, self.ax2 = plt.subplots(figsize=(6, 4))
        self.ax3 = self.ax.twinx()

        self.fig_agg = draw_figure(canvas, self.fig)
        self.fig_agg2 = draw_figure(canvas2, self.fig2)

    def disable_buttons(self):
        self.window['START'].update(disabled=True)
        self.window['PAUSE'].update(disabled=False)
        self.window['SAVE-PLOTS'].update(disabled=True)
        self.window['DESIRED-THICK'].update(disabled=True)
        self.window['INC-DATA'].update(disabled=True)

    def exit(self):
        self.window.close()



import PySimpleGUI as sg
# import serial.tools.list_ports
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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


def connect_arduino(ports, description):
    for port, desc, _ in ports:
        if description in desc:
            return serial.Serial(port=port, baudrate=9600, timeout=0.1)


def validation_check(window_with_key, state):
    image = "assets\\good.png" if state else "assets\\bad.png"
    window_with_key.update(source=image)


class GraphicalInterface:

    def __init__(self):
        # self.ports = serial.tools.list_ports.comports()
        self.window = None
        self.fig_agg, self.fig_agg2 = None, None
        self.ax, self.ax2, self.ax3 = None, None, None
        self.create_window()

    def create_window(self):
        text_font = ('Verdana', 12)
        button_font = ('Verdana', 14)
        bad_image = "assets\\bad.png"
        sg.theme('Reddit')

        col1 = sg.Canvas(key='-CANVAS-', expand_y=True, expand_x=True)
        col2 = sg.Canvas(key='-CANVAS2-', expand_y=True, expand_x=True)

        canvas_frame1 = sg.Frame(layout=[[col1]], title='', expand_y=True, expand_x=True, border_width=0)
        canvas_frame2 = sg.Frame(layout=[[col2]], title='', expand_y=True, expand_x=True, border_width=0)

        canvas_layout = sg.Frame(layout=[[canvas_frame1, canvas_frame2]], title='',
                                 expand_y=True, expand_x=True, border_width=2)

        layout = [
            # [sg.Text('Choose COM Port:', font=text_font, s=25),
            #  sg.Combo([port.description for port in self.ports], font=('Verdana', 12), key='ARDUINO',
            #           enable_events=True, s=(25, 2)),
            #  sg.Image(bad_image, key='COM-PORT-IMG')],

            # Desired thickness input
            [sg.Text('Desired Thickness (nm):', font=text_font, s=25),
             sg.Input('', key='DESIRED-THICK', s=(12, 2), enable_events=True, justification='c', font=text_font,
                      pad=((5, 9), (0, 0))),
             sg.Image(bad_image, key='DESIRED-THICK-IMG')],

            # Directory with data picker
            [sg.Text('Folder with data:', font=text_font, s=25),
             sg.Button('Choose folder', key='INC-DATA', font=text_font, s=12),
             sg.Image(bad_image, key='INC-DATA-IMG')],

            # Start button
            [sg.Button('Start', key='START', font=button_font, disabled_button_color='white', s=(36, 1))],

            # Stop button
            [sg.Button('Stop', key='PAUSE', font=button_font, disabled=True, s=(36, 1))],

            [sg.Button('Save plots and Exit', key='SAVE-PLOTS', font=button_font,
                       disabled=True, s=(36, 1))]]

        input_layout = sg.Frame(layout=layout, title='', element_justification='center', expand_x=True)

        final_layout = [[canvas_layout], [input_layout]]

        self.window = sg.Window('Realtime_PAOO', final_layout, finalize=True, resizable=True, auto_size_text=True,
                                debugger_enabled=False, icon='assets/icon2.ico', titlebar_icon='assets/icon2.ico',
                                element_justification='center')

        # Canvas drawing
        canvas_elem = self.window['-CANVAS-']
        canvas_elem2 = self.window['-CANVAS2-']

        canvas = canvas_elem.TKCanvas
        canvas2 = canvas_elem2.TKCanvas

        fig, self.ax = plt.subplots(figsize=(6, 4))
        fig2, self.ax2 = plt.subplots(figsize=(6, 4))
        self.ax3 = self.ax.twinx()

        self.ax.grid(True)
        self.ax2.grid(True)
        # self.ax3.grid(True)

        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Thickness (nm)')
        self.ax3.set_ylabel('Voltage (V)')

        self.ax2.set_xlabel('Wavelength (nm)')
        self.ax2.set_ylabel('Reflection (a.u.)')

        self.fig_agg = draw_figure(canvas, fig)
        self.fig_agg2 = draw_figure(canvas2, fig2)

        # plt.tight_layout()

    def disable_buttons(self):
        self.window['START'].update(disabled=True)
        self.window['PAUSE'].update(disabled=False)

        self.window['SAVE-PLOTS'].update(disabled=True)
        self.window['DESIRED-THICK'].update(disabled=True)
        self.window['INC-DATA'].update(disabled=True)
        # self.window['ARDUINO'].update(disabled=True)

    def exit(self):
        self.window.close()

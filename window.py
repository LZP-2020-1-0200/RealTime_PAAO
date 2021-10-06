import PySimpleGUI as sg
import serial.tools.list_ports
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


def update_validation_image(window_with_key, state):
    image = "assets\\good.png" if state else "assets\\bad.png"
    window_with_key.update(source=image)


class GraphicalInterface:

    def __init__(self, ports):
        self.ports = ports
        self.window = None
        self.fig_agg, self.fig_agg2 = None, None
        self.ax, self.ax2 = None, None
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
            # todo Com port Chooser does nothing at this moment
            [sg.Text('Choose COM Port:', font=text_font, s=25),
             sg.Combo([port.description for port in self.ports], font=('Verdana', 12), key='ARDUINO',
                      enable_events=True, s=(25, 2)),
             sg.Image(bad_image, key='COM-PORT-IMG')],
            # Desired thickness input
            [sg.Text('Desired Thickness (nm):', font=text_font, s=25),
             sg.Input('', key='DESIRED-THICK', s=(12, 2), enable_events=True, justification='c', font=text_font,
                      pad=((5, 9), (0, 0))),
             sg.Image(bad_image, key='DESIRED-THICK-IMG')],
            # Time interval input
            [sg.Text('Time Interval (ms):', font=text_font, s=25),
             sg.Input('', key='TIME-INTERVAL', enable_events=True, s=12, font=text_font, justification='c',
                      pad=((5, 9), (0, 0))),
             sg.Image(bad_image, key='TIME-INTERVAL-IMG')],
            # Reference spectrum input
            [sg.Text('Reference spectrum:', font=text_font, s=25),
             sg.Button('Choose file', key='REF-SPECTRUM', font=text_font, s=12),
             sg.Image(bad_image, key='REF-SPECTRUM-IMG')],
            # Directory with data picker
            [sg.Text('Folder with data:', font=text_font, s=25),
             sg.Button('Choose folder', key='INC-DATA', font=text_font, s=12),
             sg.Image(bad_image, key='INC-DATA-IMG')],
            # Start button
            [sg.Button('Start', key='START', font=button_font, expand_x=True, disabled_button_color='white')],
            # Stop button
            [sg.Button('Pause', key='PAUSE', expand_x=True, font=button_font, disabled=True)]]

        input_layout = sg.Frame(layout=layout, title='', element_justification='left', expand_y=True, expand_x=True)

        save_layout = [
            [sg.Text('Realtime fitness correction', justification='c', expand_x=True, font=text_font)],

            [sg.Button('+10nm', expand_x=True, key='+10', font=button_font, disabled=True)],

            [sg.Button('-10nm', expand_x=True, key='-10', font=button_font, disabled=True)],

            [sg.Button('Save plots and Exit', key='SAVE-PLOTS', font=button_font, expand_x=True, expand_y=True,
                       disabled=True)]]

        save_layout = sg.Frame(layout=save_layout, title='', expand_y=True, expand_x=True, font=button_font)

        final_layout = [[canvas_layout], [input_layout, save_layout]]

        self.window = sg.Window('Realtime_PAOO', final_layout, finalize=True, resizable=True, auto_size_text=True,
                                debugger_enabled=False, icon='icon.ico')

        # Canvas drawing
        canvas_elem = self.window['-CANVAS-']
        canvas_elem2 = self.window['-CANVAS2-']

        canvas = canvas_elem.TKCanvas
        canvas2 = canvas_elem2.TKCanvas

        fig, self.ax = plt.subplots(figsize=(5, 4))
        fig2, self.ax2 = plt.subplots(figsize=(5, 4))

        self.ax.grid(True)
        self.ax2.grid(True)

        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Thickness (nm)')

        self.ax2.set_xlabel('Wavelength (nm)')
        self.ax2.set_ylabel('Reflection (a.u.)')

        self.fig_agg = draw_figure(canvas, fig)
        self.fig_agg2 = draw_figure(canvas2, fig2)

    def disable_or_enable_buttons(self, condition):
        #self.window['START'].update(text='Waiting for files...')
        self.window['START'].update(disabled=condition)
        self.window['PAUSE'].update(disabled=not condition)

        self.window['SAVE-PLOTS'].update(disabled=condition)
        self.window['DESIRED-THICK'].update(disabled=condition)
        self.window['TIME-INTERVAL'].update(disabled=condition)
        self.window['REF-SPECTRUM'].update(disabled=condition)
        self.window['INC-DATA'].update(disabled=condition)
        self.window['ARDUINO'].update(disabled=condition)
        self.window['+10'].update(disabled=not condition)
        self.window['-10'].update(disabled=not condition)

    def exit(self):
        self.window.close()

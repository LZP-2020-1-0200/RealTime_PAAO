import PySimpleGUI as sg
from matplotlib import pyplot as plt

from RealTime_PAOO.common.constants import LAMBDA, PLOT_SIZE, THEORETICAL_THICKNESS, THEORETICAL_TIME, ZEROS
from RealTime_PAOO.common.paths import path_to_bad_image, path_to_title_icon
from RealTime_PAOO.gui.main_gui.plots import set_anodization_thickness_per_time_plot_labels, set_fitting_plot_labels
from RealTime_PAOO.gui.main_gui.helpers import draw_figure
from RealTime_PAOO.gui.fonts import button_font, info_layout_text_size, info_panel_title_font, text_font


class GraphicalInterface:

    def __init__(self):
        self.window = None
        self.fig_agg, self.fig_agg2 = None, None
        self.fig, self.ax = plt.subplots(figsize=PLOT_SIZE)
        self.fig2, self.ax2 = plt.subplots(figsize=PLOT_SIZE)
        self.ax3 = self.ax.twinx()
        self.create_window()
        set_anodization_thickness_per_time_plot_labels(self.ax, self.ax3)
        set_fitting_plot_labels(self.ax2)
        self.thickness_per_time_line = self.ax.plot([0], [0], color='tab:blue', label='Thickness')[0]
        self.theoretical = self.ax.plot(THEORETICAL_TIME, THEORETICAL_THICKNESS, color='b', ls=':',
                                        label='Theoretical')[0]
        self.current_per_time_line = self.ax3.plot([0], [0], color='orange', label='Current', alpha=0.7)[0]
        self.fitted_spectra_line = self.ax2.plot(LAMBDA, ZEROS, color='orange', label='Fitted', linewidth=2)[0]
        self.real_spectra_line = self.ax2.plot(LAMBDA, ZEROS, color='tab:blue', label='Real', alpha=0.8)[0]
        self.fig.legend(loc="upper left", bbox_to_anchor=(0, 1), bbox_transform=self.ax.transAxes)
        self.ax2.legend()

    def create_window(self):
        sg.theme('Reddit')

        col1 = sg.Canvas(key='-CANVAS-', expand_y=True, expand_x=True)
        col2 = sg.Canvas(key='-CANVAS2-', expand_y=True, expand_x=True)

        canvas_frame1 = sg.Frame(layout=[[col1]], title='', expand_y=True, expand_x=True, border_width=0)
        canvas_frame2 = sg.Frame(layout=[[col2]], title='', expand_y=True, expand_x=True, border_width=0)

        canvas_layout = sg.Frame(layout=[[canvas_frame1, canvas_frame2]], title='',
                                 expand_y=True, expand_x=True, border_width=2)

        info_layout = [
            [sg.Text('Info Panel', font=info_panel_title_font, expand_x=True, justification='center', p=(0, 15))],

            [sg.Text('Anodizing time:', font=text_font, s=info_layout_text_size),
             sg.Text('-', font=text_font, key='ANOD-TIME')],

            [sg.Text('Thickness:', font=text_font, s=info_layout_text_size),
             sg.Text('-', font=text_font, key='ANOD-THICK')],

            [sg.Text('Current:', font=text_font, s=info_layout_text_size),
             sg.Text('-', font=text_font, key='ANOD-CURRENT')],

            [sg.Text('Standard Error:', font=text_font, s=info_layout_text_size),
             sg.Text('-', font=text_font, key='ANOD-ERROR')],

            [sg.Text('File:', font=text_font, s=info_layout_text_size), sg.Text('-', font=text_font, key='ANOD-FILE')]]

        input_layout = [
            # Desired thickness input
            # [sg.Text('Desired Thickness (nm):', font=text_font, s=25),
            #  sg.Input('', key='DESIRED-THICK', s=(14, 2), enable_events=True, justification='c', font=text_font,
            #           pad=((5, 9), (0, 0))),
            #  sg.Image(path_to_bad_image, key='DESIRED-THICK-IMG')],

            # Directory with data picker
            [
             sg.Button('Check for reference spectrum', key='INC-DATA', font=button_font,expand_x=True),
             sg.Image(path_to_bad_image, key='INC-DATA-IMG')],

            # Start button
            [sg.Button('Start file reading', key='START', font=button_font, disabled_button_color='white', s=(36, 1))],

            # Electricity start button

            # Stop button
            [sg.Button('Stop', key='STOP', font=button_font, disabled=True, s=(36, 1))],

            # Exit and save button
            [sg.Button('Save plots', key='SAVE', font=button_font,
                       disabled=True, s=(36, 1))],
            [sg.Button('Power ON', key='START-ELECTRICITY', s=(17, 1), font=button_font, expand_x=True,
                       button_color='green'),
             sg.Button('Power OFF', key='EMERGENCY_STOP_ELECTRICITY', s=(17, 1), font=button_font, button_color='red',
                       disabled=True)]]

        a = sg.Frame(layout=input_layout, title='', expand_y=True)
        b = sg.Frame(layout=info_layout, title='', expand_y=True,s=(250,10))

        input_layout = sg.Frame(layout=[[a, b]], title='', element_justification='center', expand_x=True)

        final_layout = [[canvas_layout], [input_layout]]

        self.window = sg.Window('Realtime_PAOO', final_layout, finalize=True, resizable=True, auto_size_text=True,
                                debugger_enabled=False, icon=path_to_title_icon, titlebar_icon=path_to_title_icon)

        # Canvas drawing
        canvas = self.window['-CANVAS-'].TKCanvas
        canvas2 = self.window['-CANVAS2-'].TKCanvas

        self.fig_agg = draw_figure(canvas, self.fig)
        self.fig_agg2 = draw_figure(canvas2, self.fig2)

    def close_window(self):
        self.window.close()

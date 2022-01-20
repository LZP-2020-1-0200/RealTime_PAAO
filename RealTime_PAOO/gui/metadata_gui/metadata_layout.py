import PySimpleGUI as sg
from datetime import datetime
from RealTime_PAOO.common.paths import path_to_title_icon
from RealTime_PAOO.gui.fonts import button_font, text_font


class DescriptionGraphicalInterface:
    def __init__(self):
        self.window = None
        self.keys = []
        self.create_layout()


    def create_layout(self):


        today = datetime.today()
        sg.theme('Reddit')
        layout = [

            [sg.Text('Date:', font=text_font, s=25),
             sg.Input(today.strftime("%Y-%m-%d"), key='DATE', s=(14, 2), enable_events=True, justification='c',
                      font=text_font,
                      pad=((5, 9), (0, 0)),expand_x=True)],
            [sg.Text('Time:', font=text_font, s=25),
             sg.Input(today.strftime('%H:%M'), key='TIME', s=(14, 2), enable_events=True, justification='c',
                      font=text_font,
                      pad=((5, 9), (0, 0)),expand_x=True)],
            [sg.Text('Desired thickness (nm):', font=text_font, s=25),
             sg.Input('', key='DESIRED-THICKNESS', s=(14, 2), enable_events=True, justification='c', font=text_font,
                      pad=((5, 9), (0, 0)),expand_x=True)],
            [sg.Text('Temperature (°C):', font=text_font, s=25),
             sg.Input('', key='TEMPERATURE', s=(14, 2), enable_events=True, justification='c', font=text_font,
                      pad=((5, 9), (0, 0)),expand_x=True)],
            [sg.Text('Voltage (V):', font=text_font, s=25),
             sg.Input('', key='VOLTAGE', s=(14, 2), enable_events=True, justification='c', font=text_font,
                      pad=((5, 9), (0, 0)),expand_x=True)],
            [sg.Text('Solution:', font=text_font, s=25),
             sg.Input('', key='SOLUTION', s=(14, 2), enable_events=True, justification='c', font=text_font,
                      pad=((5, 9), (0, 0)),expand_x=True)],
            [sg.Text('Material:', font=text_font, s=25),
             sg.Input('', key='MATERIAL', s=(14, 2), enable_events=True, justification='c', font=text_font,
                      pad=((5, 9), (0, 0)),expand_x=True)],
            [sg.Text('Comment:', font=text_font, s=25),
             sg.Multiline('', key='COMMENT', s=(20, 4), enable_events=True, font=text_font,
                      pad=((5, 9), (0, 0)),expand_y=True,expand_x=True)],
            [sg.Button('Submit', key='SUBMIT', font=button_font,
                       disabled=False, expand_x=True)]

        ]

        self.window = sg.Window('Realtime_PAOO', layout, finalize=True, resizable=True, auto_size_text=True,
                                debugger_enabled=False, icon=path_to_title_icon, titlebar_icon=path_to_title_icon)

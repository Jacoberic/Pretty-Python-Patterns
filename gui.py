import gc
import math
from math import tau

import FreeSimpleGUI as sg
from loguru import logger

from utilities import Settings
from utilities_gui import FolderButton, theme, Icon, Loading, LED, FileButton, change_settings
from utilities_log import log_start

class Gui:
    def __init__(self, settings) -> None:
        self.closed = False
        self.settings = settings

        main_col = sg.Col([
            [sg.Input(key='file', expand_x=True), FileButton()],
            [sg.Button('hi', expand_x=True, expand_y=True)]
        ], expand_x=True, expand_y=True)

        logs_col = sg.Col([
            [sg.Output(key='out', expand_x=True, expand_y=True)],
            [sg.Input(key='log_input', s=(55,1), expand_x=True)]
        ], expand_x=True, expand_y=True, key='logs_col')

        layout = [
            [sg.Push(), Icon('settings'), Loading(key='loading')],
            [main_col, logs_col],
        ]

        #*Main window declaration
        self.window = sg.Window('Project', size=(6*theme.w, 6*theme.h), layout=layout, finalize=True, grab_anywhere=True)
        self.window['log_input'].bind('<Return>', '')
        self.window['log_input'].bind('<KP_Enter>', '')

    def update(self, timeout=10):
        if self.closed:
            return False
        else:
            #*Read the window
            self.event, self.values = self.window.read(timeout=timeout)
            
            if self.event == sg.WINDOW_CLOSED or self.event == 'close':
                self.close()
                return False
            else:
                #*Update things
                self.window['loading'].update()

                if self.event == 'log_input':
                    logger.info(self.window['log_input'].get())
                    self.window['log_input'].update('')

                if self.event == 'settings':
                    change_settings(self.settings)

                return True

    def close(self):
        self.window.close()
        self.window.layout = None
        self.window = None
        gc.collect()
        self.closed = True

if __name__ == '__main__':
    log_start('test')
    settings = Settings()
    gui = Gui(settings)
    while gui.update():
        if gui.event != '__TIMEOUT__':
            print(gui.event)

import gc
import math
from math import tau

import FreeSimpleGUI as sg
from loguru import logger

from utilities_gui import FolderButton, theme, Icon, Loading, LED, FileButton
from utilities_log import log_start

class Gui:
    def __init__(self) -> None:
        self.closed = False

        logs_col = sg.Col([
            [sg.Multiline(key='out', reroute_stdout=True, expand_x=True, expand_y=True, autoscroll=True, disabled=True)],
            [sg.Input(key='log_input', s=(55,1))]
        ], expand_y=True, key='logs_col')

        layout = [
            [sg.Push(), Loading(key='loading')],
            [logs_col],
        ]

        #*Main window declaration
        self.window = sg.Window('Project', layout=layout, finalize=True, grab_anywhere=True)
        self.window['log_input'].bind('<Return>', '')

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

                return True

    def close(self):
        self.window.close()
        self.window.layout = None
        self.window = None
        gc.collect()
        self.closed = True

if __name__ == '__main__':
    log_start('test')
    gui = Gui()
    while gui.update():
        if gui.event != '__TIMEOUT__':
            print(gui.event)

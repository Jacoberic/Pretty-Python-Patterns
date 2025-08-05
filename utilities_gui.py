from traceback import format_exc
import gc
import pickle
import time

from screeninfo import get_monitors
from loguru import logger
import FreeSimpleGUI as sg

from utilities import Timer

class Theme:
    def __init__(self) -> None:
        self.BLUE = '#3366cc'
        self.RED = '#cc3339'
        self.GREEN = '#33cc5a'
        self.PURPLE = '#8733cc'
        self.YELLOW = '#ccb433'
        self.CYAN = '#33b7cc'
        self.MAGENTA = '#cc338a'

        self.BLUEDARK = '#33363c'
        self.BLUEGRAY = '#43464c'
        self.BLUESILVER = '#c3c6cc'
        self.BLUEWHITE = '#d3d6dc'

        Jacob_Dark = {
            "BACKGROUND": self.BLUEDARK,
            "TEXT": self.BLUESILVER,
            "INPUT": self.BLUEGRAY,
            "TEXT_INPUT": self.BLUEWHITE,
            "SCROLL": self.BLUEDARK,
            "BUTTON": (self.BLUEWHITE, self.BLUEGRAY),
            "PROGRESS": (self.BLUEWHITE, self.BLUEGRAY),
            "BORDER": 1,
            "SLIDER_DEPTH": 1,
            "PROGRESS_DEPTH": 1,
        }

        sg.theme_add_new('Jacob Dark', Jacob_Dark)
        sg.theme('Jacob Dark')

        monitor = get_monitors()[0]
        self.width = monitor.width
        self.height = monitor.height
        self.w = self.width // 12
        self.h = self.height // 12

theme = Theme()

def unhandled_exception_popup(message=None):
    title = 'Error'
    traceback = format_exc()
    logger.exception(title)
    if message is None:
        choice, _ = sg.Window(title, [[sg.Multiline(traceback, size=(60,30))], [sg.Ok()]], disable_close=True).read(close=True)
    else:
        logger.error(message)
        choice, _ = sg.Window(title, [[sg.T(message)], [sg.Multiline(traceback, size=(60,30))], [sg.Ok()]], disable_close=True).read(close=True)

def popup(message):
    return True if sg.popup_ok_cancel(message) == 'OK' else False

class LoadingPopup:
    def __init__(self, message='') -> None:
        self.window = sg.Window('Loading', [[sg.T(message)]], disable_close=True, no_titlebar=True, location=(900,500))
        self.window.read(timeout=0)

    def close(self):
        self.window.close()

def change_settings(settings):
    settings_col = sg.Col([[sg.Text(text=key), sg.Input(default_text=settings._class_dict[key], key=key)] for key in settings._class_dict.keys()])
    layout = [
        [settings_col],
        [sg.Button('Save', key='_SAVE_'), sg.Button('Cancel', key='_CANCEL_')]
    ]

    window = sg.Window('Change Settings', layout=layout, finalize=True, grab_anywhere=True)

    while True:
        event, values = window.read(timeout=100)

        if event == sg.WINDOW_CLOSED or event == '_CANCEL_':
            window.close()
            window.layout = None
            window = None
            gc.collect()#Set windows to none and garbage collect to prevent errors with multi-threading and multiple windows.
            return False
        else:
            #?Show events for debugging
            # if event != '__TIMEOUT__':
                # print(self.event)

            #Update things
            if event == '_SAVE_':
                for key in settings._class_dict.keys():
                    settings.__setattr__(key, window[key].get())
                window.close()
                window.layout = None
                window = None
                gc.collect()#Set windows to none and garbage collect to prevent errors with multi-threading and multiple windows.
                return True

class BorderButton(sg.Frame):
    def __init__(
        self, button_text='', relief='groove', background_color=None, button_type=7, target=(None, None), tooltip=None, file_types=(('ALL Files', '*.* *'),), initial_folder=None, default_extension='', disabled=False, change_submits=False, 
        enable_events=False, image_filename=None, image_data=None, image_size=(None, None), image_subsample=None, image_source=None, border_width=None, size=(None, None), s=(None, None), 
        auto_size_button=None, button_color=None, disabled_button_color=None, highlight_colors=None, mouseover_colors=(None, None), use_ttk_buttons=None, font=None, bind_return_key=False, 
        focus=False, pad=None, p=None, key=None, k=None, right_click_menu=None, expand_x=False, expand_y=False, visible=True, metadata=None
    ):
        if key is None:
            button_key = 'button'
        else:
            button_key = key + '_button'
        if k is None:
            bk = 'button'
        else:
            bk = k + '_button'
        self.button = sg.Button(
            button_text, button_type, target, tooltip, file_types, initial_folder, default_extension, disabled, change_submits, 
            enable_events, image_filename, image_data, image_size, image_subsample, image_source, None, size, s, 
            auto_size_button, button_color, disabled_button_color, highlight_colors, mouseover_colors, use_ttk_buttons, font, bind_return_key, 
            focus, 0, 0, button_key, bk, right_click_menu, expand_x, expand_y, visible, metadata
        )
        
        super().__init__('', [[self.button]], pad=pad, p=p, border_width=border_width, relief=relief, background_color=background_color, key=key, k=k, expand_x=expand_x, expand_y=expand_y)

    def update(self, text=None, background_color=None, button_color=(None, None), disabled=None, image_data=None, image_filename=None, visible=None, image_subsample=None, disabled_button_color=(None, None), image_size=None):
        self.Widget.configure(background=background_color)
        return self.button.update(text, button_color, disabled, image_data, image_filename, visible, image_subsample, disabled_button_color, image_size)

class FolderButton(sg.Button):
    def __init__(
        self, tooltip=None, initial_folder=None,
        default_extension='', disabled=False, change_submits=False, enable_events=False,
        size=(None,None), s=(None,None), auto_size_button=None, button_color=(theme.BLUEDARK, theme.BLUEDARK), disabled_button_color=None,
        highlight_colors=None, mouseover_colors=(None,None), use_ttk_buttons=None, font=None, bind_return_key=False,
        focus=False, pad=None, p=None, key=None, k=None, right_click_menu=None, expand_x=False, expand_y=False, visible=True, metadata=None
    ):
        image_filename = f'_internal/folder.png'
        super().__init__(
            button_type=1, target=(555666777, -1), tooltip=tooltip, file_types=(('ALL files', '*.*'),), initial_folder=initial_folder,
            default_extension=default_extension, disabled=disabled, change_submits=change_submits, enable_events=enable_events,
            image_filename=image_filename, image_size=(20,20), image_subsample=1,
            border_width=0, size=size, s=s, auto_size_button=auto_size_button, button_color=button_color, disabled_button_color=disabled_button_color,
            highlight_colors=highlight_colors, mouseover_colors=mouseover_colors, use_ttk_buttons=use_ttk_buttons, font=font, bind_return_key=bind_return_key,
            focus=focus, pad=pad, p=p, key=key, k=k, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata
        )

class FileButton(sg.Button):
    def __init__(
        self, button_text='', tooltip=None, file_types=(('ALL files', '*.*'),), initial_folder=None,
        default_extension='', disabled=False, change_submits=False, enable_events=False,
        size=(None,None), s=(None,None), auto_size_button=None, button_color=(theme.BLUEDARK, theme.BLUEDARK), disabled_button_color=None,
        highlight_colors=None, mouseover_colors=(None,None), use_ttk_buttons=None, font=None, bind_return_key=False,
        focus=False, pad=None, p=None, key=None, k=None, right_click_menu=None, expand_x=False, expand_y=False, visible=True, metadata=None
    ):

        image_filename = f'_internal/file.png'
        super().__init__(
            button_text, button_type=2, target=(555666777, -1), tooltip=tooltip, file_types=file_types, initial_folder=initial_folder,
            default_extension=default_extension, disabled=disabled, change_submits=change_submits, enable_events=enable_events,
            image_filename=image_filename, image_size=(20,20), image_subsample=1,
            border_width=0, size=size, s=s, auto_size_button=auto_size_button, button_color=button_color, disabled_button_color=disabled_button_color,
            highlight_colors=highlight_colors, mouseover_colors=mouseover_colors, use_ttk_buttons=use_ttk_buttons, font=font, bind_return_key=bind_return_key,
            focus=focus, pad=pad, p=p, key=key, k=k, right_click_menu=right_click_menu, expand_x=expand_x, expand_y=expand_y, visible=visible, metadata=metadata
        )

class Icon(sg.Button):
    def __init__(self, icon_name=None, icon2_name=None, key=None, tooltip=None, right_click_menu=None, image_subsample=1, pad=None, p=None):

        self.icon_name = f'_internal/{icon_name}.png'
        self.icon2_name = f'_internal/{icon2_name}.png'
        self.current_icon = 1

        if key is None:
            key = icon_name

        super().__init__(
            button_text='', tooltip=tooltip,
            image_filename=self.icon_name, image_size=(20,20), image_subsample=image_subsample,
            border_width=0, button_color=(theme.BLUEDARK, theme.BLUEDARK),
            key=key, right_click_menu=right_click_menu, pad=pad, p=p
        )
    
    def toggle(self):
        if self.icon2_name is None:
            logger.warning('Second icon is not set')
        else:
            if self.current_icon == 1:
                self.update(image_filename=self.icon2_name)
                self.current_icon = 2
            else:
                self.update(image_filename=self.icon_name)
                self.current_icon = 1
        # super().__init__(source=self.icon_name, key=key)

class Collapsible(sg.Column):
    def __init__(self, layout, background_color=None, size=(None, None), s=(None, None), size_subsample_width=1, size_subsample_height=2, pad=None, p=None, scrollable=False, vertical_scroll_only=False, right_click_menu=None, key=None, k=None, visible=True, justification=None, element_justification=None, vertical_alignment=None, grab=None, expand_x=None, expand_y=None, metadata=None, sbar_trough_color=None, sbar_background_color=None, sbar_arrow_color=None, sbar_width=None, sbar_arrow_width=None, sbar_frame_color=None, sbar_relief=None):
        self.collapsed = not visible
        self.internal_column = sg.Column(layout, background_color, size, s, size_subsample_width, size_subsample_height, pad, p, scrollable, vertical_scroll_only, None, None, None, visible, justification, element_justification, vertical_alignment, grab, expand_x, expand_y, metadata, sbar_trough_color, sbar_background_color, sbar_arrow_color, sbar_width, sbar_arrow_width, sbar_frame_color, sbar_relief)
        collapsible_layout = [[self.internal_column, sg.Column([[]],pad=(0,0))]]
        super().__init__(collapsible_layout, background_color, (None, None), (None, None), 1, 2, None, None, False, False, right_click_menu, key, k, True, justification, element_justification, vertical_alignment, grab, expand_x, expand_y, None, sbar_trough_color, sbar_background_color, sbar_arrow_color, sbar_width, sbar_arrow_width, sbar_frame_color, sbar_relief)

    def collapse(self):
        self.internal_column.update(visible=False)
        self.collapsed = True

    def open(self):
        self.internal_column.update(visible=True)
        self.collapsed = False

    def toggle(self):
        self.internal_column.update(visible=self.collapsed)#if collapsed is true then toggle makes visible true
        self.collapsed = not self.collapsed

class LED(sg.Graph):
    def __init__(self, key=None, k=None, canvas_size=(20,20), graph_bottom_left=(-20, -20), graph_top_right=(20, 20), background_color=None, pad=(0,0), p=None, change_submits=False, drag_submits=False, enable_events=False, motion_events=False, tooltip=None, right_click_menu=None, expand_x=False, expand_y=False, visible=True, float_values=False, border_width=0, metadata=None):
        super().__init__(canvas_size, graph_bottom_left, graph_top_right, background_color, pad, p, change_submits, drag_submits, enable_events, motion_events, key, k, tooltip, right_click_menu, expand_x, expand_y, visible, float_values, border_width, metadata)

    def update(self, state=0, background_color=None, visible=None):
        sg.Graph.erase(self)
        if state == 2:
            color = theme.GREEN
        elif state == 1:
            color = theme.BLUE
        elif state == 0:
            color = None
        elif state == -1:
            color = theme.YELLOW
        elif state == -2:
            color = theme.RED
        else:
            color = theme.PURPLE
        sg.Graph.draw_circle(self, (0,0), 12, fill_color=color, line_color='black')
        return super().update(background_color, visible)

class Loading(sg.Image):
    def __init__(self, key=None, size=(20,20), subsample=6, frames=30):
        self.size = size
        self.subsample = subsample
        self.frames = frames

        image_filename = f'_internal/LoadingIcon.pickle'
        with open(image_filename, 'rb') as file:
            self.icon = pickle.load(file)
            
        self.timer = Timer(1/self.frames)
        self.i = 0

        super().__init__(source=self.icon[self.i], key=key, size=self.size, subsample=self.subsample)

    def update(self):
        super().update(size=(20,20), subsample=6)
        if self.timer.finished:
            super().update(source=self.icon[self.i], size=self.size, subsample=self.subsample)

            self.i = (self.i+1)%self.frames
            self.timer.next()

    def reset(self):
        super().update(visible=False)
        time.sleep(1)
        gc.collect()
        time.sleep(1)
        super().update(visible=True)

    def clear(self):
        self.update()
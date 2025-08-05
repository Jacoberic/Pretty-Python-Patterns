try:
    #*Native libraries
    from math import tau

    #*Installed libraries
    from loguru import logger

    #*My classes
    from gui import Gui

    #*Utilities
    from utilities import Settings
    from utilities_log import log_start

except Exception:#this is so that errors are captured no matter what when run outside of VSCode.
    from traceback import format_exc
    from datetime import datetime
    with open('critical errors.log', 'a', newline='') as file:
        file.write(f'{datetime.now():%Y-%m-%d %H.%M.%S} | ERROR | {format_exc()}')
    quit()

try:
    log_start()
    settings = Settings()
    gui = Gui(settings)

    while gui.update():
        if gui.event == 'hi':
            logger.info(gui.window['file'].get())

except Exception:
    logger.exception('Unhandled exception')
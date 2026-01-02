try:
    #*Native libraries
    from math import tau

    #*Installed libraries
    from loguru import logger

    #*My classes
    from gui import Gui

    #*Utilities
    from utilities import Settings, Spinner
    from utilities_log import log_start
    from utilities_zmq import StateMachine

except Exception:#this is so that errors are captured no matter what when run outside of VSCode.
    from traceback import format_exc
    from datetime import datetime
    with open('critical errors.log', 'a', newline='') as file:
        file.write(f'{datetime.now():%Y-%m-%d %H.%M.%S} | ERROR | {format_exc()}')
    quit()

class Main(StateMachine):
    #*___________Overloads____________
    def __init__(self):
        super().__init__()

        self.settings = Settings()
        self.spinner = Spinner()

        self.gui = Gui(self.settings)

    def main_state(self):
        #*-->ENTER STATE
        pass

        #*-->RUN STATE-->
        while self.gui.update():
            try:
                self.spinner.spin()

                message = self.recv()

            except KeyboardInterrupt:
                #*EXIT STATE-->
                return None
          
    def state(self):
        #*-->ENTER STATE
        pass

        #*-->RUN STATE-->
        while True:
            pass
            
            if True:
                #*EXIT STATE-->
                return None

    def close(self):
        return super().close()
    
if __name__ == '__main__':
    main = Main()
    main.run()
    main.close()
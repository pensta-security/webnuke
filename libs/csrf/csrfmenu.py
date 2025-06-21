from libs.utils import MenuHelper
from .csrfcommands import CSRFCommands


class CSRFScreen:
    def __init__(self, screen, webdriver, curses_util, jsinjector, logger):
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.logger = logger
        self.commands = CSRFCommands(self.driver, jsinjector, self.logger)

    def show(self):
        items = [
            ('1', 'Enable form capture', self.commands.enable_capture),
            ('2', 'Generate CSRF PoC and open', self.commands.generate_and_open),
        ]
        MenuHelper.run(self.curses_util, 'CSRF Tools', items)
        return

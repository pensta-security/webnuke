import curses
from selenium.common.exceptions import WebDriverException
from libs.utils import MenuHelper

from libs.xss.xsscommands import XSSCommands

class XSSScreen:
    def __init__(self, screen, webdriver, curses_util, logger):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.logger = logger
        self.commands = XSSCommands(self.driver, self.logger)
        
        
        

    def show(self):
        def get_payload():
            try:
                return input("Enter XSS payload (default alert): ") or None
            except KeyboardInterrupt:
                return None

        def get_message():
            try:
                return input("Enter postMessage payload: ") or "test"
            except KeyboardInterrupt:
                return "test"

        items = [
            ('1', "Find XSS", self.commands.find_xss),
            ('2', "Create window.name exploit", lambda: self.commands.create_window_name_exploit(get_payload())),
            ('3', "Test postMessage", lambda: self.commands.test_post_message(get_message())),
            ('4', "Find reflected parameters", self.commands.find_reflected_params),
        ]
        MenuHelper.run(self.curses_util, "XSS", items)
        return

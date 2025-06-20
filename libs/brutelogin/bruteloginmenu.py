import curses
from selenium.common.exceptions import WebDriverException

from libs.brutelogin.brutelogincommands import *
from libs.utils import MenuHelper

class BruteLoginScreen:
    def __init__(self, screen, webdriver, curses_util):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.commands = BruteLoginCommands(self.driver)
        
        

    def show(self):
        items = [
            ('1', "Start brute forcing", self.commands.start_brute_force),
        ]
        MenuHelper.run(self.curses_util, "Brute Force Login", items)
        return

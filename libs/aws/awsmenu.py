import curses
from selenium.common.exceptions import WebDriverException

from libs.aws.awscommands import *
from libs.utils import MenuHelper

class AWSScreen:
    def __init__(self, screen, webdriver, curses_util, logger):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.logger = logger
        self.commands = AWSCommands(self.driver, self.logger)
        
        
        

    def show(self):
        items = [
            ('1', "Find S3 Bucket Urls", self.commands.show_bucket_report),
        ]
        MenuHelper.run(self.curses_util, "AWS", items)
        return

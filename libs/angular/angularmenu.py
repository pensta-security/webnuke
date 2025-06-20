import curses
from libs.angular.angularCommands import AngularCommands
from libs.utils import MenuHelper
from libs.utils.logger import FileLogger

class AngularScreen:
    def __init__(self, screen, webdriver, curses_util, jsinjector, logger=None):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.jsinjector = jsinjector
        self.logger = logger or FileLogger()
        self.commands = AngularCommands(self.driver, self.jsinjector, self.logger)
        
        
        
    def show(self):
        items = [
            ('1', "Show Main Application Name", self.commands.show_app_name),
            ('2', "Show Routes", self.commands.show_routes),
            ('3', "Show Dependencies", self.commands.show_deps),
            ('4', "Show Main Classes", self.commands.show_main_classes),
            ('5', "Show All Classes", self.commands.show_all_classes),
            ('6', "Test classes relying on ngResource", self.commands.show_ngResource_tests),
            ('7', "Test classes with get() and query()", self.commands.show_http_tests),
        ]

        MenuHelper.run(self.curses_util, "AngularJS Tools", items)
        return
        
    
        
    

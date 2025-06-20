import curses
from selenium.common.exceptions import WebDriverException

from libs.javascript.javascriptscript import *
from libs.utils import MenuHelper
from libs.utils.logger import FileLogger
from libs.javascript.javascriptcommands import *
from libs.javascript.jswalker import *
from libs.javascript.jsshell import JSShell


class JavascriptScreen:
    def __init__(self, screen, webdriver, curses_util, jsinjector, url_callback=None, logger=None):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.jsinjector = jsinjector
        self.url_callback = url_callback
        self.logger = logger or FileLogger()
        self.commands = JavascriptCommands(self.driver, self.jsinjector, self.logger)
        self.jswalker = JSWalker(self.driver, self.jsinjector, self.logger)
        
        

    def show(self):
        items = [
            ('1', "Find URLS within Javascript Global Properties", self.commands.search_for_urls),
            ('2', "Show Javascript functions of Document", self.commands.search_for_document_javascript_methods),
            ('3', "Run all js functions without args", self.commands.run_lone_javascript_functions),
            ('4', "Show Cookies accessable by Javascript", self.commands.show_cookies),
            ('5', "Walk Javascript Functions", self.jswalker.start_walk_tree),
            ('6', "Javascript Shell", self._run_shell),
            ('7', "Update builtin object list", self.commands.dump_browser_objects),
        ]
        MenuHelper.run(self.curses_util, "Javascript Tools", items)

    def _run_shell(self):
        if self.driver == 'notset':
            self.logger.log("Javascript Shell requires a loaded page. Use GOTO to open a URL first.")
            input("Press ENTER to continue...")
        else:
            JSShell(self.driver, self.url_callback, logger=self.logger).run()

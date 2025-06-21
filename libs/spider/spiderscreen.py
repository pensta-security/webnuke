import curses
from libs.spider.spidercommands import SpiderCommands
from libs.utils import MenuHelper
from libs.utils.logger import FileLogger

class SpiderScreen:
    def __init__(self, screen, curses_util, webdriver, logger=None):
        self.version = 2.0
        self.screen = screen
        self.curses_util = curses_util
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

        self.commands = SpiderCommands(self.webdriver, self.logger)
        
    def show(self, currenturl):
        self.current_url = currenturl

        def build_items():
            return [
                ('1', "Set Url to spider", self._set_url),
                ('2', "Run Kitchensinks in foreground", self._run_kitchensinks),
            ]

        def draw(screen):
            screen.addstr(4, 4, "1) Set Url to spider")
            screen.addstr(5, 24, "URL: " + self.current_url)
            screen.addstr(7, 4, "2) Run Kitchensinks in foreground")
            return 9  # next line

        MenuHelper.run(self.curses_util, "Spider Tools", build_items, extra_draw=lambda s: draw(s))
        return

    def _set_url(self):
        self.current_url = self.curses_util.get_param("Enter the url to spider")
        if self.current_url and self.current_url[-1] != '/':
            self.current_url += '/'

    def _run_kitchensinks(self):
        try:
            self.commands.run_kitchensinks_in_foreground(self.current_url)
        except Exception:
            self.logger.error("meh")
            pass


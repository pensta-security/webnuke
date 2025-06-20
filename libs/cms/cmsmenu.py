import curses
from libs.cms.cmscommands import CMSCommands
from libs.utils import MenuHelper


class CMSScreen:
    def __init__(self, screen, webdriver, curses_util, logger):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.logger = logger

    def show(self):
        items = [
            ('1', 'WordPress', lambda: CMSCommands(self.driver, 'wordpress', self.curses_util, self.logger).show()),
            ('2', 'Drupal', lambda: CMSCommands(self.driver, 'drupal', self.curses_util, self.logger).show()),
            ('3', 'Sitecore', lambda: CMSCommands(self.driver, 'sitecore', self.curses_util, self.logger).show()),
        ]
        MenuHelper.run(self.curses_util, "CMS Information", items)
        return

import curses
from libs.cms.cmscommands import CMSCommands


class CMSScreen:
    def __init__(self, screen, webdriver, curses_util, logger):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util
        self.logger = logger

    def show(self):
        showscreen = True
        while showscreen:
            self.screen = self.curses_util.get_screen()
            self.screen.addstr(2, 2, "CMS Information")
            self.screen.addstr(4, 5, "1) WordPress")
            self.screen.addstr(5, 5, "2) Drupal")
            self.screen.addstr(6, 5, "3) Sitecore")
            self.screen.addstr(22, 28, "PRESS M FOR MAIN MENU")
            self.screen.refresh()
            c = self.screen.getch()
            if c in (ord('M'), ord('m')):
                showscreen = False
            elif c == ord('1'):
                self.curses_util.close_screen()
                self.logger.log('CMS menu: selected WordPress')
                CMSCommands(self.driver, 'wordpress', self.curses_util, self.logger).show()
            elif c == ord('2'):
                self.curses_util.close_screen()
                self.logger.log('CMS menu: selected Drupal')
                CMSCommands(self.driver, 'drupal', self.curses_util, self.logger).show()
            elif c == ord('3'):
                self.curses_util.close_screen()
                self.logger.log('CMS menu: selected Sitecore')
                CMSCommands(self.driver, 'sitecore', self.curses_util, self.logger).show()
        return

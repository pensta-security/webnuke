import curses
from libs.cms.cmscommands import CMSCommands


class CMSScreen:
    def __init__(self, screen, webdriver, curses_util):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        self.curses_util = curses_util

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
                CMSCommands(self.driver, 'wordpress', self.curses_util).show()
            elif c == ord('2'):
                self.curses_util.close_screen()
                CMSCommands(self.driver, 'drupal', self.curses_util).show()
            elif c == ord('3'):
                self.curses_util.close_screen()
                CMSCommands(self.driver, 'sitecore', self.curses_util).show()
        return

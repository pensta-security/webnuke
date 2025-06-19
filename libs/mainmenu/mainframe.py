import curses
import time
import atexit
from libs.utils.WebDriverUtil import *
from libs.utils.cursesutil import *
from libs.javascript.javascriptmenu import *
from libs.angular.angularmenu import *
from libs.htmltools.htmlmenu import *
from libs.quickdetect.QuickDetect import *
from libs.jsconsole.JSConsole import *
from libs.spider.spiderscreen import *
from libs.spider.spidercommands import *
from libs.utils.javascriptinjector import *
from libs.mainmenu.mainmenuscreen import *
from libs.followme.followmemenu import *
from libs.brutelogin.bruteloginmenu import *
from libs.aws.awsmenu import *
from libs.xss.xssmenu import *
from libs.cms.cmsmenu import *
import subprocess
import os
import sys

class mainframe:
    def __init__(self, logger):
        self.debug = True
        self.proxy_host = ''
        self.proxy_port = 0
        self.driver = 'notset'
        self.current_url = "NONE"
        self.warning = ''
        self.curses_util = CursesUtil()
        self.logger = logger
        self.jsinjector = JavascriptInjector()
        atexit.register(self.curses_util.close_screen)
        # load plugin javascript
        self.plugins = [JSConsoleScript(self.jsinjector), JavascriptScript(self.jsinjector), HTMLToolsScript(self.jsinjector), AngularCustomJavascript(self.jsinjector)]
        self.url_history = []

    def prompt_for_url(self):
        if not self.url_history:
            return self.curses_util.get_param("Enter the url").decode("utf-8")

        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(2, 2, "Goto URL - select history or enter new")
        y = 4
        for i, url in enumerate(self.url_history, start=1):
            self.screen.addstr(y, 4, f"{i}) {url}")
            y += 1
        self.screen.addstr(y, 4, "Enter number or URL:")
        self.screen.refresh()
        choice = self.screen.getstr(y, 23, 60).decode("utf-8")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.url_history):
                return self.url_history[idx]
        return choice
        
    def show_main_screen(self):
        self.logger.log("run_main")
        mystr = 'startup'
        mystr_elements = mystr.split()
        firstelement=mystr_elements[0]

        while firstelement != 'quit' and firstelement != 'q':
            try:
                self.screen = self.curses_util.get_screen()
                MainMenuScreen(self.screen, curses).drawscreen()

                if self.warning != '':
                    self.screen.addstr(22, 2, self.warning, curses.color_pair(1))
                    self.warning = ''

                if self.proxy_host != '':
                    self.screen.addstr(0, 1, "PROXY ENABLED", curses.color_pair(1))
                if self.debug:
                    self.screen.addstr(0, 71, "DEBUG ON", curses.color_pair(1))
                self.screen.refresh()

                mystr = self.screen.getstr(22, 4).decode(encoding="utf-8")
                mystr_elements = mystr.split()
                firstelement = 'notset'
                if len(mystr_elements) >= 1:
                    firstelement = mystr_elements[0]

                if firstelement == 'd':
                    self.debug = True
                    self.current_url = "https://xss-game.appspot.com/level1/frame?query=d&bah=heh&jim=ab"
                    #self.proxy_host = '192.168.162.33'
                    #self.proxy_port = 8080
                    self.open_url(self.current_url)
                    firstelement = "html"

                if firstelement in ('1', 'goto'):
                    if len(mystr_elements) >= 2:
                        url = mystr_elements[1]
                    else:
                        url = self.prompt_for_url()
                    self.open_url(url)

                if firstelement in ('13', 'debug'):
                    self.debug = not self.debug

                if firstelement in ('14', 'proxy'):
                    self.proxy_host = self.curses_util.get_param("Enter Proxy Server Hostname or IP, Leave BLANK for no proxy")
                    self.proxy_port = self.curses_util.get_param("Enter Proxy Server Port Number")

                if firstelement in ('2', 'quickdetect'):
                    if len(mystr_elements) >= 2:
                        url = mystr_elements[1]
                        self.open_url(url)
                    if self.driver == 'notset':
                        self.warning = "QUICKDETECT requires a url is loaded, please set a url using GOTO"
                        return
                    QuickDetect(self.screen, self.driver, self.curses_util, self.logger).run()

                if firstelement in ('3', 'jsconsole'):
                    self.curses_util.close_screen()
                    JSConsole(self.driver, self.jsinjector).run()

                if firstelement in ('8', 'followme'):
                    self.curses_util.close_screen()
                    FollowmeScreen(self.screen, self.driver, self.curses_util, self.debug, self.proxy_host, self.proxy_port, self.logger).run()

                if firstelement in ('15', '!sh'):
                    self.curses_util.execute_cmd("bash")

                if firstelement in ('5', 'javascript'):
                    JavascriptScreen(self.screen, self.driver, self.curses_util, self.jsinjector).show()

                if firstelement in ('6', 'angularjs'):
                    AngularScreen(self.screen, self.driver, self.curses_util, self.jsinjector).show()

                if firstelement in ('7', 'spider'):
                    SpiderScreen(self.screen, self.curses_util, self.driver).show(self.driver.current_url)

                if firstelement in ('9', 'brute'):
                    BruteLoginScreen(self.screen, self.driver, self.curses_util).show()

                if firstelement in ('10', 'aws'):
                    AWSScreen(self.screen, self.driver, self.curses_util, self.logger).show()

                if firstelement in ('11', 'cms'):
                    if self.driver == 'notset':
                        self.warning = "CMS requires a url is loaded, please set a url using GOTO"
                    else:
                        CMSScreen(self.screen, self.driver, self.curses_util, self.logger).show()

                if firstelement in ('4', 'html'):
                    HTMLScreen(self.screen, self.driver, self.curses_util, self.jsinjector).show()

                if firstelement in ('12', 'xss'):
                    XSSScreen(self.screen, self.driver, self.curses_util, self.logger).show()

                if firstelement in ('16', 'update'):
                    self.update_and_restart()

                if firstelement in ('17',):
                    firstelement = 'quit'
            except curses.error:
                pass
            except Exception:
                self.logger.log("EEE Unexpected error in main::show_main_screen")
                print("Unexpected error!")
                raise
        self.curses_util.close_screen()
    def create_browser_instance(self):
        self.webdriver_util = WebDriverUtil()
        self.webdriver_util.setDebug(self.debug)
        if self.proxy_host != '' and int(self.proxy_port) != 0:
            print("getting webdriver with proxy support")
            return self.webdriver_util.getDriverWithProxySupport(self.proxy_host, int(self.proxy_port))
        else:
            return self.webdriver_util.getDriver(self.logger)
         
    def open_url(self, url):
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'

        if self.driver == 'notset':
            self.driver = self.create_browser_instance()

        self.current_url = url
        try:
            self.driver.get(url)
            self.current_url = self.driver.current_url
        except Exception:
            pass
        self.url_history.insert(0, self.current_url)
        self.url_history = self.url_history[:5]

    def update_and_restart(self):
        """Pull latest updates from git and restart the application."""
        self.curses_util.close_screen()
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        print(result.stdout)
        if 'Already up to date.' in result.stdout:
            input('No updates found. Press Enter to continue...')
        else:
            input('Updates applied. Press Enter to restart...')
            os.execv(sys.executable, [sys.executable] + sys.argv)

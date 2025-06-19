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

                if firstelement == 'goto':
                    if len(mystr_elements) >= 2:
                        url = mystr_elements[1]
                    else:
                        url = self.curses_util.get_param("Enter the url")
                    self.open_url(url)
                 
                if firstelement == 'debug':
                    self.debug = not self.debug
                      
                if firstelement == 'proxy':
                    self.proxy_host = self.curses_util.get_param("Enter Proxy Server Hostname or IP, Leave BLANK for no proxy")
                    self.proxy_port = self.curses_util.get_param("Enter Proxy Server Port Number")
                      
                if firstelement == 'quickdetect':
                    if len(mystr_elements) >= 2:
                        url = mystr_elements[1]
                        self.open_url(url)
                    if self.driver == 'notset':
                        self.warning = "QUICKDETECT requires a url is loaded, please set a url using GOTO"
                        return
                    QuickDetect(self.screen, self.driver, self.curses_util, self.logger).run()
                 
                if firstelement == 'jsconsole':
                    self.curses_util.close_screen()
                    JSConsole(self.driver, self.jsinjector).run()

                if firstelement == 'followme':
                    self.curses_util.close_screen()
                    FollowmeScreen(self.screen, self.driver, self.curses_util, self.debug, self.proxy_host, self.proxy_port, self.logger).run()
                     
                if firstelement == '!sh':
                    self.curses_util.execute_cmd("bash")
                      
                if firstelement == 'javascript':
                    JavascriptScreen(self.screen, self.driver, self.curses_util, self.jsinjector).show()

                if firstelement == 'angularjs':
                    AngularScreen(self.screen, self.driver, self.curses_util, self.jsinjector).show()
                     
                if firstelement == 'spider':
                    SpiderScreen(self.screen, self.curses_util, self.driver).show(self.driver.current_url)

                if firstelement == 'brute':
                    BruteLoginScreen(self.screen, self.driver, self.curses_util).show()
                 
                if firstelement == 'aws':
                    AWSScreen(self.screen, self.driver, self.curses_util, self.logger).show()

                if firstelement == 'cms':
                    CMSScreen(self.screen, self.driver, self.curses_util).show()

                if firstelement == 'html':
                    HTMLScreen(self.screen, self.driver, self.curses_util, self.jsinjector).show()
                 
                if firstelement == 'xss':
                    XSSScreen(self.screen, self.driver, self.curses_util, self.logger).show()
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
        if self.driver == 'notset':
            self.driver = self.create_browser_instance()
        self.current_url = url
        try:
            self.driver.get(url)
            self.current_url = self.driver.current_url
        except:
            pass

import curses
import time
import atexit
import json
from libs.utils.WebDriverUtil import WebDriverUtil
from libs.utils.cursesutil import CursesUtil
from libs.javascript.javascriptmenu import JavascriptScreen
from libs.angular.angularmenu import AngularScreen
from libs.htmltools.htmlmenu import HTMLScreen
from libs.quickdetect.QuickDetect import QuickDetect
from libs.jsconsole.JSConsole import JSConsole
from libs.spider.spiderscreen import SpiderScreen
from libs.utils.javascriptinjector import JavascriptInjector
from libs.utils import wait_for_enter, NetworkLogger
from libs.mainmenu.mainmenuscreen import MainMenuScreen
from libs.followme.followmemenu import FollowmeScreen
from libs.brutelogin.bruteloginmenu import BruteLoginScreen
from libs.aws.awsmenu import AWSScreen
from libs.xss.xssmenu import XSSScreen
from libs.cms.cmsmenu import CMSScreen
from libs.csrf.csrfmenu import CSRFScreen
from libs.jsconsole.jsconsolescript import JSConsoleScript
from libs.javascript.javascriptscript import JavascriptScript
from libs.htmltools.htmltoolsscript import HTMLToolsScript
from libs.angular.angularCustomJavascript import AngularCustomJavascript
import subprocess
import os
import sys

class mainframe:
    def __init__(self, logger, headless=False, har_path=None, proxy_host='', proxy_port=0):
        self.debug = True
        self.headless = headless
        self.har_path = har_path
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.driver = 'notset'
        self.current_url = "NONE"
        self.warning = ''
        self.curses_util = CursesUtil(logger)
        self.logger = logger
        self.jsinjector = JavascriptInjector()
        self.network_logger = None
        atexit.register(self.curses_util.close_screen)
        # load plugin javascript
        self.plugins = [JSConsoleScript(self.jsinjector), JavascriptScript(self.jsinjector), HTMLToolsScript(self.jsinjector), AngularCustomJavascript(self.jsinjector)]
        self.history_file = os.path.join(os.getcwd(), 'history.txt')
        self.url_history = self._load_history()
        atexit.register(self._save_history)
        atexit.register(self._save_network_har)

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

        def goto_cmd(args):
            url = args[0] if args else self.prompt_for_url()
            self.open_url(url)

        def toggle_debug_cmd(args):
            self.debug = not self.debug

        def proxy_cmd(args):
            self.proxy_host = (
                self.curses_util.get_param(
                    "Enter Proxy Server Hostname or IP, Leave BLANK for no proxy"
                )
                .decode("utf-8")
                .strip()
            )
            self.proxy_port = (
                self.curses_util.get_param("Enter Proxy Server Port Number")
                .decode("utf-8")
                .strip()
            )

        def quickdetect_cmd(args):
            if args:
                self.open_url(args[0])
            if self.driver == "notset":
                self.warning = (
                    "QUICKDETECT requires a url is loaded, please set a url using GOTO"
                )
                return
            qd = QuickDetect(self.screen, self.driver, self.curses_util, self.logger)
            qd.run()
            if self.har_path:
                os.makedirs(self.har_path, exist_ok=True)
                ts = time.strftime("%Y%m%d_%H%M%S")
                path = os.path.join(self.har_path, f"har_{ts}.json")
                qd.get_network_har(path)

        def jsconsole_cmd(args):
            self.curses_util.close_screen()
            JSConsole(self.driver, self.jsinjector, self.logger).run()

        def followme_cmd(args):
            self.curses_util.close_screen()
            FollowmeScreen(
                self.screen,
                self.driver,
                self.curses_util,
                self.debug,
                self.proxy_host,
                self.proxy_port,
                self.logger,
            ).run()

        def shell_cmd(args):
            self.curses_util.execute_cmd("bash")

        def javascript_cmd(args):
            JavascriptScreen(
                self.screen,
                self.driver,
                self.curses_util,
                self.jsinjector,
                self.open_url,
                logger=self.logger,
            ).show()

        def angular_cmd(args):
            AngularScreen(
                self.screen,
                self.driver,
                self.curses_util,
                self.jsinjector,
                logger=self.logger,
            ).show()

        def spider_cmd(args):
            SpiderScreen(
                self.screen, self.curses_util, self.driver, self.logger
            ).show(self.driver.current_url)

        def brute_cmd(args):
            BruteLoginScreen(self.screen, self.driver, self.curses_util).show()

        def aws_cmd(args):
            AWSScreen(self.screen, self.driver, self.curses_util, self.logger).show()

        def cms_cmd(args):
            if self.driver == "notset":
                self.warning = (
                    "CMS requires a url is loaded, please set a url using GOTO"
                )
            else:
                CMSScreen(
                    self.screen, self.driver, self.curses_util, self.logger
                ).show()

        def html_cmd(args):
            HTMLScreen(
                self.screen, self.driver, self.curses_util, self.jsinjector
            ).show()

        def xss_cmd(args):
            XSSScreen(self.screen, self.driver, self.curses_util, self.logger).show()

        def csrf_cmd(args):
            CSRFScreen(
                self.screen,
                self.driver,
                self.curses_util,
                self.jsinjector,
                self.logger,
            ).show()

        def update_cmd(args):
            self.update_and_restart()

        def debug_demo_cmd(args):
            self.debug = True
            self.current_url = (
                "https://xss-game.appspot.com/level1/frame?query=d&bah=heh&jim=ab"
            )
            self.open_url(self.current_url)
            html_cmd([])

        def quit_cmd(args):
            nonlocal firstelement
            firstelement = "quit"

        command_table = {
            "1": goto_cmd,
            "goto": goto_cmd,
            "2": quickdetect_cmd,
            "quickdetect": quickdetect_cmd,
            "3": jsconsole_cmd,
            "jsconsole": jsconsole_cmd,
            "4": html_cmd,
            "html": html_cmd,
            "5": javascript_cmd,
            "javascript": javascript_cmd,
            "6": angular_cmd,
            "angularjs": angular_cmd,
            "7": spider_cmd,
            "spider": spider_cmd,
            "8": followme_cmd,
            "followme": followme_cmd,
            "9": brute_cmd,
            "brute": brute_cmd,
            "10": aws_cmd,
            "aws": aws_cmd,
            "11": cms_cmd,
            "cms": cms_cmd,
            "12": xss_cmd,
            "xss": xss_cmd,
            "13": csrf_cmd,
            "csrf": csrf_cmd,
            "14": toggle_debug_cmd,
            "debug": toggle_debug_cmd,
            "15": proxy_cmd,
            "proxy": proxy_cmd,
            "16": shell_cmd,
            "!sh": shell_cmd,
            "17": update_cmd,
            "update": update_cmd,
            "18": quit_cmd,
            "quit": quit_cmd,
            "q": quit_cmd,
            "d": debug_demo_cmd,
        }

        mystr = "startup"
        mystr_elements = mystr.split()
        firstelement = mystr_elements[0]

        while firstelement not in ("quit", "q"):
            try:
                self.screen = self.curses_util.get_screen()
                MainMenuScreen(self.screen, curses).drawscreen()

                if self.warning != "":
                    self.screen.addstr(22, 2, self.warning, curses.color_pair(1))
                    self.warning = ""

                if self.proxy_host != "":
                    self.screen.addstr(0, 1, "PROXY ENABLED", curses.color_pair(1))
                if self.debug:
                    self.screen.addstr(0, 71, "DEBUG ON", curses.color_pair(1))
                self.screen.refresh()

                mystr = self.screen.getstr(22, 4).decode(encoding="utf-8")
                mystr_elements = mystr.split()
                firstelement = mystr_elements[0] if mystr_elements else "notset"
                args = mystr_elements[1:]

                cmd_fn = command_table.get(firstelement)
                if cmd_fn:
                    cmd_fn(args)
            except curses.error:
                pass
            except Exception:
                self.logger.log("EEE Unexpected error in main::show_main_screen")
                self.logger.error("Unexpected error!")
                raise
        self.curses_util.close_screen()
        if self.driver != "notset":
            try:
                self._save_network_har()
                if hasattr(self, "webdriver_util"):
                    self.webdriver_util.quit_driver(self.driver)
                else:
                    self.driver.quit()
            except Exception:
                pass
    def create_browser_instance(self):
        self.webdriver_util = WebDriverUtil()
        self.webdriver_util.setDebug(self.debug)
        port = int(self.proxy_port) if str(self.proxy_port).isdigit() else 0
        if self.proxy_host and port:
            self.logger.log("getting webdriver with proxy support")
            driver = self.webdriver_util.getDriverWithProxySupport(
                self.proxy_host, port, headless=self.headless
            )
        else:
            driver = self.webdriver_util.getDriver(self.logger, headless=self.headless)

        self.network_logger = NetworkLogger(driver, self.logger)
        return driver
         
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
        while self.current_url in self.url_history:
            self.url_history.remove(self.current_url)
        self.url_history.insert(0, self.current_url)
        self.url_history = self.url_history[:5]
        self._save_history()

    def update_and_restart(self):
        """Pull latest updates from git and restart the application."""
        self.curses_util.close_screen()
        if self.driver != 'notset':
            try:
                self._save_network_har()
                if hasattr(self, 'webdriver_util'):
                    self.webdriver_util.quit_driver(self.driver)
                else:
                    self.driver.quit()
            except Exception:
                pass
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        self.logger.log(result.stdout)
        if 'Already up to date.' in result.stdout:
            wait_for_enter('No updates found. Press Enter to continue...')
        else:
            wait_for_enter('Updates applied. Press Enter to restart...')
            os.execv(sys.executable, [sys.executable] + sys.argv)

    def _load_history(self):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            lines = []
        return lines[:5]

    def _save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for url in self.url_history:
                    f.write(url + '\n')
        except Exception:
            pass

    def _save_network_har(self):
        if self.har_path and self.network_logger:
            try:
                os.makedirs(self.har_path, exist_ok=True)
                ts = time.strftime("%Y%m%d_%H%M%S")
                path = os.path.join(self.har_path, f"har_{ts}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.network_logger.get_har(), f, indent=2)
            except Exception as exc:
                self.logger.error(f"Error writing HAR file: {exc}")
            finally:
                self.network_logger = None

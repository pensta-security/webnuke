import time
import _thread
from libs.utils.WebDriverUtil import WebDriverUtil
from libs.utils.logger import FileLogger

class FollowmeCommands:
    def __init__(self, webdriver, debug, proxy_host, proxy_port, logger):
        self.version = 2.0
        self.driver = webdriver
        self.debug = debug
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.logger = logger
        self.paused = False
        self.run_thread = True
        self.running_browsers = []
    
    def start_new_instance(self):
        self.run_thread = True
        browser = self.create_browser_instance()
        self.running_browsers.append(browser)
        _thread.start_new_thread(self.linkbrowsers, (self.driver, browser))
        
        
    def pause_all(self):
        self.paused = True

    def resume_all(self):
        self.paused = False

    def kill_all(self):
        self.run_thread = False
        for browser in self.running_browsers:
            browser.quit()
        self.running_browsers = []
        

        
    def get_paused(self):
        return self.paused

    def create_browser_instance(self):
        self.webdriver_util = WebDriverUtil()
        self.webdriver_util.setDebug(self.debug)
        if self.proxy_host != '' and int(self.proxy_port) != 0:
            return self.webdriver_util.getDriverWithProxySupport(self.proxy_host, int(self.proxy_port))
        else:
            return self.webdriver_util.getDriver(self.logger)

    def linkbrowsers(self, maindriver, followmedriver):
        while self.run_thread:
            if not self.paused:
                try:
                    main_url = maindriver.current_url
                    if followmedriver.current_url != main_url:
                        followmedriver.get(main_url)
                except Exception as e:
                    self.logger.error(f'Error syncing browsers: {e}')
                finally:
                    time.sleep(0.5)

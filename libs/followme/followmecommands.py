import time
import threading
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
        self.running_threads = []
    
    def start_new_instance(self):
        self.run_thread = True
        browser = self.create_browser_instance()
        self.running_browsers.append(browser)
        thread = threading.Thread(target=self.linkbrowsers, args=(self.driver, browser))
        thread.daemon = True
        self.running_threads.append(thread)
        thread.start()
        
        
    def pause_all(self):
        self.paused = True

    def resume_all(self):
        self.paused = False

    def kill_all(self):
        self.run_thread = False
        for thread in self.running_threads:
            if thread.is_alive():
                thread.join(timeout=1)
        self.running_threads = []
        for browser in self.running_browsers:
            browser.quit()
        self.running_browsers = []
        

        
    def get_paused(self):
        return self.paused

    def create_browser_instance(self):
        self.webdriver_util = WebDriverUtil()
        self.webdriver_util.setDebug(self.debug)
        port = int(self.proxy_port) if str(self.proxy_port).isdigit() else 0
        if self.proxy_host and port:
            return self.webdriver_util.getDriverWithProxySupport(self.proxy_host, port)
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

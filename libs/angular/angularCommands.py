from selenium.common.exceptions import WebDriverException
from libs.angular.angularCustomJavascript import *
import selenium.webdriver.support.ui as ui
import time
from libs.utils.logger import FileLogger

class AngularCommands:
    def __init__(self, webdriver, jsinjector, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.jsinjector = jsinjector
        self.logger = logger or FileLogger()
        #self.reload_with_debug_info()
    
    def reload_with_debug_info(self):
        self.driver.execute_script('angular.reloadWithDebugInfo()')
        newurl = self.driver.current_url
        self.logger.log(newurl)
        
    def show_app_name(self):
        self.run_javascript('wn_showAngularAppName()')
        
    def show_deps(self):
        self.run_javascript('wn_showAngularDeps()')     
        
    def show_main_classes(self):
        self.run_javascript('wn_showAngularMainClasses()')
    
    def show_all_classes(self):
        self.run_javascript('wn_showAngularAllClasses()')
        
    def show_routes(self):
        self.run_javascript('wn_showAngularRoutes()')
    
    def run_javascript(self, javascript_function):
        self.jsinjector.execute_javascript(self.driver, javascript_function)
        self.logger.log('')
        self.logger.log('')
        input("Press ENTER to return to menu.")
        
    def show_ngResource_tests(self):
        # ngResource classes generally communicate with api endpoints... run with proxy to capture api calls.
        self.logger.log("Testing classes, please wait...")
        self.logger.log('')
        self.jsinjector.execute_javascript(self.driver, "wn_testNgResourceClasses();")
        time.sleep(10)
        result = self.jsinjector.execute_javascript(self.driver, "console.log('all done');")
        self.logger.log(result)
        self.logger.log('')
        self.logger.log('')
        input("Press ENTER to return to menu.")
        
    def show_http_tests(self):
        # ngResource classes generally communicate with api endpoints... run with proxy to capture api calls.
        self.logger.log("Testing classes using $http, please wait...")
        self.logger.log('')
        self.jsinjector.execute_javascript(self.driver, "wn_testHTTPClasses();")
        time.sleep(10)
        result = self.jsinjector.execute_javascript(self.driver, "console.log('All done son.');")
        self.logger.log(result)
        self.logger.log('')
        self.logger.log('')
        input("Press ENTER to return to menu.")     
        

import time
from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger
from libs.utils import wait_for_enter

class SpiderCommands:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.webdriver = webdriver
        self.default_page_element_count = 0
        self.logger = logger or FileLogger()
        
    def run_kitchensinks_in_foreground(self, url):
        self.logger.log("Running Kitchensinks on %s, please wait..." % url)
        self.logger.log('')
        self.logger.log('')
        # try fuzzdb, kitchensinks
        kitchensinks_path = 'libs/spider/KitchensinkDirectories.txt'
        
        
        
        with open(kitchensinks_path) as f:
            content = f.read().splitlines()
        for line in content:
            url_to_try = self.build_full_url(url, line)
            r = self.try_url(url_to_try)
        
            
        self.logger.log('')
        self.logger.log('')
        wait_for_enter("Finished, Press ENTER to return to menu.")
        
    def build_full_url(self, url, line):
        url_to_return = url
        
        if '#' in url:
            url_without_hash = url.split('#')[0]
            url_to_return = url_without_hash+'#'+line
        elif line[0] == '/' and url[-1] == '/': 
            url_to_return += line[1:]
        else:
            url_to_return = url+"/"+line
            
        return url_to_return
    
    def try_url(self, url_to_try):      
        try:
            if self.default_page_element_count == 0:
                all_elements = self.webdriver.find_elements(By.XPATH, '//*')
                self.default_page_element_count = len(all_elements)
            self.webdriver.get(url_to_try)
            #time.sleep(0.5)
            newurl = self.webdriver.current_url
            new_elements = self.webdriver.find_elements(By.XPATH, '//*')
            new_elements_count= len(new_elements)
            if new_elements_count != self.default_page_element_count:
                self.logger.debug("XXX "+url_to_try)
            
        
        except Exception as e:
            self.logger.error(f'Error processing {url_to_try}: {e}')
            time.sleep(10)
            # sleep a bit to ease up on network sockets
            
        return None
        
    def log_result(self, r, url_to_try):
        if r.status_code != 404:
            self.logger.log('%s - %s' % (r.status_code, url_to_try))
        

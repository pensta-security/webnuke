import time
from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger

class DrupalUtil:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver
        self.logger = logger or FileLogger()
        
    def isDrupal(self):
        try:
            result = self.webdriver.execute_script('return this.Drupal')
            if result is None:
                return False
            return True
        except Exception as e:
            self.logger.error(f'Error checking Drupal: {e}')
        return False
    
    def getVersionString(self):
        generator = self.getMetaGenerator()
        if generator and generator.startswith('Drupal'):
            return generator
        return None
        
    def getMetaGenerator(self):
        try:
            for xpath in ("//meta[@name='Generator']", "//meta[@name='generator']"):
                elements = self.webdriver.find_elements(By.XPATH, xpath)
                if elements:
                    return elements[0].get_attribute("content")
        except Exception as e:
            self.logger.error(f'Error reading generator tag: {e}')
        return None
        


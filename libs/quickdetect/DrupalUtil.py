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
            if result == None:
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
        generator = ''
        
        found_generator = False
        try:
            result = self.webdriver.find_element(By.XPATH, "//meta[@name='Generator']")
            generator = result.get_attribute("content")
            found_generator = True
        except Exception as e:
            self.logger.error(f'Error reading Generator meta tag: {e}')

        if found_generator == False:
            try:
                result = self.webdriver.find_element(By.XPATH, "//meta[@name='generator']")
                generator = result.get_attribute("content")
                found_generator = True
            except Exception as e:
                self.logger.error(f'Error reading generator tag: {e}')
        
        if found_generator:
            return generator
        return None
        


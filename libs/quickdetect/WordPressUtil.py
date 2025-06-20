from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger

class WordPressUtil:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver
        self.logger = logger or FileLogger()
        
    def isWordPress(self):
        try:
            self.webdriver.find_element(By.XPATH, "//meta[@name='generator']")
            generator = self.getVersionString()
            if generator and generator.startswith('WordPress'):
                return True
        except Exception as e:
            self.logger.error(f'Error detecting WordPress: {e}')
        return False
        
    def getVersionString(self):
        try:
            result = self.webdriver.find_element(By.XPATH, "//meta[@name='generator']")
            generator = result.get_attribute("content")
            return generator
        except Exception as e:
            self.logger.error(f'Error retrieving WordPress version: {e}')
        return None


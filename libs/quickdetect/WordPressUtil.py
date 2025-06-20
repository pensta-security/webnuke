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
            elements = self.webdriver.find_elements(By.XPATH, "//meta[@name='generator']")
            if elements:
                generator = self.getVersionString()
                if generator and generator.startswith('WordPress'):
                    return True
        except Exception as e:
            self.logger.error(f'Error detecting WordPress: {e}')
        return False
        
    def getVersionString(self):
        try:
            elements = self.webdriver.find_elements(By.XPATH, "//meta[@name='generator']")
            if elements:
                return elements[0].get_attribute("content")
        except Exception as e:
            self.logger.error(f'Error retrieving WordPress version: {e}')
        return None


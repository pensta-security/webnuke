from selenium.webdriver.common.by import By

class WordPressUtil:
    def __init__(self, webdriver):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver
        
    def isWordPress(self):
        try:
            self.webdriver.find_element(By.XPATH, "//meta[@name='generator']")
            generator = self.getVersionString()
            if generator and generator.startswith('WordPress'):
                return True
        except Exception:
            pass
        return False
        
    def getVersionString(self):
        try:
            result = self.webdriver.find_element(By.XPATH, "//meta[@name='generator']")
            generator = result.get_attribute("content")
            return generator
        except:
            pass
        return None


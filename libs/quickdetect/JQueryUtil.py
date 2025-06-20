from libs.utils.logger import FileLogger


class JQueryUtil:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver
        self.logger = logger or FileLogger()
        
    def isJQuery(self):
        try:
            result = self.webdriver.execute_script('return this.$.fn.jquery')
            if result == None:
                return False
            return True
        except Exception as e:
            self.logger.error(f'Error detecting jQuery: {e}')
        return False
        
    def getVersionString(self):
        try:
            result = self.webdriver.execute_script('return this.$.fn.jquery')
            return result
        except Exception as e:
            self.logger.error(f'Error retrieving jQuery version: {e}')
        return None



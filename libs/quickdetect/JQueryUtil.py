from libs.utils.logger import FileLogger


class JQueryUtil:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver
        self.logger = logger or FileLogger()
        
    def isJQuery(self):
        try:
            script = (
                "return (window.jQuery && window.jQuery.fn && "
                "window.jQuery.fn.jquery) ? window.jQuery.fn.jquery : null;"
            )
            result = self.webdriver.execute_script(script)
            return bool(result)
        except Exception as e:
            self.logger.error(f'Error detecting jQuery: {e}')
            return False

    def getVersionString(self):
        try:
            script = (
                "return (window.jQuery && window.jQuery.fn && "
                "window.jQuery.fn.jquery) ? window.jQuery.fn.jquery : null;"
            )
            return self.webdriver.execute_script(script)
        except Exception as e:
            self.logger.error(f'Error retrieving jQuery version: {e}')
            return None



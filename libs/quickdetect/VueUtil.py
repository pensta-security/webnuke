from selenium.webdriver.remote.webdriver import WebDriver
from libs.utils.logger import FileLogger

class VueUtil:
    def __init__(self, webdriver: WebDriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def is_vue(self) -> bool:
        """Return True if Vue is detected on the page."""
        try:
            return bool(self.webdriver.execute_script("return typeof Vue !== 'undefined';"))
        except Exception as e:
            self.logger.error(f'Error detecting Vue: {e}')
            return False

    def get_version_string(self):
        """Return the Vue.js version string if available."""
        try:
            script = "return (window.Vue && window.Vue.version) ? window.Vue.version : null;"
            return self.webdriver.execute_script(script)
        except Exception as e:
            self.logger.error(f'Error retrieving Vue version: {e}')
            return None

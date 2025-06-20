from selenium.webdriver.remote.webdriver import WebDriver
from libs.utils.logger import FileLogger

class ReactUtil:
    def __init__(self, webdriver: WebDriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def is_react(self) -> bool:
        try:
            return bool(self.webdriver.execute_script("return typeof React !== 'undefined';"))
        except Exception as e:
            self.logger.error(f'Error detecting React: {e}')
            return False

    def get_version_string(self):
        try:
            script = "return (window.React && window.React.version) ? window.React.version : null;"
            return self.webdriver.execute_script(script)
        except Exception as e:
            self.logger.error(f'Error retrieving React version: {e}')
            return None

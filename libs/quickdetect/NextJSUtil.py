from selenium.webdriver.remote.webdriver import WebDriver
from libs.utils.logger import FileLogger

class NextJSUtil:
    def __init__(self, webdriver: WebDriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def is_nextjs(self) -> bool:
        """Return True if Next.js is detected on the page."""
        try:
            script = (
                "return !!(window.__NEXT_DATA__ || "
                "document.querySelector('#__next'));"
            )
            return bool(self.webdriver.execute_script(script))
        except Exception as e:
            self.logger.error(f'Error detecting Next.js: {e}')
            return False

    def get_version_string(self):
        """Return build/version information if available."""
        try:
            script = (
                "return (window.__NEXT_DATA__ && "
                "window.__NEXT_DATA__.buildId) ? "
                "window.__NEXT_DATA__.buildId : null;"
            )
            return self.webdriver.execute_script(script)
        except Exception as e:
            self.logger.error(f'Error retrieving Next.js version: {e}')
            return None

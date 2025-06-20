from selenium.webdriver.remote.webdriver import WebDriver
from libs.utils.logger import FileLogger

class EmberUtil:
    def __init__(self, webdriver: WebDriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def is_ember(self) -> bool:
        """Return True if Ember.js is detected on the page."""
        try:
            script = (
                "return !!(window.Ember || window.__ember_root__ || "
                "document.querySelector('meta[name=\"ember-cli\"]'));"
            )
            return bool(self.webdriver.execute_script(script))
        except Exception as e:
            self.logger.error(f'Error detecting Ember: {e}')
            return False

    def get_version_string(self):
        """Return the Ember.js version string if available."""
        try:
            script = (
                "return (window.Ember && window.Ember.VERSION) ? "
                "window.Ember.VERSION : null;"
            )
            version = self.webdriver.execute_script(script)
            if version:
                return str(version)
            meta_script = (
                "var el = document.querySelector('meta[name=\"ember-cli\"]');"
                "return el ? el.getAttribute('content') : null;"
            )
            return self.webdriver.execute_script(meta_script)
        except Exception as e:
            self.logger.error(f'Error retrieving Ember version: {e}')
            return None

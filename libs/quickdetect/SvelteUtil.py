from selenium.webdriver.remote.webdriver import WebDriver
from libs.utils.logger import FileLogger

class SvelteUtil:
    def __init__(self, webdriver: WebDriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def is_svelte(self) -> bool:
        """Return True if Svelte is detected on the page."""
        try:
            script = (
                "return !!(window.__svelte || window.Svelte || "
                "document.querySelector('[data-svelte-h]'));"
            )
            return bool(self.webdriver.execute_script(script))
        except Exception as e:
            self.logger.error(f'Error detecting Svelte: {e}')
            return False

    def get_version_string(self):
        """Return the Svelte version string if available."""
        try:
            script = (
                "return (window.__SVELTE_DEVTOOLS_GLOBAL_HOOK__ && "
                "window.__SVELTE_DEVTOOLS_GLOBAL_HOOK__.version) ? "
                "window.__SVELTE_DEVTOOLS_GLOBAL_HOOK__.version : null;"
            )
            return self.webdriver.execute_script(script)
        except Exception as e:
            self.logger.error(f'Error retrieving Svelte version: {e}')
            return None

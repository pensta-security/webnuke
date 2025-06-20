from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger


class CSPUtil:
    """Utility to detect Content Security Policy from meta tags or response headers."""

    def __init__(self, webdriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def get_meta_csp(self):
        """Return the Content-Security-Policy defined in a meta tag if present."""
        try:
            elements = self.webdriver.find_elements(By.XPATH, "//meta[@http-equiv='Content-Security-Policy']")
            for meta in elements:
                content = meta.get_attribute("content")
                if content:
                    return content
        except Exception as e:
            self.logger.error(f"Error reading CSP meta tag: {e}")
        return None

    def get_header_csp(self):
        """Return the CSP from response headers if available on the driver."""
        headers = None
        try:
            headers = getattr(self.webdriver, "last_response_headers", None)
            if headers is None:
                headers = getattr(self.webdriver, "response_headers", None)
            if headers:
                for key in ("Content-Security-Policy", "Content-Security-Policy-Report-Only"):
                    value = headers.get(key)
                    if value:
                        return value
        except Exception as e:
            self.logger.error(f"Error reading CSP headers: {e}")
        return None

    def has_csp(self):
        return bool(self.get_meta_csp() or self.get_header_csp())


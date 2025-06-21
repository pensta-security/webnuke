from libs.utils.logger import FileLogger

class CORSUtil:
    """Utility to inspect CORS related headers."""

    def __init__(self, webdriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def _get_headers(self):
        try:
            headers = getattr(self.webdriver, "last_response_headers", None)
            if headers is None:
                headers = getattr(self.webdriver, "response_headers", None)
            if isinstance(headers, dict):
                return {k.lower(): v for k, v in headers.items()}
        except Exception as e:
            self.logger.error(f"Error retrieving response headers: {e}")
        return {}

    def get_allow_origin(self):
        """Return the value of the Access-Control-Allow-Origin header."""
        return self._get_headers().get("access-control-allow-origin")

    def allows_wildcard(self) -> bool:
        """Return True if ACAO header allows any origin."""
        value = self.get_allow_origin()
        if not value:
            return False
        try:
            return "*" in str(value)
        except Exception as e:
            self.logger.error(f"Error checking CORS header: {e}")
            return False

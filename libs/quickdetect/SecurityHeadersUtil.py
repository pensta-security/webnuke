from libs.utils.logger import FileLogger

class SecurityHeadersUtil:
    """Utility to inspect common security headers on the response."""

    def __init__(self, webdriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def _get_headers(self):
        try:
            headers = getattr(self.webdriver, "last_response_headers", None)
            if headers is None:
                headers = getattr(self.webdriver, "response_headers", None)
            if isinstance(headers, dict):
                # normalize keys to lower-case for easier lookup
                return {k.lower(): v for k, v in headers.items()}
        except Exception as e:
            self.logger.error(f"Error retrieving response headers: {e}")
        return {}

    def has_hsts(self) -> bool:
        return "strict-transport-security" in self._get_headers()

    def has_x_frame_options(self) -> bool:
        return "x-frame-options" in self._get_headers()

    def has_x_content_type_options(self) -> bool:
        return "x-content-type-options" in self._get_headers()

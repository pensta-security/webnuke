import unittest
from libs.quickdetect.SecurityHeadersUtil import SecurityHeadersUtil

class DummyDriver:
    def __init__(self, last_headers=None, response_headers=None):
        if last_headers is not None:
            self.last_response_headers = last_headers
        if response_headers is not None:
            self.response_headers = response_headers

class SecurityHeadersUtilTests(unittest.TestCase):
    def test_has_hsts(self):
        driver = DummyDriver(last_headers={"Strict-Transport-Security": "max-age=31536000"})
        util = SecurityHeadersUtil(driver)
        self.assertTrue(util.has_hsts())
        self.assertFalse(util.has_x_frame_options())
        self.assertFalse(util.has_x_content_type_options())

    def test_header_fallback(self):
        driver = DummyDriver(response_headers={"X-Frame-Options": "DENY"})
        util = SecurityHeadersUtil(driver)
        self.assertTrue(util.has_x_frame_options())
        self.assertFalse(util.has_hsts())

    def test_no_headers(self):
        driver = DummyDriver()
        util = SecurityHeadersUtil(driver)
        self.assertFalse(util.has_hsts())
        self.assertFalse(util.has_x_frame_options())
        self.assertFalse(util.has_x_content_type_options())

if __name__ == '__main__':
    unittest.main()

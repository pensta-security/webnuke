import unittest
from libs.quickdetect.CSPUtil import CSPUtil
from selenium.webdriver.common.by import By


class DummyElement:
    def __init__(self, attrs=None):
        self.attrs = attrs or {}

    def get_attribute(self, name):
        return self.attrs.get(name)


class DummyDriver:
    def __init__(self, elements=None, headers=None):
        self.elements = elements or {}
        self.last_response_headers = headers or {}

    def find_elements(self, by, value):
        if value in self.elements:
            return [DummyElement(self.elements[value])]
        return []


class CSPUtilTests(unittest.TestCase):
    def test_has_csp_meta(self):
        elements = {"//meta[@http-equiv='Content-Security-Policy']": {"content": "default-src 'self'"}}
        driver = DummyDriver(elements)
        util = CSPUtil(driver)
        self.assertTrue(util.has_csp())
        self.assertEqual(util.get_meta_csp(), "default-src 'self'")

    def test_has_csp_header(self):
        driver = DummyDriver(headers={"Content-Security-Policy": "default-src 'self'"})
        util = CSPUtil(driver)
        self.assertTrue(util.has_csp())
        self.assertEqual(util.get_header_csp(), "default-src 'self'")

    def test_no_csp(self):
        driver = DummyDriver()
        util = CSPUtil(driver)
        self.assertFalse(util.has_csp())


if __name__ == '__main__':
    unittest.main()


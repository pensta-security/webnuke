import unittest
from libs.quickdetect.AWSS3Util import AWSS3Util
from selenium.webdriver.common.by import By

class DummyElement:
    def __init__(self, attrs=None):
        self.attrs = attrs or {}
    def get_attribute(self, name):
        return self.attrs.get(name)

class DummyDriver:
    def __init__(self, elements=None):
        self.elements = elements or {}
        self.current_url = 'http://example.com/'
    def find_elements(self, by, value):
        return self.elements.get(value, [])

class AWSS3UtilTests(unittest.TestCase):
    def test_collects_bucket_urls(self):
        elements = {
            "//meta": [DummyElement({'content': 'http://bucket.amazonaws.com/file'})],
            "//img": [DummyElement({'src': 'http://example.com/image'})]
        }
        driver = DummyDriver(elements)
        util = AWSS3Util(driver, driver.current_url)
        self.assertTrue(util.hasS3Buckets())
        self.assertEqual(util.get_bucket_urls(), ['http://bucket.amazonaws.com/file'])

    def test_no_bucket_urls(self):
        elements = {
            "//meta": [DummyElement({'content': 'http://example.com/file'})]
        }
        driver = DummyDriver(elements)
        util = AWSS3Util(driver, driver.current_url)
        self.assertFalse(util.hasS3Buckets())
        self.assertEqual(util.get_bucket_urls(), [])

if __name__ == '__main__':
    unittest.main()

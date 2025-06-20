import unittest
from libs.quickdetect.WordPressUtil import WordPressUtil
from libs.quickdetect.DrupalUtil import DrupalUtil
from selenium.webdriver.common.by import By

class DummyElement:
    def __init__(self, attrs=None):
        self.attrs = attrs or {}
    def get_attribute(self, name):
        return self.attrs.get(name)

class DummyDriver:
    def __init__(self, elements=None):
        self.elements = elements or {}
    def find_element(self, by, value):
        if value in self.elements:
            return DummyElement(self.elements[value])
        raise Exception('not found')
    def execute_script(self, script):
        return None

class WordPressUtilTests(unittest.TestCase):
    def test_is_wordpress_true_when_generator_present(self):
        driver = DummyDriver({'//meta[@name=\'generator\']': {'content': 'WordPress 6.0'}})
        util = WordPressUtil(driver)
        self.assertTrue(util.isWordPress())

    def test_is_wordpress_false_when_generator_missing(self):
        driver = DummyDriver({'//meta[@name=\'generator\']': {'content': None}})
        util = WordPressUtil(driver)
        self.assertFalse(util.isWordPress())

class DrupalUtilTests(unittest.TestCase):
    def test_get_version_string_none_when_no_generator(self):
        driver = DummyDriver()
        util = DrupalUtil(driver)
        self.assertIsNone(util.getVersionString())

if __name__ == '__main__':
    unittest.main()

import unittest
from libs.quickdetect.WordPressUtil import WordPressUtil
from libs.quickdetect.DrupalUtil import DrupalUtil
from libs.quickdetect.WindowNameUtil import WindowNameUtil
from libs.quickdetect.ServiceWorkerUtil import ServiceWorkerUtil
from libs.quickdetect.ReactUtil import ReactUtil
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


class WindowNameUtilTests(unittest.TestCase):
    def test_is_set_true_and_value(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return "payload"
        driver = Driver()
        util = WindowNameUtil(driver)
        self.assertTrue(util.is_set())
        self.assertEqual(util.get_value(), "payload")

    def test_is_set_false_when_empty(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return ""
        driver = Driver()
        util = WindowNameUtil(driver)
        self.assertFalse(util.is_set())


class ServiceWorkerUtilTests(unittest.TestCase):
    def test_service_worker_positive(self):
        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
            def execute_script(self, script):
                return True
            def execute_async_script(self, script):
                if 'active' in script:
                    return True
                return True
        driver = Driver()
        util = ServiceWorkerUtil(driver)
        self.assertTrue(util.is_supported())
        self.assertTrue(util.has_service_worker())
        self.assertTrue(util.is_running())

    def test_service_worker_negative(self):
        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
            def execute_script(self, script):
                return False
            def execute_async_script(self, script):
                return False
        driver = Driver()
        util = ServiceWorkerUtil(driver)
        self.assertFalse(util.is_supported())
        self.assertFalse(util.has_service_worker())
        self.assertFalse(util.is_running())


class ReactUtilTests(unittest.TestCase):
    def test_is_react_positive(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                if 'typeof React' in script:
                    return True
                if 'window.React && window.React.version' in script:
                    return '18.2.0'
        driver = Driver()
        util = ReactUtil(driver)
        self.assertTrue(util.is_react())
        self.assertEqual(util.get_version_string(), '18.2.0')

    def test_is_react_negative(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return None
        driver = Driver()
        util = ReactUtil(driver)
        self.assertFalse(util.is_react())
        self.assertIsNone(util.get_version_string())

if __name__ == '__main__':
    unittest.main()

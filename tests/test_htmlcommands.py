import unittest
from unittest.mock import patch
from libs.htmltools.htmlcommands import HTMLCommands

class DummyElement:
    def __init__(self):
        self.clicked = False
    def click(self):
        self.clicked = True

class DummyDriver:
    def __init__(self):
        self.current_url = 'http://example.com'
        self.visited = []
        self.refreshed = False
    def get(self, url):
        self.visited.append(url)
    def find_elements(self, by, selector):
        return ['el1', 'el2']
    def refresh(self):
        self.refreshed = True

class DummyJS:
    def execute_javascript(self, driver, script):
        pass

class HTMLCommandsUnitTests(unittest.TestCase):
    def setUp(self):
        self.driver = DummyDriver()
        self.cmds = HTMLCommands(self.driver, DummyJS())

    def test_handle_navigation_reload(self):
        elements = self.cmds._handle_navigation('http://start', True)
        self.assertEqual(self.driver.visited, ['http://start'])
        self.assertEqual(elements, ['el1', 'el2'])

    def test_interact_with_element(self):
        elem = DummyElement()
        with patch('time.sleep') as ts:
            self.cmds._interact_with_element(elem)
            ts.assert_called()
        self.assertTrue(elem.clicked)

    def test_handle_click_error_index_break(self):
        do_reload, cont = self.cmds._handle_click_error(IndexError(), 10, 10)
        self.assertFalse(cont)
        self.assertFalse(do_reload)

    def test_handle_click_error_stale(self):
        from selenium.common.exceptions import StaleElementReferenceException
        exc = StaleElementReferenceException()
        do_reload, cont = self.cmds._handle_click_error(exc, 10, 5)
        self.assertTrue(do_reload)
        self.assertTrue(cont)

    def test_refresh_page(self):
        with patch.object(self.cmds.logger, 'log') as log:
            with patch('builtins.input', return_value=''):
                self.cmds.refresh_page()
            log.assert_any_call("Page refreshed")
        self.assertTrue(self.driver.refreshed)

if __name__ == '__main__':
    unittest.main()

import unittest
from libs.xss.xsscommands import XSS_Url_Suggestor, XSSCommands
from unittest.mock import patch
import urllib.parse


class DummyElement:
    def __init__(self, name):
        self.name = name
    def get_attribute(self, attr):
        if attr == "name":
            return self.name
        return None


class DummyDriver:
    def __init__(self):
        self.current_url = "http://example.com/page?foo=1"
        self.page_source = ""
        self.visited = []

    def get(self, url):
        self.visited.append(url)
        self.current_url = url
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        self.page_source = params.get("foo", [""])[0]

    def find_elements(self, *_):
        return [DummyElement("foo"), DummyElement("bar")]


class XSSUrlSuggestorTests(unittest.TestCase):
    def test_xss_url_suggestor_creates_payloads(self):
        url = 'http://example.com/page?param=1&test=2'
        suggestor = XSS_Url_Suggestor(url)
        urls = suggestor.get_xss_urls()
        expected_params = set(['param', 'test'] + suggestor.common_param_names)
        self.assertEqual(len(urls), len(expected_params) * len(suggestor.xss_attacks))
        self.assertTrue(all(u.startswith('http://example.com/page?') for u in urls))

    def test_xss_url_suggestor_no_params(self):
        url = 'http://example.com/page'
        suggestor = XSS_Url_Suggestor(url)
        urls = suggestor.get_xss_urls()
        expected_params = set(suggestor.common_param_names)
        self.assertEqual(len(urls), len(expected_params) * len(suggestor.xss_attacks))
        self.assertTrue(all(u.startswith('http://example.com/page?') for u in urls))


class ReflectedParamTests(unittest.TestCase):
    @patch('libs.xss.xsscommands.wait_for_enter')
    @patch('libs.xss.xsscommands.time.sleep')
    def test_find_reflected_params_logs(self, _sleep, _wait):
        driver = DummyDriver()
        class Logger:
            def __init__(self):
                self.records = []
            def log(self, text):
                self.records.append(text)
            error = log
            debug = log

        logger = Logger()
        cmds = XSSCommands(driver, logger)
        cmds.find_reflected_params("TESTVAL")
        self.assertIn("Reflected parameter found: foo", logger.records)


if __name__ == '__main__':
    unittest.main()

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
        value = params.get("foo", [""])[0]
        self.page_source = f"prefix {value} suffix"

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

    def test_xss_url_suggestor_har_params(self):
        url = 'http://example.com/page'
        har = [{'url': 'http://example.com/api?harparam=1', 'status': 200}]
        suggestor = XSS_Url_Suggestor(url, network_har=har)
        urls = suggestor.get_xss_urls()
        self.assertTrue(any('harparam=' in u for u in urls))


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
        self.assertIn(
            "Reflected parameter found: foo (1x) -> prefix TESTVAL suffix",
            logger.records,
        )
        self.assertIn(
            "  foo (1x): http://example.com/page?foo=TESTVAL", logger.records
        )

    @patch('libs.xss.xsscommands.wait_for_enter')
    @patch('libs.xss.xsscommands.time.sleep')
    def test_find_reflected_params_truncates_line(self, _sleep, _wait):
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
        long_val = "A" * 60
        cmds.find_reflected_params(long_val)
        expected_snippet = f"prefix {long_val} suffix"[:42]
        self.assertIn(
            f"Reflected parameter found: foo (1x) -> {expected_snippet}",
            logger.records,
        )

    @patch('libs.xss.xsscommands.wait_for_enter')
    @patch('libs.xss.xsscommands.time.sleep')
    def test_find_reflected_params_ignores_network_error(self, _sleep, _wait):
        class ErrorDriver(DummyDriver):
            def get(self, url):
                self.visited.append(url)
                self.current_url = url
                self.page_source = 'errorCode":"ERR_NETWORK_CHANGED"'

        driver = ErrorDriver()

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
        self.assertNotIn('Reflected parameter found', ''.join(logger.records))

    @patch('libs.xss.xsscommands.wait_for_enter')
    @patch('libs.xss.xsscommands.time.sleep')
    def test_find_reflected_params_uses_imported_har(self, _sleep, _wait):
        driver = DummyDriver()

        class Logger:
            def __init__(self):
                self.records = []

            def log(self, text):
                self.records.append(text)

            error = log
            debug = log

        logger = Logger()
        har = [{"url": "http://example.com/api?fromhar=1", "status": 200}]
        cmds = XSSCommands(driver, logger, imported_har=har)
        cmds.find_reflected_params("VAL")
        self.assertTrue(any("fromhar=VAL" in url for url in driver.visited))


if __name__ == '__main__':
    unittest.main()

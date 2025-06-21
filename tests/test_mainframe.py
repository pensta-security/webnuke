import unittest
import atexit
import os
import json
from libs.mainmenu.mainframe import mainframe
from libs.utils.networklogger import NetworkLogger

class DummyLogger:
    def log(self, text):
        pass

class DummyDriver:
    def __init__(self):
        self.current_url = ''
    def get(self, url):
        self.current_url = url

    def execute_cdp_cmd(self, *_):
        return None

    def get_log(self, _):
        message = json.dumps({
            "message": {
                "method": "Network.responseReceived",
                "params": {"response": {"url": "http://example.com", "status": 200}}
            }
        })
        return [{"message": message}]

class MainframeHistoryTests(unittest.TestCase):
    def setUp(self):
        class TestMainframe(mainframe):
            def __init__(self_inner, logger):
                super().__init__(logger)
                atexit.unregister(self_inner.curses_util.close_screen)

            def create_browser_instance(self_inner):
                driver = DummyDriver()
                self_inner.network_logger = NetworkLogger(driver, DummyLogger())
                return driver

        # ensure history file is removed
        try:
            os.remove(os.path.join(os.getcwd(), 'history.txt'))
        except FileNotFoundError:
            pass
        self.mf = TestMainframe(DummyLogger())

    def test_open_url_tracks_last_five(self):
        urls = [f'http://example{i}.com' for i in range(6)]
        for url in urls:
            self.mf.open_url(url)
        expected = list(reversed(urls[1:]))[:5]
        self.assertEqual(self.mf.url_history, expected)

    def test_open_url_removes_duplicates(self):
        first = 'http://example.com'
        second = 'http://test.com'
        self.mf.open_url(first)
        self.mf.open_url(second)
        self.mf.open_url(first)
        self.assertEqual(self.mf.url_history[0], first)
        self.assertEqual(self.mf.url_history.count(first), 1)

    def test_history_persisted(self):
        url = 'http://persist.com'
        self.mf.open_url(url)
        # reload mainframe to load history from file
        new_mf = self.mf.__class__(DummyLogger())
        atexit.unregister(new_mf.curses_util.close_screen)
        self.assertIn(url, new_mf.url_history)

    def test_har_written_on_exit(self):
        self.mf.har_path = 'har_out'
        self.mf.open_url('http://example.com')
        self.mf._save_network_har()
        files = os.listdir('har_out')
        self.assertEqual(len(files), 1)
        with open(os.path.join('har_out', files[0]), 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data, [{"url": "http://example.com", "status": 200}])
        os.remove(os.path.join('har_out', files[0]))
        os.rmdir('har_out')

if __name__ == '__main__':
    unittest.main()

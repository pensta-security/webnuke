import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

import quickdetect_cli


class QuickDetectCLITests(unittest.TestCase):
    def _run_cli(self, args):
        with patch.object(sys, 'argv', args):
            quickdetect_cli.main()

    def test_json_stdout(self):
        dummy_lines = ['React Detected', 'Vue.js Detected']

        class DummyQD:
            def __init__(self, screen, driver, curses_util, logger):
                self.screen = screen
            def run(self, screenshot_path=None):
                for msg in dummy_lines:
                    self.screen.lines.append(msg)

        class DummyLogger:
            def log(self, *_):
                pass
            debug = log
            error = log

        class DummyDriver:
            def get(self, url):
                pass

        with patch('quickdetect_cli.FileLogger', return_value=DummyLogger()), \
             patch('quickdetect_cli.WebDriverUtil.getDriver', return_value=DummyDriver()), \
             patch('quickdetect_cli.WebDriverUtil.quit_driver'), \
             patch('quickdetect_cli.QuickDetect', DummyQD):
            buf = io.StringIO()
            with patch('sys.stdout', new=buf):
                self._run_cli(['quickdetect_cli.py', 'http://example.com', '--json'])
            data = json.loads(buf.getvalue())
            self.assertEqual(data['findings'], dummy_lines)

    def test_json_file(self):
        dummy_lines = ['AWS S3 Bucket Detected']

        class DummyQD:
            def __init__(self, screen, driver, curses_util, logger):
                self.screen = screen
            def run(self, screenshot_path=None):
                self.screen.lines.extend(dummy_lines)

        class DummyLogger:
            def log(self, *_):
                pass
            debug = log
            error = log

        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tf:
            out_path = tf.name
        try:
            class DummyDriver:
                def get(self, url):
                    pass

            with patch('quickdetect_cli.FileLogger', return_value=DummyLogger()), \
                 patch('quickdetect_cli.WebDriverUtil.getDriver', return_value=DummyDriver()), \
                 patch('quickdetect_cli.WebDriverUtil.quit_driver'), \
                 patch('quickdetect_cli.QuickDetect', DummyQD):
                self._run_cli(['quickdetect_cli.py', 'http://example.com', '--json', out_path])
            with open(out_path) as f:
                data = json.load(f)
            self.assertEqual(data['findings'], dummy_lines)
        finally:
            import os
            os.remove(out_path)

    def test_url_file_and_json(self):
        dummy_lines = ['Tech Detected']
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tf:
            tf.write('http://one.com\nhttp://two.com\n')
            url_file = tf.name
        try:
            class DummyQD:
                def __init__(self, screen, driver, curses_util, logger):
                    self.screen = screen
                def run(self, screenshot_path=None):
                    self.screen.lines.extend(dummy_lines)
                def get_network_har(self, path=None):
                    return []

            class DummyLogger:
                def log(self, *_):
                    pass
                debug = log
                error = log

            class DummyDriver:
                def get(self, url):
                    pass

            with patch('quickdetect_cli.FileLogger', return_value=DummyLogger()), \
                 patch('quickdetect_cli.WebDriverUtil.getDriver', return_value=DummyDriver()), \
                 patch('quickdetect_cli.WebDriverUtil.quit_driver'), \
                 patch('quickdetect_cli.QuickDetect', DummyQD):
                buf = io.StringIO()
                with patch('sys.stdout', new=buf):
                    self._run_cli(['quickdetect_cli.py', '--url-file', url_file, '--json'])
                data = json.loads(buf.getvalue())
                self.assertIn('results', data)
                self.assertEqual(len(data['results']), 2)
                for entry in data['results']:
                    self.assertEqual(entry['findings'], dummy_lines)
        finally:
            import os
            os.remove(url_file)

    def test_har_output(self):
        dummy_lines = ['Info']
        dummy_har = [{'url': 'http://example.com', 'status': 200}]

        class DummyQD:
            def __init__(self, screen, driver, curses_util, logger):
                self.screen = screen
            def run(self, screenshot_path=None):
                self.screen.lines.extend(dummy_lines)
            def get_network_har(self, path=None):
                return dummy_har

        class DummyLogger:
            def log(self, *_):
                pass
            debug = log
            error = log

        class DummyDriver:
            def get(self, url):
                pass

        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tf:
            har_path = tf.name
        try:
            with patch('quickdetect_cli.FileLogger', return_value=DummyLogger()), \
                 patch('quickdetect_cli.WebDriverUtil.getDriver', return_value=DummyDriver()), \
                 patch('quickdetect_cli.WebDriverUtil.quit_driver'), \
                 patch('quickdetect_cli.QuickDetect', DummyQD):
                self._run_cli(['quickdetect_cli.py', 'http://example.com', '--har', har_path])
            with open(har_path) as f:
                data = json.load(f)
            self.assertEqual(data, dummy_har)
        finally:
            import os
            os.remove(har_path)


if __name__ == '__main__':
    unittest.main()

import tempfile
import unittest
from libs.utils.logger import FileLogger
from libs.quickdetect.AngularUtil import find_urls_from_source_code
from libs.utils.networklogger import NetworkLogger
import json


class UtilsTests(unittest.TestCase):
    def test_file_logger_writes_to_file(self):
        log = FileLogger()
        with tempfile.NamedTemporaryFile(mode="r+") as tf:
            log.log_path = tf.name
            log.log("hello")
            tf.seek(0)
            contents = tf.read()
        self.assertIn("hello", contents)

    def test_find_urls_from_source_code(self):
        source = "var a = '/foo'; fetch('/bar');"
        urls = find_urls_from_source_code(source)
        self.assertIn("'/foo';", urls)
        self.assertIn("fetch('/bar');", urls)

    def test_network_logger_filters_entries(self):
        message = json.dumps({
            "message": {
                "method": "Network.requestWillBeSent",
                "params": {"request": {"url": "http://example.com"}}
            }
        })

        class Driver:
            def execute_cdp_cmd(self, *_):
                return None

            def get_log(self, _):
                return [{"message": message}]

        logger = NetworkLogger(Driver())
        entries = logger.get_log()
        self.assertTrue(entries)
        self.assertEqual(entries[0]["method"], "Network.requestWillBeSent")

    def test_network_logger_har_generation(self):
        message = json.dumps({
            "message": {
                "method": "Network.responseReceived",
                "params": {
                    "response": {
                        "url": "http://example.com",
                        "status": 200
                    }
                }
            }
        })

        class Driver:
            def execute_cdp_cmd(self, *_):
                return None

            def get_log(self, _):
                return [{"message": message}]

        logger = NetworkLogger(Driver())
        har = logger.get_har()
        self.assertEqual(har, [{"url": "http://example.com", "status": 200}])


if __name__ == '__main__':
    unittest.main()

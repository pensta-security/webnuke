import tempfile
import unittest
from libs.utils.logger import FileLogger
from libs.quickdetect.AngularUtil import find_urls_from_source_code


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


if __name__ == '__main__':
    unittest.main()

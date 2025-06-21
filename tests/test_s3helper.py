import unittest
from libs.aws.s3_helper import find_s3_urls

class DummyElement:
    def __init__(self, attrs=None):
        self.attrs = attrs or {}
    def get_attribute(self, name):
        return self.attrs.get(name)

class DummyDriver:
    def __init__(self, elements=None):
        self.elements = elements or {}
    def find_elements(self, by, value):
        return self.elements.get(value, [])

class S3HelperTests(unittest.TestCase):
    def test_finds_bucket_urls(self):
        elements = {
            "//meta": [DummyElement({'content': 'http://bucket.amazonaws.com/file'})],
            "//img": [DummyElement({'src': 'http://example.com/img'})]
        }
        driver = DummyDriver(elements)
        urls = find_s3_urls(driver)
        self.assertEqual(urls, ['http://bucket.amazonaws.com/file'])

    def test_returns_empty_when_no_buckets(self):
        elements = {
            "//meta": [DummyElement({'content': 'http://example.com/file'})]
        }
        driver = DummyDriver(elements)
        urls = find_s3_urls(driver)
        self.assertEqual(urls, [])

if __name__ == '__main__':
    unittest.main()

import unittest
from libs.xss.xsscommands import XSS_Url_Suggestor


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


if __name__ == '__main__':
    unittest.main()

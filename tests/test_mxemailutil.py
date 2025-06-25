import unittest
from unittest.mock import patch

from libs.quickdetect.MXEmailUtil import MXEmailUtil
from libs.quickdetect.O365Util import O365Util


class DummyLogger:
    def log(self, *_):
        pass
    debug = log
    error = log


class MXEmailUtilTests(unittest.TestCase):
    def test_provider_detects_outlook_multilevel_tld(self):
        util = MXEmailUtil("https://www.example.co.uk", DummyLogger())
        captured = {}

        def fake_query(domain):
            captured['domain'] = domain
            return ["example-co-uk.mail.protection.outlook.com"]

        util._query_mx_records = fake_query
        provider = util.get_provider()
        self.assertEqual(provider, "Office 365")
        self.assertEqual(captured['domain'], "example.co.uk")


class O365UtilTests(unittest.TestCase):
    def test_domain_uses_office365_multilevel_tld(self):
        class DummyDriver:
            pass

        util = O365Util(DummyDriver(), "https://www.example.co.uk", DummyLogger())

        class Ans:
            def __init__(self, val):
                self.exchange = val

        with patch('dns.resolver.resolve', return_value=[Ans('example-co-uk.mail.protection.outlook.com')]) as res, \
             patch('subprocess.check_output', return_value=""):
            self.assertTrue(util.domain_uses_office365())
            self.assertEqual(res.call_args[0][0], "example.co.uk")


if __name__ == '__main__':
    unittest.main()

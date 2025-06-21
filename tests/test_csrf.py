import json
import os
import tempfile
import unittest
from libs.csrf.csrfcommands import CSRFCommands


class DummyDriver:
    def __init__(self, data=None):
        self.data = data
        self.opened = None
    def execute_script(self, script):
        # return stored data when fetching from localStorage
        if script.startswith("return"):
            return self.data
    def get(self, url):
        self.opened = url


class DummyJS:
    def execute_javascript(self, driver, script):
        driver.injected = script


class CSRFCommandsTests(unittest.TestCase):
    def test_create_returns_false_when_no_data(self):
        cmds = CSRFCommands(DummyDriver(), DummyJS())
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.html')
            with unittest.mock.patch('builtins.input', return_value=''):
                self.assertFalse(cmds.create_csrf_poc(path))
            self.assertFalse(os.path.exists(path))

    def test_create_writes_file(self):
        form = {"action": "/post", "method": "POST", "data": {"a": "1"}}
        data = json.dumps(form)
        driver = DummyDriver(data)
        cmds = CSRFCommands(driver, DummyJS())
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.html')
            with unittest.mock.patch('builtins.input', return_value=''):
                self.assertTrue(cmds.create_csrf_poc(path))
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            self.assertIn("/post", content)
            self.assertIn("name='a'", content)


if __name__ == '__main__':
    unittest.main()

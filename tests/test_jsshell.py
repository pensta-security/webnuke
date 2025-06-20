import unittest
import io
from contextlib import redirect_stdout
from libs.javascript.jsshell import JSShell

class DummyDriver:
    def __init__(self, entries=None):
        self.entries = entries or []
    def execute_script(self, script):
        return self.entries

class JSShellTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {'name': 'foo', 'type': 'string', 'size': 3},
            {'name': 'bar', 'type': 'function', 'size': 10}
        ]
        self.driver = DummyDriver(self.entries)
        self.shell = JSShell(self.driver)

    def test_ls_lists_names(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.shell.handle_command('ls')
        output = buf.getvalue().splitlines()
        self.assertIn('foo', output)
        self.assertIn('bar()', output)

    def test_ls_la_shows_sizes(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.shell.handle_command('ls -la')
        output = buf.getvalue().splitlines()
        self.assertIn('foo\t3', output)
        self.assertIn('bar()\t10', output)

if __name__ == '__main__':
    unittest.main()

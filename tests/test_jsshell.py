import unittest
import io
from contextlib import redirect_stdout
from libs.javascript.jsshell import JSShell

class DummyDriver:
    def __init__(self, entries=None):
        self.entries = entries or []
        self.current_url = ''
    def execute_script(self, script):
        return self.entries
    def get(self, url):
        self.current_url = url

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
        expected_foo = f"{JSShell.COLOR_FILE}foo{JSShell.COLOR_RESET}"
        expected_bar = f"{JSShell.COLOR_EXECUTABLE}bar(){JSShell.COLOR_RESET}"
        self.assertIn(expected_foo, output)
        self.assertIn(expected_bar, output)

    def test_ls_la_shows_sizes(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.shell.handle_command('ls -la')
        output = buf.getvalue().splitlines()
        expected_foo = f"{JSShell.COLOR_FILE}foo{JSShell.COLOR_RESET}\t3"
        expected_bar = f"{JSShell.COLOR_EXECUTABLE}bar(){JSShell.COLOR_RESET}\t10"
        self.assertIn(expected_foo, output)
        self.assertIn(expected_bar, output)

    def test_goto_navigates(self):
        url = 'https://example.com'
        self.shell.handle_command(f'goto {url}')
        self.assertEqual(self.driver.current_url, url)
        self.assertEqual(self.shell.cwd, 'this')

if __name__ == '__main__':
    unittest.main()

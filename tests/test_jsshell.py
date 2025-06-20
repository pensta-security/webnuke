import unittest
import io
import os
import tempfile
from contextlib import redirect_stdout
from unittest.mock import patch
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
        self.history = []
        def cb(url):
            self.history.append(url)
            self.driver.get(url)
        self.shell = JSShell(self.driver, cb)

    def test_builtin_color(self):
        self.shell.builtins = {'foo'}
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.shell.handle_command('ls')
        output = buf.getvalue().splitlines()
        expected_foo = f"{JSShell.COLOR_BUILTIN}foo{JSShell.COLOR_RESET}"
        self.assertIn(expected_foo, output)

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

    def test_goto_updates_history(self):
        url = 'https://example.org'
        self.shell.handle_command(f'goto {url}')
        self.assertIn(url, self.history)

    def test_command_autocomplete(self):
        with patch('readline.get_line_buffer', return_value='l'):
            completions = []
            i = 0
            while True:
                res = self.shell.complete('l', i)
                if res is None:
                    break
                completions.append(res)
                i += 1
        self.assertIn('ls', completions)
        self.assertIn('ls -la', completions)

    def test_property_autocomplete(self):
        with patch('readline.get_line_buffer', return_value='cd f'), \
             patch.object(self.shell, 'get_property_names', return_value=['foo', 'bar']):
            completions = []
            i = 0
            while True:
                res = self.shell.complete('f', i)
                if res is None:
                    break
                completions.append(res)
                i += 1
        self.assertEqual(completions, ['foo'])

    def test_nested_property_autocomplete(self):
        with patch('readline.get_line_buffer', return_value='cat obj/'), \
             patch.object(self.shell, 'get_property_names', return_value=['inner', 'leaf']):
            completions = []
            i = 0
            while True:
                res = self.shell.complete('', i)
                if res is None:
                    break
                completions.append(res)
                i += 1
        self.assertEqual(completions, ['obj/inner', 'obj/leaf'])

    def test_custom_scripts_loaded(self):
        class CaptureDriver(DummyDriver):
            def __init__(self):
                super().__init__([])
                self.scripts = []
            def execute_script(self, script):
                self.scripts.append(script)
                return []

        with tempfile.TemporaryDirectory() as tmpdir:
            js_path = os.path.join(tmpdir, 'custom.js')
            with open(js_path, 'w', encoding='utf-8') as fh:
                fh.write('window.wn_custom = function(){};')
            driver = CaptureDriver()
            shell = JSShell(driver, custom_dir=tmpdir)
            shell.inject_custom_scripts()
            self.assertTrue(driver.scripts)

if __name__ == '__main__':
    unittest.main()

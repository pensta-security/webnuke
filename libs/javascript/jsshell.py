import readline
import os


class JSShell:
    COLOR_RESET = '\033[0m'
    COLOR_FOLDER = '\033[94m'
    COLOR_EXECUTABLE = '\033[92m'
    COLOR_FILE = '\033[0m'
    COLOR_BUILTIN = '\033[95m'

    COMMANDS = ['cd', 'pwd', 'cat', 'bash', 'goto', 'man', 'ls', 'ls -la', 'exit', 'quit']

    def __init__(self, webdriver, url_callback=None, custom_dir='/opt/webnuke'):
        self.driver = webdriver
        self.url_callback = url_callback
        self.custom_dir = custom_dir
        # start at the root of the javascript context
        self.cwd = 'this'
        self.builtins = set()

        builtin_path = os.path.join(os.path.dirname(__file__), 'browser_builtins.txt')
        if os.path.exists(builtin_path):
            with open(builtin_path, 'r') as fh:
                self.builtins = {line.strip() for line in fh if line.strip()}

        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')

    def inject_custom_scripts(self) -> None:
        """Load and execute any JavaScript files from custom_dir."""
        if not os.path.isdir(self.custom_dir):
            return
        for name in os.listdir(self.custom_dir):
            if not name.endswith('.js'):
                continue
            path = os.path.join(self.custom_dir, name)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    script = fh.read()
                self.driver.execute_script(script)
            except Exception as e:
                print(f'Failed loading {path}: {e}')

    def _display_path(self) -> str:
        """Return a filesystem-like representation of the current path."""
        if self.cwd in ('this', 'window'):
            return '/'
        path = self.cwd
        if path.startswith('this.'):
            path = path[len('this.'):]
        elif path == 'this':
            path = ''
        return '/' + path.replace('.', '/')

    def run(self):
        print('Webnuke Javascript Shell. Type "exit" to return.')
        self.inject_custom_scripts()
        while True:
            try:
                cmd = input(f'{self._display_path()}> ').strip()
            except EOFError:
                break
            if cmd in ('exit', 'quit'):
                break
            if not cmd:
                continue
            try:
                self.handle_command(cmd)
            except Exception as e:
                print(f'Error: {e}')

    def handle_command(self, cmd):
        if cmd.startswith('cd '):
            self.change_dir(cmd[3:].strip())
        elif cmd == 'pwd':
            print(self._display_path())
        elif cmd.startswith('cat '):
            self.cat_property(cmd[4:].strip())
        elif cmd.startswith('bash '):
            self.run_js(cmd[5:].strip())
        elif cmd.startswith('goto '):
            self.goto_url(cmd[5:].strip())
        elif cmd.startswith('man '):
            self.show_function_help(cmd[4:].strip())
        elif cmd == 'ls':
            self.list_dir()
        elif cmd == 'ls -la':
            self.list_dir(long_format=True)
        else:
            print('Unknown command')

    def change_dir(self, path):
        if path in ('/', 'this', 'window'):
            # going to the root of the javascript context
            self.cwd = 'this'
            return
        if path == '..':
            parts = self.cwd.split('.')
            if len(parts) > 1:
                self.cwd = '.'.join(parts[:-1])
            else:
                self.cwd = 'this'
            return
        # allow paths relative to current working object
        path = path.replace('/', '.')
        new_path = path if path.startswith(('this', 'window')) else f'{self.cwd}.{path}'
        exists = self.driver.execute_script(f'return typeof {new_path} !== "undefined";')
        if exists:
            self.cwd = new_path
        else:
            print('Path does not exist')

    def _resolve_js_path(self, path: str) -> str:
        """Return a javascript path relative to the current working object."""
        if not path:
            return self.cwd
        path = path.replace('/', '.')
        if path.startswith(('this', 'window')):
            return path
        if self.cwd in ('this', 'window'):
            return f"{self.cwd}.{path}"
        return f"{self.cwd}.{path}"

    def cat_property(self, prop):
        script = f'return {self._resolve_js_path(prop)};'
        result = self.driver.execute_script(script)
        print(result)

    def run_js(self, js):
        script = f'with({self.cwd}){{ {js}; }}'
        self.driver.execute_script(script)

    def goto_url(self, url: str) -> None:
        if not url:
            print('Usage: goto <url>')
            return
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
        try:
            if self.url_callback:
                self.url_callback(url)
            else:
                self.driver.get(url)
            self.cwd = 'this'
        except Exception as e:
            print(f'Error loading URL: {e}')

    def show_function_help(self, fn):
        script = f'try{{return {self.cwd}.{fn}.toString();}}catch(e){{return null;}}'
        result = self.driver.execute_script(script)
        if result:
            first_line = result.split('\n', 1)[0]
            if '(' in first_line and ')' in first_line:
                args = first_line[first_line.find('(')+1:first_line.find(')')]
                print(f'Arguments: {args}')
            print(result)
        else:
            print('Function not found')

    def _colorize_name(self, name: str, type_: str) -> str:
        base_name = name.split('(')[0].rstrip('/')
        if base_name in self.builtins:
            color = self.COLOR_BUILTIN
        elif type_ == 'object':
            color = self.COLOR_FOLDER
        elif type_ == 'function':
            color = self.COLOR_EXECUTABLE
        else:
            color = self.COLOR_FILE
        return f"{color}{name}{self.COLOR_RESET}"

    def get_property_names(self, path: str | None = None):
        target = self._resolve_js_path(path or '')
        script = f"""
var obj;
try {{
    obj = {target};
}} catch(e) {{
    obj = undefined;
}}
var result = [];
if (obj) {{
    for (var prop in obj) {{
        result.push(prop);
    }}
}}
return result;
"""
        return self.driver.execute_script(script)

    def complete(self, text, state):
        line = readline.get_line_buffer()
        tokens = line.split()
        if len(tokens) <= 1 and not line.endswith(' '):
            options = [cmd for cmd in self.COMMANDS if cmd.startswith(text)]
        else:
            path_token = tokens[-1]
            sep_index = max(path_token.rfind('/'), path_token.rfind('.'))
            if sep_index != -1:
                obj_part = path_token[:sep_index]
                prefix = path_token[sep_index+1:]
            else:
                obj_part = ''
                prefix = path_token
            try:
                properties = self.get_property_names(obj_part)
            except Exception:
                properties = []
            base = obj_part + ('/' if obj_part else '')
            options = [base + p for p in properties if p.startswith(prefix)]
        options.sort()
        if state < len(options):
            return options[state]
        return None

    def list_dir(self, long_format: bool = False) -> None:
        script = f"""
var obj = {self.cwd};
var result = [];
for (var prop in obj) {{
    try {{
        var val = obj[prop];
        var type = typeof val;
        var size = type === 'function' ? val.toString().length : String(val).length;
        result.push({{name: prop, type: type, size: size}});
    }} catch(e) {{
        result.push({{name: prop, type: 'unknown', size: 0}});
    }}
}}
return result.sort(function(a, b) {{return a.name.localeCompare(b.name);}});
"""
        entries = self.driver.execute_script(script)
        for entry in entries:
            name = entry['name']
            if entry['type'] == 'function':
                name += '()'
            elif entry['type'] == 'object':
                name += '/'

            colored_name = self._colorize_name(name, entry['type'])

            if long_format:
                print(f"{colored_name}\t{entry['size']}")
            else:
                print(colored_name)

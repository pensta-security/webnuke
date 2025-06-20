import readline


class JSShell:
    COLOR_RESET = '\033[0m'
    COLOR_FOLDER = '\033[94m'
    COLOR_EXECUTABLE = '\033[92m'
    COLOR_FILE = '\033[0m'

    COMMANDS = ['cd', 'pwd', 'cat', 'bash', 'goto', 'man', 'ls', 'ls -la', 'exit', 'quit']

    def __init__(self, webdriver):
        self.driver = webdriver
        # start at the root of the javascript context
        self.cwd = 'this'

        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')

    def run(self):
        print('Webnuke Javascript Shell. Type "exit" to return.')
        while True:
            try:
                cmd = input(f'{self.cwd}> ').strip()
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
            print(self.cwd)
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
        new_path = path if path.startswith(('this', 'window')) else f'{self.cwd}.{path}'
        exists = self.driver.execute_script(f'return typeof {new_path} !== "undefined";')
        if exists:
            self.cwd = new_path
        else:
            print('Path does not exist')

    def cat_property(self, prop):
        script = f'return {self.cwd}.{prop};'
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
        if type_ == 'object':
            color = self.COLOR_FOLDER
        elif type_ == 'function':
            color = self.COLOR_EXECUTABLE
        else:
            color = self.COLOR_FILE
        return f"{color}{name}{self.COLOR_RESET}"

    def get_property_names(self):
        script = f"""
var obj = {self.cwd};
var result = [];
for (var prop in obj) {{
    result.push(prop);
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
            try:
                properties = self.get_property_names()
            except Exception:
                properties = []
            options = [p for p in properties if p.startswith(text)]
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

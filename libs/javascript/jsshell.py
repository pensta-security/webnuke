class JSShell:
    def __init__(self, webdriver):
        self.driver = webdriver
        self.cwd = 'window'

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
        elif cmd.startswith('man '):
            self.show_function_help(cmd[4:].strip())
        elif cmd == 'ls':
            self.list_dir()
        elif cmd == 'ls -la':
            self.list_dir(long_format=True)
        else:
            print('Unknown command')

    def change_dir(self, path):
        if path in ('/', 'window'):
            self.cwd = 'window'
            return
        if path == '..':
            parts = self.cwd.split('.')
            if len(parts) > 1:
                self.cwd = '.'.join(parts[:-1])
            else:
                self.cwd = 'window'
            return
        new_path = path if path.startswith('window') else f'{self.cwd}.{path}'
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
            if long_format:
                print(f"{name}\t{entry['size']}")
            else:
                print(name)

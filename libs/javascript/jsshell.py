import readline
import os
import sys
import io
from contextlib import redirect_stdout


class JSShell:
    COLOR_RESET = '\033[0m'
    COLOR_FOLDER = '\033[94m'
    COLOR_EXECUTABLE = '\033[92m'
    COLOR_FILE = '\033[0m'
    COLOR_BUILTIN = '\033[95m'

    COMMANDS = ['cd', 'pwd', 'cat', 'bash', 'goto', 'man', 'ls', 'ls -la', 'script', 'exit', 'quit']

    def __init__(self, webdriver, url_callback=None, custom_dir='/opt/webnuke'):
        self.driver = webdriver
        self.url_callback = url_callback
        self.custom_dir = custom_dir
        # start at the root of the javascript context
        self.cwd = 'this'
        # track /proc path when browsing events
        self.proc_path = None
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

    def _install_console(self) -> None:
        """Install a custom console object that records output and errors."""
        script = """
if (!window.webnukeConsoleInstalled) {
    window.webnukeConsoleInstalled = true;
    window.console = {
        log: function(d){ this.output.push(d); },
        warn: function(d){ this.output.push('WARN: ' + d); },
        error: function(d){ this.output.push('ERROR: ' + d); },
        output: [],
        flushOutput: function(){ var o = this.output; this.output = []; return o; }
    };
    window.addEventListener('error', function(e){ window.console.error(e.message); });
    window.addEventListener('unhandledrejection', function(e){ window.console.error(e.reason); });
}
"""
        try:
            self.driver.execute_script(script)
        except Exception:
            pass

    def _display_path(self) -> str:
        """Return a filesystem-like representation of the current path."""
        if self.proc_path is not None:
            if self.proc_path:
                return '/proc/' + self.proc_path
            return '/proc'
        if self.cwd in ('this', 'window'):
            return '/'
        path = self.cwd
        if path.startswith('this.'):
            path = path[len('this.') :]
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
        elif cmd.startswith('script'):
            parts = cmd.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else 'typescript'
            self.script_session(filename)
        else:
            print('Unknown command')

    def change_dir(self, path):
        if path.startswith('/proc'):
            self.proc_path = path[len('/proc'):].strip('/')
            return
        if self.proc_path is not None:
            if path == '..':
                if self.proc_path:
                    self.proc_path = '/'.join(self.proc_path.split('/')[:-1])
                else:
                    self.proc_path = None
                return
            if path.startswith('/'):
                if path.startswith('/proc'):
                    self.proc_path = path[len('/proc'):].strip('/')
                else:
                    self.proc_path = None
                    self.change_dir(path.lstrip('/'))
                return
            self.proc_path = '/'.join(filter(None, [self.proc_path, path]))
            return
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
        if self.proc_path is not None or prop.startswith('/proc'):
            full_path = prop
            if not full_path.startswith('/proc'):
                base = self.proc_path or ''
                full_path = '/'.join(filter(None, ['/proc', base, prop]))
            result = self._proc_cat(full_path[len('/proc'):].strip('/'))
            if result is None:
                print('Path does not exist')
            else:
                print(result)
            return
        script = f'return {self._resolve_js_path(prop)};'
        result = self.driver.execute_script(script)
        print(result)

    def run_js(self, js):
        if self.proc_path is not None or js.startswith('/proc'):
            full_path = js
            if not full_path.startswith('/proc'):
                base = self.proc_path or ''
                full_path = '/'.join(filter(None, ['/proc', base, js]))
            output = self._proc_run(full_path[len('/proc'):].strip('/'))
            if output is not None:
                print(output)
            return
        self._install_console()
        script = f"""var callback = arguments[0];
try {{
    with({self.cwd}){{ {js}; }}
}} catch(e) {{
    console.error(e);
}}
setTimeout(function(){{ callback(window.console.flushOutput()); }}, 0);"""
        result = self.driver.execute_async_script(script)
        if isinstance(result, list):
            for line in result:
                print(line)

    def script_session(self, filename: str) -> None:
        """Run an interactive shell logging all input and output to a file."""
        print(f'Recording session to {filename}. Type "exit" to stop.')
        try:
            with open(filename, 'w', encoding='utf-8') as fh:
                while True:
                    try:
                        prompt = f'{self._display_path()}> '
                        cmd = input(prompt)
                    except EOFError:
                        break
                    fh.write(f'{prompt}{cmd}\n')
                    fh.flush()
                    stripped = cmd.strip()
                    if stripped in ("exit", "quit"):
                        break
                    if not stripped:
                        continue
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        try:
                            self.handle_command(stripped)
                        except Exception as e:
                            print(f'Error: {e}')
                    output = buf.getvalue()
                    fh.write(output)
                    fh.flush()
                    print(output, end='')
        except Exception as e:
            print(f'Error starting script session: {e}')

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
        if self.proc_path is not None:
            entries = self._proc_list_dir(self.proc_path)
            if entries is None:
                print('Path does not exist')
                return
            for entry in entries:
                name = entry['name']
                if entry['type'] == 'function':
                    name += '()'
                elif entry['type'] == 'object':
                    name += '/'
                colored_name = self._colorize_name(name, entry['type'])
                if long_format:
                    print(f"{colored_name}\t{entry.get('size', 0)}")
                else:
                    print(colored_name)
            return

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

    # ----- /proc helper methods -----
    def _proc_list_dir(self, path: str):
        """Return directory entries for a given /proc path."""
        path = path.strip('/')
        if not path:
            forms = self.driver.execute_script('return document.forms.length;')
            entries = [{'name': f'form_{i}', 'type': 'object'} for i in range(forms)]
            has_window = self.driver.execute_script("""
for(var k in window){ if(k.startsWith('on') && typeof window[k]==='function'){ return true; }}
return false;
""")
            if has_window:
                entries.append({'name': 'window', 'type': 'object'})
            count = self.driver.execute_async_script("""
var cb = arguments[0];
if(navigator.serviceWorker && navigator.serviceWorker.getRegistrations){
    navigator.serviceWorker.getRegistrations().then(r=>cb(r.length)).catch(()=>cb(0));
}else cb(0);
""")
            for i in range(count):
                entries.append({'name': f'service_worker_{i}', 'type': 'object'})
            return entries

        parts = path.split('/')
        if parts[0].startswith('form_'):
            idx = int(parts[0].split('_')[1])
            if len(parts) == 1:
                names = self.driver.execute_script(f"""
var f=document.forms[{idx}];
if(!f) return [];
var r=[];
for(var i=0;i<f.elements.length;i++){{
    var e=f.elements[i];
    var n=e.name||e.id||'element_'+i;
    for(var k in e){{if(k.startsWith('on') && typeof e[k]==='function'){{r.push(n);break;}}}}
}}
return r;
""")
                return [{'name': n, 'type': 'object'} for n in names]
            else:
                elname = parts[1]
                events = self.driver.execute_script(f"""
var form=document.forms[{idx}];
if(!form) return [];
var el=null;
if(form['{elname}']) el=form['{elname}'];
else{{for(var i=0;i<form.elements.length;i++){{var e=form.elements[i]; if((e.name||e.id||'element_'+i)=='{elname}'){{el=e;break;}}}}}}
if(!el) return [];
var res=[];
for(var p in el){{ if(p.startsWith('on') && typeof el[p]==='function') res.push(p); }}
return res;
""")
                return [{'name': ev, 'type': 'function'} for ev in events]
        elif parts[0] == 'window':
            if len(parts) == 1:
                events = self.driver.execute_script("""
var res=[];
for(var k in window){ if(k.startsWith('on') && typeof window[k]==='function') res.push(k); }
return res;
""")
                return [{'name': ev, 'type': 'function'} for ev in events]
        # service worker directories have no children
        return []

    def _proc_cat(self, path: str):
        parts = path.split('/')
        if parts[0].startswith('form_') and len(parts) == 3:
            idx = int(parts[0].split('_')[1])
            elname = parts[1]
            event = parts[2]
            script = (
                "var form=document.forms[{idx}];\n"
                "if(!form) return null;\n"
                "var el=null;\n"
                "if(form['{elname}']) el=form['{elname}'];\n"
                "else{for(var i=0;i<form.elements.length;i++){var e=form.elements[i]; if((e.name||e.id||'element_'+i)=='{elname}'){el=e;break;}}}\n"
                "if(el && typeof el['{event}']==='function') return el['{event}'].toString();\n"
                "return null;"
            ).format(idx=idx, elname=elname, event=event)
            return self.driver.execute_script(script)
        if parts[0] == 'window' and len(parts) == 2:
            event = parts[1]
            script = f"if(typeof window['{event}']==='function') return window['{event}'].toString(); return null;"
            return self.driver.execute_script(script)
        if parts[0].startswith('service_worker_') and len(parts) == 1:
            idx = int(parts[0].split('_')[2]) if '_' in parts[0] else 0
            urls = self.driver.execute_async_script("""
var cb=arguments[0];
if(navigator.serviceWorker && navigator.serviceWorker.getRegistrations){
    navigator.serviceWorker.getRegistrations().then(function(r){var u=r[{0}] && r[{0}].active ? r[{0}].active.scriptURL : null; cb(u);}).catch(function(){cb(null);});
}else cb(null);
""".format(idx))
            return urls
        return None

    def _proc_run(self, path: str):
        parts = path.split('/')
        if parts[0].startswith('form_') and len(parts) == 3:
            idx = int(parts[0].split('_')[1])
            elname = parts[1]
            event = parts[2]
            script = (
                "var form=document.forms[{idx}];\n"
                "var el=null;\n"
                "if(form && form['{elname}']) el=form['{elname}'];\n"
                "if(!el && form){for(var i=0;i<form.elements.length;i++){var e=form.elements[i]; if((e.name||e.id||'element_'+i)=='{elname}'){el=e;break;}}}\n"
                "if(el && typeof el['{event}']==='function'){ el['{event}'](); }"
            ).format(idx=idx, elname=elname, event=event)
            return self.driver.execute_script(script)
        if parts[0] == 'window' and len(parts) == 2:
            event = parts[1]
            script = f"if(typeof window['{event}']==='function') window['{event}']();"
            return self.driver.execute_script(script)
        return None

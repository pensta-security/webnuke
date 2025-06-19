from selenium.webdriver.common.by import By

class SitecoreUtil:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def _get_meta_generator(self):
        try:
            element = self.webdriver.find_element(By.XPATH, "//meta[@name='generator']")
            return element.get_attribute("content") or ""
        except Exception:
            return ""

    def is_sitecore(self):
        # Check meta generator tag
        generator = self._get_meta_generator()
        if generator and 'sitecore' in generator.lower():
            return True
        # Check for global Sitecore JS object
        try:
            result = self.webdriver.execute_script("return typeof Sitecore !== 'undefined'")
            if result:
                return True
        except Exception:
            pass
        # Check page source for common Sitecore markers
        try:
            source = self.webdriver.page_source.lower()
            if 'sc_site' in source or 'sc_itemid' in source or '/-/media/' in source:
                return True
        except Exception:
            pass
        return False

    def get_version_string(self):
        generator = self._get_meta_generator()
        if generator and 'sitecore' in generator.lower():
            return generator
        return None

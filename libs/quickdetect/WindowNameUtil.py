class WindowNameUtil:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def is_set(self):
        try:
            value = self.webdriver.execute_script("return window.name")
            return bool(value)
        except Exception:
            return False

    def get_value(self):
        try:
            return self.webdriver.execute_script("return window.name")
        except Exception:
            return None

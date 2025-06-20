class OnMessageUtil:
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def is_set(self):
        try:
            return bool(self.webdriver.execute_script("return !!window.onmessage"))
        except Exception:
            return False

    def checks_origin(self):
        try:
            script = "return window.onmessage && window.onmessage.toString()"
            handler = self.webdriver.execute_script(script)
            if not handler:
                return False
            return 'origin' in handler
        except Exception:
            return False

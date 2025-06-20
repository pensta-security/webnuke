class DojoUtil:
    def __init__(self, webdriver):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver

    def is_dojo(self):
        try:
            script = (
                "return (window.dojo && window.dojo.version) ? "
                "window.dojo.version : null;"
            )
            result = self.webdriver.execute_script(script)
            return bool(result)
        except Exception:
            return False

    def getVersionString(self):
        try:
            script = (
                "return (window.dojo && window.dojo.version) ? "
                "window.dojo.version : null;"
            )
            result = self.webdriver.execute_script(script)
            if isinstance(result, dict):
                return "%d.%d.%d.%d" % (
                    result.get('major', 0),
                    result.get('minor', 0),
                    result.get('patch', 0),
                    result.get('revision', 0),
                )
        except Exception:
            pass
        return None

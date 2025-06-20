class DojoUtil:
    def __init__(self, webdriver):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver

    def is_dojo(self):
        try:
            result = self.webdriver.execute_script('return this.dojo.version')
            if result is None:
                return False
            return True
        except Exception:
            pass
        return False

    def getVersionString(self):
        try:
            result = self.webdriver.execute_script('return this.dojo.version')
            return '%d.%d.%d.%d' % (
                result['major'],
                result['minor'],
                result['patch'],
                result['revision'],
            )
        except Exception:
            pass
        return None

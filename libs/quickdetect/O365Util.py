class O365Util:
    def __init__(self, webdriver, current_url, logger):
        self.webdriver = webdriver
        self.current_url = current_url
        self.logger = logger

    def has_ms_bookings(self):
        try:
            from selenium.webdriver.common.by import By
            frames = self.webdriver.find_elements(By.XPATH, "//iframe[contains(@src,'bookings')]")
            for frame in frames:
                src = frame.get_attribute('src')
                if src and 'office' in src:
                    return True
        except Exception:
            pass
        return False

    def is_office365(self):
        try:
            result = self.webdriver.execute_script("return typeof IsOwaPremiumBrowser !== 'undefined'")
            if result:
                return True
        except Exception:
            pass
        # look for office urls
        try:
            from selenium.webdriver.common.by import By
            tags = self.webdriver.find_elements(By.XPATH, "//script|//link|//iframe")
            for tag in tags:
                for attr in ['src', 'href']:
                    url = tag.get_attribute(attr)
                    if url and 'office' in url.lower():
                        return True
        except Exception:
            pass
        return False

    def domain_uses_office365(self):
        from libs.utils import get_root_domain
        import subprocess

        root_domain = get_root_domain(self.current_url)
        if not root_domain:
            return False
        # try dnspython
        try:
            import dns.resolver  # type: ignore
            answers = dns.resolver.resolve(root_domain, 'MX')
            for rdata in answers:
                exch = str(rdata.exchange).lower()
                if 'outlook' in exch or 'office365' in exch or 'microsoft' in exch:
                    return True
        except Exception:
            pass
        # fallback to dig command
        try:
            output = subprocess.check_output(['dig', '+short', root_domain, 'mx'], text=True, timeout=5)
            for line in output.splitlines():
                line = line.lower()
                if 'outlook' in line or 'office365' in line or 'microsoft' in line:
                    return True
        except Exception:
            pass
        return False


from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from urllib.parse import urljoin
import hashlib
import requests
from libs.utils.logger import FileLogger


class FaviconUtil:
    def __init__(self, webdriver: WebDriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def get_favicon_url(self):
        """Return the absolute favicon URL if found, else None."""
        try:
            elements = self.webdriver.find_elements(By.XPATH, "//link[contains(@rel, 'icon')]")
            if elements:
                href = elements[0].get_attribute('href')
                if href:
                    return urljoin(self.webdriver.current_url, href)
        except Exception as e:
            self.logger.error(f'Error retrieving favicon URL: {e}')
        return None

    def has_favicon(self) -> bool:
        return self.get_favicon_url() is not None

    def download_favicon(self, path: str) -> bool:
        """Download the favicon to ``path``. Return True on success."""
        url = self.get_favicon_url()
        if not url:
            return False
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(path, 'wb') as f:
                f.write(resp.content)
            return True
        except Exception as e:
            self.logger.error(f'Error downloading favicon: {e}')
        return False

    def get_favicon_md5(self):
        """Return the MD5 hash of the favicon contents, or None if not found."""
        url = self.get_favicon_url()
        if not url:
            return None
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return hashlib.md5(resp.content).hexdigest()
        except Exception as e:
            self.logger.error(f'Error fetching favicon for MD5: {e}')
        return None

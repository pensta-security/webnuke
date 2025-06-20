from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger


class ManifestUtil:
    def __init__(self, webdriver: WebDriver, logger=None):
        self.webdriver = webdriver
        self.logger = logger or FileLogger()

    def has_manifest(self) -> bool:
        try:
            self.webdriver.find_element(By.XPATH, "//link[@rel='manifest']")
            return True
        except Exception as e:
            self.logger.error(f'Error detecting manifest: {e}')
            return False

    def get_manifest_url(self):
        try:
            element = self.webdriver.find_element(By.XPATH, "//link[@rel='manifest']")
            return element.get_attribute('href')
        except Exception as e:
            self.logger.error(f'Error retrieving manifest URL: {e}')
            return None

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger
from .s3_helper import find_s3_urls

class AWSCommands:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.logger = logger or FileLogger()
        self.known_s3_hosts = ['.amazonaws.com']
        
    def show_bucket_report(self):
        self.logger.log("finding buckets...")
        for url in find_s3_urls(self.driver, self.known_s3_hosts):
            self.logger.log(url)
        self.logger.log("")
        self.logger.log("")
        input("Press ENTER to return to menu.")

    def extract_bucket_urls(self, xpath: str, attribute: str) -> None:
        """Generic helper to look for bucket URLs in matching elements."""
        for tag in self.driver.find_elements(By.XPATH, xpath):
            self.process_url(tag.get_attribute(attribute))
        
    def extract_bucket_urls_from_meta_tags(self):
        self.extract_bucket_urls("//meta", "content")

    def extract_bucket_urls_from_image_tags(self):
        self.extract_bucket_urls("//img", "src")

    def extract_bucket_urls_from_link_tags(self):
        self.extract_bucket_urls("//link", "href")

    def extract_bucket_urls_from_anchor_tags(self):
        self.extract_bucket_urls("//a", "href")

    def extract_bucket_urls_from_javascript_tags(self):
        self.extract_bucket_urls("//script", "src")

                        
    def process_url(self, url: str) -> None:
        """Log the URL if it belongs to a known S3 host."""
        if url and any(s3host in url for s3host in self.known_s3_hosts):
            self.logger.log(url)
    

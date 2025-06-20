from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from libs.utils.logger import FileLogger


class AWSS3Util:
    def __init__(self, webdriver, start_url, logger=None):
        self.version = 2.0
        self.beta = True
        self.webdriver = webdriver
        self.start_url = start_url
        self.end_url = self.webdriver.current_url
        self.known_s3_hosts = ['.amazonaws.com']
        self.logger = logger or FileLogger()
        self.bucket_urls = []
    

    
        
    def hasS3Buckets(self):
        self.bucket_urls = []

        def scan(xpath: str, attribute: str) -> None:
            for tag in self.webdriver.find_elements(By.XPATH, xpath):
                url = tag.get_attribute(attribute)
                if url:
                    for s3host in self.known_s3_hosts:
                        if s3host in url:
                            self.bucket_urls.append(url)
                            break

        try:
            scan("//meta", "content")
            scan("//img", "src")
            scan("//link", "href")
            scan("//script", "src")
            scan("//a", "href")
        except Exception:
            self.logger.error("ERRORORORORORO")
            raise

        return bool(self.bucket_urls)
        
    def getUrlString(self):
        return "S3 BUCKET"

    def get_bucket_urls(self):
        return self.bucket_urls
        

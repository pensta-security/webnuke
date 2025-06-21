from selenium import webdriver
import time
from libs.utils.logger import FileLogger
from libs.aws.s3_helper import find_s3_urls


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
        try:
            self.bucket_urls = find_s3_urls(self.webdriver, self.known_s3_hosts)
        except Exception:
            self.logger.error("ERRORORORORORO")
            raise

        return bool(self.bucket_urls)
        
    def getUrlString(self):
        return "S3 BUCKET"

    def get_bucket_urls(self):
        return self.bucket_urls
        

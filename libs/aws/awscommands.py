from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

class AWSCommands:
    def __init__(self, webdriver, logger):
        self.version = 0.1
        self.driver = webdriver
        self.logger = logger
        self.known_s3_hosts = ['.amazonaws.com']
        
    def show_bucket_report(self):
        print("finding buckets...")
        self.extract_bucket_urls_from_meta_tags()
        self.extract_bucket_urls_from_image_tags()
        self.extract_bucket_urls_from_link_tags()
        self.extract_bucket_urls_from_javascript_tags()
        self.extract_bucket_urls_from_anchor_tags()
        print('')
        print('')
        input("Press ENTER to return to menu.")
        
    def extract_bucket_urls_from_meta_tags(self):
        metatags = self.driver.find_elements(By.XPATH, "//meta")
        for tag in metatags:
            contenturl = tag.get_attribute('content')
            self.process_url(contenturl)

    def extract_bucket_urls_from_image_tags(self):
        metatags = self.driver.find_elements(By.XPATH, "//img")
        for tag in metatags:
            contenturl = tag.get_attribute('src')
            self.process_url(contenturl)

    def extract_bucket_urls_from_link_tags(self):
        metatags = self.driver.find_elements(By.XPATH, "//link")
        for tag in metatags:
            contenturl = tag.get_attribute('href')
            self.process_url(contenturl)

    def extract_bucket_urls_from_anchor_tags(self):
        metatags = self.driver.find_elements(By.XPATH, "//a")
        for tag in metatags:
            contenturl = tag.get_attribute('href')
            self.process_url(contenturl)


    def extract_bucket_urls_from_javascript_tags(self):
        metatags = self.driver.find_elements(By.XPATH, "//script")
        for tag in metatags:
            contenturl = tag.get_attribute('src')
            self.process_url(contenturl)

                        
    def process_url(self, url):
        if url:
            for s3host in self.known_s3_hosts:
                if s3host in url:
                    self.logger.log(url)
    

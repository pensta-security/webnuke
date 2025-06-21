from typing import List, Iterable
from selenium.webdriver.common.by import By


def find_s3_urls(driver, known_hosts: Iterable[str] | None = None) -> List[str]:
    """Return a list of S3 bucket URLs discovered in the current page."""
    hosts = list(known_hosts) if known_hosts is not None else ['.amazonaws.com']
    urls: List[str] = []
    searches = [
        ("//meta", "content"),
        ("//img", "src"),
        ("//link", "href"),
        ("//script", "src"),
        ("//a", "href"),
    ]
    for xpath, attr in searches:
        for tag in driver.find_elements(By.XPATH, xpath):
            url = tag.get_attribute(attr)
            if url and any(host in url for host in hosts):
                urls.append(url)
    return urls

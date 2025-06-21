from selenium.common.exceptions import (
    ElementNotInteractableException,
    ElementNotVisibleException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
import time
from libs.utils.logger import FileLogger
from libs.utils import wait_for_enter

class HTMLCommands:
    def __init__(self, webdriver, jsinjector, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.jsinjector = jsinjector
        self.logger = logger or FileLogger()

    def _load_url_with_retry(self, url: str, delay: int = 2) -> None:
        """Load a URL retrying on network disconnect errors."""
        while True:
            try:
                self.driver.get(url)
                break
            except WebDriverException as exc:
                if 'ERR_INTERNET_DISCONNECTED' in str(exc):
                    self.logger.error(
                        f'Internet disconnected while loading {url}. Retrying...'
                    )
                    time.sleep(delay)
                    continue
                raise
        
    def show_hidden_form_elements(self):
        self.jsinjector.execute_javascript(self.driver, 'wn_showHiddenFormElements()')
        self.logger.log('')
        self.logger.log('')
        wait_for_enter()

    def show_password_fields_as_text(self):
        self.jsinjector.execute_javascript(self.driver, 'wn_showPasswordFieldsAsText()')
        self.logger.log('')
        self.logger.log('')
        wait_for_enter()

    def see_all_html_elements(self):
        self.jsinjector.execute_javascript(self.driver, 'wn_showAllHTMLElements()')
        self.logger.log('')
        self.logger.log('')
        wait_for_enter()
    
    def remove_hidden_from_classnames(self):
        self.jsinjector.execute_javascript(self.driver, 'wn_remove_hidden_from_classnames()')
        self.logger.log('')
        self.logger.log('')
        wait_for_enter()
    def show_modals(self):
        self.jsinjector.execute_javascript(self.driver, 'wn_show_modals()')
        self.logger.log('')
        self.logger.log('')
        wait_for_enter()

    def refresh_page(self):
        """Refresh the current browser page."""
        self.driver.refresh()
        self.logger.log("Page refreshed")
        self.logger.log('')
        wait_for_enter()

    def _handle_navigation(self, start_url: str, do_reload: bool):
        """Return all elements on the page, reloading if needed."""
        if do_reload:
            self._load_url_with_retry(start_url)
        return self.driver.find_elements(By.XPATH, '//*')

    def _interact_with_element(self, element):
        """Click an element and wait briefly."""
        element.click()
        time.sleep(3)

    def _handle_click_error(self, exc, baseline_count, all_len):
        """Return (do_reload, continue_loop) based on the exception."""
        if isinstance(exc, ElementNotInteractableException):
            return False, True
        if isinstance(exc, ElementNotVisibleException):
            return False, True
        if isinstance(exc, IndexError):
            give_or_take = 10
            if baseline_count - all_len - give_or_take > 0:
                return True, True
            return False, False
        if isinstance(exc, StaleElementReferenceException):
            self.logger.debug("!!!STALE!!!")
            return True, True
        if isinstance(exc, WebDriverException):
            return False, True
        self.logger.error(f'Unexpected error clicking elements: {exc}')
        raise exc
        
    def click_everything(self):
        start_url = self.driver.current_url
        all_elements = self.driver.find_elements(By.XPATH, '//*')
        baseline_elements_count = len(all_elements)
        self.logger.log(
            "Found %d elements on page %s" % (baseline_elements_count, start_url)
        )

        urls_found = []
        do_page_reload = False
        self.logger.log("Clicking...")
        for current_index in range(baseline_elements_count):
            all_elements = self._handle_navigation(start_url, do_page_reload)

            try:
                do_page_reload = False
                current_element = all_elements[current_index]
                self._interact_with_element(current_element)

                if self.driver.current_url != start_url:
                    if self.driver.current_url not in urls_found:
                        urls_found.append(self.driver.current_url)
                    self.logger.log(
                        "%d/%d - %s" %
                        (current_index + 1, len(all_elements) + 1, self.driver.current_url)
                    )
                    do_page_reload = True

                after_click_elements = self.driver.find_elements(By.XPATH, '//*')
                if not do_page_reload and len(all_elements) != len(after_click_elements):
                    do_page_reload = True

            except Exception as e:  # handle known selenium errors
                do_page_reload, cont = self._handle_click_error(
                    e, baseline_elements_count, len(all_elements)
                )
                if not cont:
                    break
        self.logger.log('')
        self.logger.log('Found the following pages: ')
        for url in urls_found:
            self.logger.log("\t%s" % url)
        self.logger.log('')
        wait_for_enter()
        
    def type_into_everything(self):
        all_text_elements = self.driver.find_elements(By.XPATH, '//input[@type="text"]')
        for x in all_text_elements:
            x.send_keys("test")
        self.logger.log("'test' typed into %d text elements" % len(all_text_elements))

        all_text_elements = self.driver.find_elements(By.XPATH, '//input[@type="password"]')
        for x in all_text_elements:
            x.send_keys("test")
        self.logger.log("'test' typed into %d password elements" % len(all_text_elements))

        all_text_elements = self.driver.find_elements(By.XPATH, '//textarea')
        for x in all_text_elements:
            x.send_keys("test")
        self.logger.log("'test' typed into %d textarea elements" % len(all_text_elements))


        self.logger.log('')
        wait_for_enter()

    def favicon_info(self):
        """Download the page favicon or display its MD5 hash."""
        from libs.quickdetect.FaviconUtil import FaviconUtil

        util = FaviconUtil(self.driver, self.logger)
        url = util.get_favicon_url()
        if not url:
            self.logger.log('No favicon detected')
            self.logger.log('')
            wait_for_enter()
            return
        self.logger.log(f'Favicon URL: {url}')
        choice = input('Download favicon? [y/N]: ').strip().lower()
        if choice.startswith('y'):
            filename = 'favicon.ico'
            if util.download_favicon(filename):
                self.logger.log(f'Favicon saved to {filename}')
            else:
                self.logger.log('Failed to download favicon')
        md5 = util.get_favicon_md5()
        if md5:
            self.logger.log(f'Favicon MD5: {md5}')
        self.logger.log('')
        wait_for_enter()

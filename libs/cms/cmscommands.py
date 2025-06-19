from selenium.webdriver.common.by import By
from libs.quickdetect.WordPressUtil import WordPressUtil
from libs.quickdetect.DrupalUtil import DrupalUtil
from libs.quickdetect.SitecoreUtil import SitecoreUtil


class CMSCommands:
    def __init__(self, webdriver, cms_type, curses_util):
        self.version = 2.0
        self.driver = webdriver
        self.cms_type = cms_type.lower()
        self.curses_util = curses_util

    def _find_wordpress_plugins(self):
        plugins = set()
        try:
            elements = self.driver.find_elements(By.XPATH,
                "//link[contains(@href,'/wp-content/plugins/')]|//script[contains(@src,'/wp-content/plugins/')]")
            for el in elements:
                url = el.get_attribute('href') or el.get_attribute('src')
                if not url:
                    continue
                if '/wp-content/plugins/' in url:
                    part = url.split('/wp-content/plugins/')[1]
                    plugin = part.split('/')[0]
                    if plugin:
                        plugins.add(plugin)
        except Exception:
            pass
        return sorted(plugins)

    def _find_drupal_modules(self):
        modules = set()
        try:
            elements = self.driver.find_elements(By.XPATH,
                "//link[contains(@href,'/modules/')]|//script[contains(@src,'/modules/')]")
            for el in elements:
                url = el.get_attribute('href') or el.get_attribute('src')
                if not url:
                    continue
                if '/modules/' in url:
                    part = url.split('/modules/')[1]
                    module = part.split('/')[0]
                    if module:
                        modules.add(module)
        except Exception:
            pass
        return sorted(modules)

    def _find_sitecore_modules(self):
        modules = set()
        try:
            elements = self.driver.find_elements(By.XPATH,
                "//link[contains(@href,'sitecore')]|//script[contains(@src,'sitecore')]")
            for el in elements:
                url = el.get_attribute('href') or el.get_attribute('src')
                if not url:
                    continue
                url_lower = url.lower()
                if 'sitecore' in url_lower:
                    part = url_lower.split('sitecore')[1].lstrip('/')
                    module = part.split('/')[0]
                    if module:
                        modules.add(module)
        except Exception:
            pass
        return sorted(modules)

    def gather_info(self):
        version = None
        plugins = []
        if self.cms_type == 'wordpress':
            util = WordPressUtil(self.driver)
            version = util.getVersionString()
            plugins = self._find_wordpress_plugins()
        elif self.cms_type == 'drupal':
            util = DrupalUtil(self.driver)
            version = util.getVersionString()
            plugins = self._find_drupal_modules()
        elif self.cms_type == 'sitecore':
            util = SitecoreUtil(self.driver)
            version = util.get_version_string()
            plugins = self._find_sitecore_modules()
        return version, plugins

    def show(self):
        showscreen = True
        version, plugins = self.gather_info()
        while showscreen:
            screen = self.curses_util.get_screen()
            screen.addstr(2, 2, f"{self.cms_type.capitalize()} Information")
            line = 4
            if version:
                screen.addstr(line, 4, f"Version: {version}", curses.color_pair(2))
                line += 1
            if plugins:
                screen.addstr(line, 4, "Plugins:", curses.color_pair(2))
                line += 1
                for p in plugins:
                    screen.addstr(line, 6, p)
                    line += 1
            else:
                screen.addstr(line, 4, "No plugins detected")
                line += 1
            screen.addstr(22, 28, "PRESS M FOR MAIN MENU")
            screen.refresh()
            c = screen.getch()
            if c in (ord('M'), ord('m')):
                showscreen = False

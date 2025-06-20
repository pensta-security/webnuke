from selenium.webdriver.common.by import By
import curses
from urllib.parse import urlsplit, urljoin
from libs.quickdetect.WordPressUtil import WordPressUtil
from libs.quickdetect.DrupalUtil import DrupalUtil
from libs.quickdetect.SitecoreUtil import SitecoreUtil
from libs.utils.logger import FileLogger
import os


class CMSCommands:
    def __init__(self, webdriver, cms_type, curses_util, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.cms_type = cms_type.lower()
        self.curses_util = curses_util
        self.logger = logger or FileLogger()

    def _load_top_plugins(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if self.cms_type == 'wordpress':
            filename = 'wordpress_top_plugins.txt'
        elif self.cms_type == 'drupal':
            filename = 'drupal_top_modules.txt'
        else:
            return []
        path = os.path.join(data_dir, filename)
        plugins = []
        try:
            with open(path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        plugins.append(line)
        except Exception as e:
            self.logger.error(f'Error loading plugin list {filename}: {e}')
        self.logger.debug(f'Loaded {len(plugins)} plugins from {filename}')
        return plugins

    def _find_wordpress_plugins(self):
        plugins = set()
        try:
            elements = self.driver.find_elements(
                By.XPATH,
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
        except Exception as e:
            self.logger.error(f'Error finding WordPress plugins: {e}')
        self.logger.debug(f'Found WordPress plugins: {plugins}')
        return sorted(plugins)

    def _find_drupal_modules(self):
        modules = set()
        try:
            elements = self.driver.find_elements(
                By.XPATH,
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
        except Exception as e:
            self.logger.error(f'Error finding Drupal modules: {e}')
        self.logger.debug(f'Found Drupal modules: {modules}')
        return sorted(modules)

    def _find_sitecore_modules(self):
        modules = set()
        try:
            elements = self.driver.find_elements(
                By.XPATH,
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
        except Exception as e:
            self.logger.error(f'Error finding Sitecore modules: {e}')
        self.logger.debug(f'Found Sitecore modules: {modules}')
        return sorted(modules)

    def _check_url_exists(self, url):
        try:
            self.driver.get(url)
            text = (self.driver.title or "") + (self.driver.page_source or "")
            text = text.lower()
            if "404" in text or "not found" in text:
                return False
            return True
        except Exception as e:
            self.logger.error(f'Error checking URL {url}: {e}')
            return False

    def _enumerate_plugin_list(self, plugin_list):
        base = self.driver.current_url
        parts = urlsplit(base)
        base_root = f"{parts.scheme}://{parts.netloc}"
        found = []
        for path in plugin_list:
            full_url = urljoin(base_root, path.lstrip('/'))
            if self._check_url_exists(full_url):
                found.append(path)
        try:
            self.driver.get(base)
        except Exception:
            pass
        return found

    def gather_info(self):
        self.logger.debug(f'gather_info called for {self.cms_type}')
        version = None
        detected_plugins = []
        top_plugins = self._load_top_plugins()
        try:
            if self.cms_type == 'wordpress':
                util = WordPressUtil(self.driver)
                version = util.getVersionString()
                self.logger.debug(f'WordPress version: {version}')
                detected_plugins = self._find_wordpress_plugins()
            elif self.cms_type == 'drupal':
                util = DrupalUtil(self.driver)
                version = util.getVersionString()
                self.logger.debug(f'Drupal version: {version}')
                detected_plugins = self._find_drupal_modules()
            elif self.cms_type == 'sitecore':
                util = SitecoreUtil(self.driver)
                version = util.get_version_string()
                self.logger.debug(f'Sitecore version: {version}')
                detected_plugins = self._find_sitecore_modules()
        except Exception as e:
            self.logger.error(f'Error gathering CMS info: {e}')
        enumerated_plugins = self._enumerate_plugin_list(top_plugins)
        return version, detected_plugins, top_plugins, enumerated_plugins

    def show(self):
        showscreen = True
        self.logger.debug(f'Starting CMSCommands.show for {self.cms_type}')
        try:
            version, detected_plugins, top_plugins, enumerated_plugins = self.gather_info()
            self.logger.debug(f'Version: {version} | Plugins: {detected_plugins}')
            for p in top_plugins:
                self.logger.log(f'TOP {self.cms_type} plugin location: {p}')
            while showscreen:
                screen = self.curses_util.get_screen()
                height, _ = screen.getmaxyx()
                screen.addstr(2, 2, f"{self.cms_type.capitalize()} Information")
                line = 4
                if version:
                    screen.addstr(line, 4, f"Version: {version}", curses.color_pair(2))
                    line += 1
                if detected_plugins:
                    screen.addstr(line, 4, "Plugins:", curses.color_pair(2))
                    line += 1
                    max_lines = height - 3
                    for p in detected_plugins:
                        if line >= max_lines:
                            remaining = len(detected_plugins) - (line - 5)
                            screen.addstr(line, 6, f"...and {remaining} more")
                            line += 1
                            break
                        screen.addstr(line, 6, p)
                        line += 1
                else:
                    screen.addstr(line, 4, "No plugins detected")
                    line += 1
                if top_plugins:
                    screen.addstr(line, 4, "Common plugin locations:", curses.color_pair(2))
                    line += 1
                    max_lines = height - 3
                    for p in top_plugins:
                        if line >= max_lines:
                            remaining = len(top_plugins) - (line - 5 - len(detected_plugins))
                            screen.addstr(line, 6, f"...and {remaining} more")
                            line += 1
                            break
                        screen.addstr(line, 6, p)
                        line += 1
                if enumerated_plugins:
                    screen.addstr(line, 4, "Valid plugin locations:", curses.color_pair(2))
                    line += 1
                    max_lines = height - 3
                    for p in enumerated_plugins:
                        if line >= max_lines:
                            remaining = len(enumerated_plugins) - (line - 5 - len(detected_plugins) - len(top_plugins))
                            screen.addstr(line, 6, f"...and {remaining} more")
                            line += 1
                            break
                        screen.addstr(line, 6, p)
                        line += 1
                screen.addstr(22, 28, "PRESS M FOR MAIN MENU")
                screen.refresh()
                c = screen.getch()
                if c in (ord('M'), ord('m')):
                    showscreen = False
        except Exception as e:
            import traceback
            self.logger.error(f'Error displaying CMS info: {e}')
            self.logger.error(traceback.format_exc())
            self.curses_util.close_screen()
            raise
        self.logger.debug(f'Leaving CMSCommands.show for {self.cms_type}')

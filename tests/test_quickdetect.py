import unittest
import unittest.mock
from libs.quickdetect.WordPressUtil import WordPressUtil
from libs.quickdetect.DrupalUtil import DrupalUtil
from libs.quickdetect.WindowNameUtil import WindowNameUtil
from libs.quickdetect.ServiceWorkerUtil import ServiceWorkerUtil
from libs.quickdetect.ReactUtil import ReactUtil
from libs.quickdetect.VueUtil import VueUtil
from libs.quickdetect.SvelteUtil import SvelteUtil
from libs.quickdetect.EmberUtil import EmberUtil
from libs.quickdetect.NextJSUtil import NextJSUtil
from libs.quickdetect.GraphQLUtil import GraphQLUtil
from libs.quickdetect.ManifestUtil import ManifestUtil
from libs.quickdetect.WebSocketUtil import WebSocketUtil
from selenium.webdriver.common.by import By

class DummyElement:
    def __init__(self, attrs=None):
        self.attrs = attrs or {}
    def get_attribute(self, name):
        return self.attrs.get(name)

class DummyDriver:
    def __init__(self, elements=None):
        self.elements = elements or {}
    def find_element(self, by, value):
        if value in self.elements:
            return DummyElement(self.elements[value])
        raise Exception('not found')
    def find_elements(self, by, value):
        if value in self.elements:
            return [DummyElement(self.elements[value])]
        return []
    def execute_script(self, script):
        return None

class WordPressUtilTests(unittest.TestCase):
    def test_is_wordpress_true_when_generator_present(self):
        driver = DummyDriver({'//meta[@name=\'generator\']': {'content': 'WordPress 6.0'}})
        util = WordPressUtil(driver)
        self.assertTrue(util.isWordPress())

    def test_is_wordpress_false_when_generator_missing(self):
        driver = DummyDriver({'//meta[@name=\'generator\']': {'content': None}})
        util = WordPressUtil(driver)
        self.assertFalse(util.isWordPress())

    def test_is_wordpress_false_when_tag_absent(self):
        driver = DummyDriver()
        util = WordPressUtil(driver)
        self.assertFalse(util.isWordPress())
        self.assertIsNone(util.getVersionString())

class DrupalUtilTests(unittest.TestCase):
    def test_get_version_string_none_when_no_generator(self):
        driver = DummyDriver()
        util = DrupalUtil(driver)
        self.assertIsNone(util.getVersionString())


class WindowNameUtilTests(unittest.TestCase):
    def test_is_set_true_and_value(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return "payload"
        driver = Driver()
        util = WindowNameUtil(driver)
        self.assertTrue(util.is_set())
        self.assertEqual(util.get_value(), "payload")

    def test_is_set_false_when_empty(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return ""
        driver = Driver()
        util = WindowNameUtil(driver)
        self.assertFalse(util.is_set())


class ServiceWorkerUtilTests(unittest.TestCase):
    def test_service_worker_positive(self):
        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
            def execute_script(self, script):
                return True
            def execute_async_script(self, script):
                if 'active' in script:
                    return True
                return True
        driver = Driver()
        util = ServiceWorkerUtil(driver)
        self.assertTrue(util.is_supported())
        self.assertTrue(util.has_service_worker())
        self.assertTrue(util.is_running())

    def test_service_worker_negative(self):
        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
            def execute_script(self, script):
                return False
            def execute_async_script(self, script):
                return False
        driver = Driver()
        util = ServiceWorkerUtil(driver)
        self.assertFalse(util.is_supported())
        self.assertFalse(util.has_service_worker())
        self.assertFalse(util.is_running())


class ReactUtilTests(unittest.TestCase):
    def test_is_react_positive(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                if 'typeof React' in script:
                    return True
                if 'window.React && window.React.version' in script:
                    return '18.2.0'
        driver = Driver()
        util = ReactUtil(driver)
        self.assertTrue(util.is_react())
        self.assertEqual(util.get_version_string(), '18.2.0')

    def test_is_react_negative(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return None
        driver = Driver()
        util = ReactUtil(driver)
        self.assertFalse(util.is_react())
        self.assertIsNone(util.get_version_string())


class VueUtilTests(unittest.TestCase):
    def test_is_vue_positive(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                if 'typeof Vue' in script:
                    return True
                if 'window.Vue && window.Vue.version' in script:
                    return '3.2.0'
        driver = Driver()
        util = VueUtil(driver)
        self.assertTrue(util.is_vue())
        self.assertEqual(util.get_version_string(), '3.2.0')

    def test_is_vue_negative(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return None
        driver = Driver()
        util = VueUtil(driver)
        self.assertFalse(util.is_vue())
        self.assertIsNone(util.get_version_string())


class SvelteUtilTests(unittest.TestCase):
    def test_is_svelte_positive(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                if '__svelte' in script or 'data-svelte-h' in script:
                    return True
                if '__SVELTE_DEVTOOLS_GLOBAL_HOOK__' in script:
                    return '4.0.0'
        driver = Driver()
        util = SvelteUtil(driver)
        self.assertTrue(util.is_svelte())
        self.assertEqual(util.get_version_string(), '4.0.0')

    def test_is_svelte_negative(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return None
        driver = Driver()
        util = SvelteUtil(driver)
        self.assertFalse(util.is_svelte())
        self.assertIsNone(util.get_version_string())


class EmberUtilTests(unittest.TestCase):
    def test_is_ember_positive(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                if 'Ember.VERSION' in script:
                    return '4.9.0'
                if 'ember-cli' in script:
                    return '4.9.0'
                if 'window.Ember' in script or '__ember_root__' in script:
                    return True
        driver = Driver()
        util = EmberUtil(driver)
        self.assertTrue(util.is_ember())
        self.assertEqual(util.get_version_string(), '4.9.0')

    def test_is_ember_negative(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return None
        driver = Driver()
        util = EmberUtil(driver)
        self.assertFalse(util.is_ember())
        self.assertIsNone(util.get_version_string())


class NextJSUtilTests(unittest.TestCase):
    def test_is_nextjs_positive(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                if 'buildId' in script:
                    return '12345'
                if '__NEXT_DATA__' in script or '#__next' in script:
                    return True
        driver = Driver()
        util = NextJSUtil(driver)
        self.assertTrue(util.is_nextjs())
        self.assertEqual(util.get_version_string(), '12345')

    def test_is_nextjs_negative(self):
        class Driver(DummyDriver):
            def execute_script(self, script):
                return None
        driver = Driver()
        util = NextJSUtil(driver)
        self.assertFalse(util.is_nextjs())
        self.assertIsNone(util.get_version_string())


class GraphQLUtilTests(unittest.TestCase):
    def test_has_graphql_dom(self):
        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
                self.scripts = [
                    DummyElement({'src': '/graphql.js'}),
                ]

            def find_elements(self, by, value):
                if value == "//script":
                    return self.scripts
                return []

        driver = Driver()
        util = GraphQLUtil(driver)
        self.assertTrue(util.has_graphql())

    def test_has_graphql_network(self):
        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
                self.entries = ['/api/graphql']

            def find_elements(self, by, value):
                return []

            def execute_script(self, script):
                return self.entries

        driver = Driver()
        util = GraphQLUtil(driver)
        self.assertTrue(util.has_graphql())

    def test_has_graphql_negative(self):
        class Driver(DummyDriver):
            def find_elements(self, by, value):
                return []

            def execute_script(self, script):
                return []

        driver = Driver()
        util = GraphQLUtil(driver)
        self.assertFalse(util.has_graphql())


class ManifestUtilTests(unittest.TestCase):
    def test_has_manifest_and_url(self):
        driver = DummyDriver({'//link[@rel=\'manifest\']': {'href': '/test.webmanifest'}})
        util = ManifestUtil(driver)
        self.assertTrue(util.has_manifest())
        self.assertEqual(util.get_manifest_url(), '/test.webmanifest')

    def test_has_manifest_false(self):
        driver = DummyDriver()
        util = ManifestUtil(driver)
        self.assertFalse(util.has_manifest())
        self.assertIsNone(util.get_manifest_url())


class WebSocketUtilTests(unittest.TestCase):
    def test_has_websocket_scripts(self):
        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
                self.scripts = [
                    DummyElement({'src': 'ws://example.com/app.js'}),
                    DummyElement({'innerHTML': 'connect("wss://host")'})
                ]

            def find_elements(self, by, value):
                if value == "//script":
                    return self.scripts
                return []

            def execute_script(self, script):
                return []

        driver = Driver()
        util = WebSocketUtil(driver)
        self.assertTrue(util.has_websocket())

    def test_has_websocket_network(self):
        class Driver(DummyDriver):
            def find_elements(self, by, value):
                return []

            def execute_script(self, script):
                return ['wss://example.com/socket']

        driver = Driver()
        util = WebSocketUtil(driver)
        self.assertTrue(util.has_websocket())

    def test_has_websocket_negative(self):
        class Driver(DummyDriver):
            def find_elements(self, by, value):
                return []

            def execute_script(self, script):
                return []

        driver = Driver()
        util = WebSocketUtil(driver)
        self.assertFalse(util.has_websocket())


class QuickDetectScreenshotTests(unittest.TestCase):
    def test_run_saves_screenshot_when_path_given(self):
        class DummyLogger:
            def __init__(self):
                self.messages = []
            def log(self, text):
                self.messages.append(text)
            def error(self, text):
                self.messages.append(text)

        class Driver(DummyDriver):
            def __init__(self):
                super().__init__()
                self.saved = None
                self.current_url = 'http://example.com'
            def save_screenshot(self, path):
                self.saved = path
                return True

        class Screen:
            def addstr(self, *a, **k):
                pass
            def border(self, *a, **k):
                pass
            def clear(self):
                pass
            def refresh(self):
                pass
            def getch(self):
                return ord('m')

        class CursesUtil:
            def __init__(self, logger=None):
                pass
            def show_header(self):
                pass

        dummy = Driver()
        logger = DummyLogger()
        screen = Screen()
        curses_util = CursesUtil()

        # Patch detection utilities to no-ops so run() exits quickly
        from libs.quickdetect import QuickDetect as QDModule
        class DummyUtil:
            def __init__(self, *a, **kw):
                pass
            def __getattr__(self, name):
                return lambda *a, **kw: False

        with unittest.mock.patch('curses.color_pair', return_value=0), \
             unittest.mock.patch.multiple(
            QDModule,
            AngularUtilV2=DummyUtil,
            ReactUtil=DummyUtil,
            VueUtil=DummyUtil,
            SvelteUtil=DummyUtil,
            EmberUtil=DummyUtil,
            NextJSUtil=DummyUtil,
            GraphQLUtil=DummyUtil,
            WordPressUtil=DummyUtil,
            DrupalUtil=DummyUtil,
            SitecoreUtil=DummyUtil,
            JQueryUtil=DummyUtil,
            AWSS3Util=DummyUtil,
            CloudIPUtil=DummyUtil,
            MXEmailUtil=DummyUtil,
            O365Util=DummyUtil,
            DojoUtil=DummyUtil,
            WindowNameUtil=DummyUtil,
            OnMessageUtil=DummyUtil,
            ServiceWorkerUtil=DummyUtil,
            CSPUtil=DummyUtil,
            ManifestUtil=DummyUtil,
            WebSocketUtil=DummyUtil,
            SecurityHeadersUtil=DummyUtil,
        ):
            qd = QDModule.QuickDetect(screen, dummy, curses_util, logger)
            qd.run(screenshot_path='test.png')

        self.assertEqual(dummy.saved, 'test.png')

if __name__ == '__main__':
    unittest.main()

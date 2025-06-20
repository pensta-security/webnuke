import unittest
from libs.cms.cmscommands import CMSCommands

class DummyDriver:
    def __init__(self):
        self.current_url = 'http://example.com/'
        self.visited = []
        self.title = ''
        self.page_source = ''
    def get(self, url):
        self.visited.append(url)
        self.current_url = url
        if 'exists' in url:
            self.title = 'ok'
            self.page_source = 'plugin page'
        else:
            self.title = '404'
            self.page_source = 'Not Found'

class DummyCurses:
    pass

class CMSCommandsEnumerateTests(unittest.TestCase):
    def test_enumerate_plugin_list(self):
        driver = DummyDriver()
        cmds = CMSCommands(driver, 'wordpress', DummyCurses())
        plugins = ['/wp-content/plugins/exists', '/wp-content/plugins/missing']
        result = cmds._enumerate_plugin_list(plugins)
        self.assertEqual(result, ['/wp-content/plugins/exists'])
        self.assertIn('http://example.com/wp-content/plugins/exists', driver.visited)
        self.assertIn('http://example.com/wp-content/plugins/missing', driver.visited)

class CMSCommandsNewMethodTests(unittest.TestCase):
    def setUp(self):
        self.driver = DummyDriver()
        self.cmds = CMSCommands(self.driver, 'wordpress', DummyCurses())

    def test_detect_version(self):
        from unittest.mock import patch
        with patch('libs.cms.cmscommands.WordPressUtil') as util:
            util.return_value.getVersionString.return_value = '5.0'
            version = self.cmds._detect_version()
            self.assertEqual(version, '5.0')
            util.assert_called_once_with(self.driver)

    def test_discover_plugins(self):
        from unittest.mock import patch
        with patch.object(self.cmds, '_find_wordpress_plugins', return_value=['plug']):
            plugins = self.cmds._discover_plugins()
            self.assertEqual(plugins, ['plug'])


if __name__ == '__main__':
    unittest.main()


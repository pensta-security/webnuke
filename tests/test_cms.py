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

if __name__ == '__main__':
    unittest.main()

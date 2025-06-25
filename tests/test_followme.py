import unittest
from unittest.mock import patch, MagicMock

from libs.followme.followmecommands import FollowmeCommands
from libs.utils.logger import FileLogger


class DummyDriver:
    def __init__(self):
        self.current_url = ''
        self.quit_called = False

    def get(self, url):
        self.current_url = url

    def quit(self):
        self.quit_called = True


class FollowmeCommandsTests(unittest.TestCase):
    def setUp(self):
        self.main_driver = DummyDriver()
        self.logger = FileLogger()
        self.cmds = FollowmeCommands(self.main_driver, False, '', 0, self.logger)

    @patch('libs.followme.followmecommands.threading.Thread')
    @patch('libs.followme.followmecommands.WebDriverUtil.getDriver')
    def test_start_new_instance_creates_browser(self, mock_get_driver, mock_thread_class):
        browser = DummyDriver()
        mock_get_driver.return_value = browser
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        self.cmds.start_new_instance()
        self.assertIn(browser, self.cmds.running_browsers)
        mock_thread_class.assert_called_once()
        mock_thread.start.assert_called_once()
        self.assertIn(mock_thread, self.cmds.running_threads)

    def test_pause_and_resume(self):
        self.cmds.pause_all()
        self.assertTrue(self.cmds.get_paused())
        self.cmds.resume_all()
        self.assertFalse(self.cmds.get_paused())

    @patch('libs.followme.followmecommands.threading.Thread')
    @patch('libs.followme.followmecommands.WebDriverUtil.getDriver')
    def test_kill_all_stops_browsers(self, mock_get_driver, mock_thread_class):
        browser = DummyDriver()
        mock_get_driver.return_value = browser
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = True
        mock_thread_class.return_value = mock_thread
        self.cmds.start_new_instance()
        self.assertTrue(self.cmds.running_browsers)
        self.assertTrue(self.cmds.running_threads)
        self.cmds.kill_all()
        self.assertFalse(self.cmds.running_browsers)
        self.assertFalse(self.cmds.running_threads)
        self.assertFalse(self.cmds.run_thread)
        self.assertTrue(browser.quit_called)
        mock_thread.join.assert_called_once()

    @patch('libs.followme.followmecommands.WebDriverUtil.getDriverWithProxySupport')
    @patch('libs.followme.followmecommands.WebDriverUtil.getDriver')
    def test_create_browser_instance_no_proxy_when_port_none(self, mock_get_driver, mock_get_proxy_driver):
        self.cmds.proxy_host = 'localhost'
        self.cmds.proxy_port = None
        self.cmds.create_browser_instance()
        mock_get_driver.assert_called_once_with(self.logger)
        mock_get_proxy_driver.assert_not_called()


if __name__ == '__main__':
    unittest.main()

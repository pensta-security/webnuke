import unittest
from unittest.mock import patch

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

    @patch('libs.followme.followmecommands._thread.start_new_thread', return_value=None)
    @patch('libs.followme.followmecommands.WebDriverUtil.getDriver')
    def test_start_new_instance_creates_browser(self, mock_get_driver, mock_thread):
        browser = DummyDriver()
        mock_get_driver.return_value = browser
        self.cmds.start_new_instance()
        self.assertIn(browser, self.cmds.running_browsers)
        mock_thread.assert_called_once()

    def test_pause_and_resume(self):
        self.cmds.pause_all()
        self.assertTrue(self.cmds.get_paused())
        self.cmds.resume_all()
        self.assertFalse(self.cmds.get_paused())

    @patch('libs.followme.followmecommands._thread.start_new_thread', return_value=None)
    @patch('libs.followme.followmecommands.WebDriverUtil.getDriver')
    def test_kill_all_stops_browsers(self, mock_get_driver, _):
        browser = DummyDriver()
        mock_get_driver.return_value = browser
        self.cmds.start_new_instance()
        self.assertTrue(self.cmds.running_browsers)
        self.cmds.kill_all()
        self.assertFalse(self.cmds.running_browsers)
        self.assertFalse(self.cmds.run_thread)
        self.assertTrue(browser.quit_called)


if __name__ == '__main__':
    unittest.main()

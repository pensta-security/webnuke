import argparse
from libs.utils.WebDriverUtil import WebDriverUtil
from libs.utils.logger import FileLogger
from libs.quickdetect.QuickDetect import QuickDetect


class DummyScreen:
    """Simple stand-in for a curses screen that captures messages."""

    def __init__(self):
        self.lines = []

    def addstr(self, *args, **kwargs):
        if len(args) >= 3:
            text = str(args[2])
            self.lines.append(text)

    def border(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def refresh(self):
        pass

    def getch(self):
        # Immediately signal to exit the QuickDetect screen
        return ord('m')

    def getmaxyx(self):
        return (24, 80)


class DummyCursesUtil:
    """Minimal curses util replacement for CLI usage."""

    def __init__(self, logger, screen):
        self.logger = logger
        self.screen = screen

    def show_header(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(0, 28, " WEBNUKE V2.0 - BETA ")


def main():
    parser = argparse.ArgumentParser(description="Run QuickDetect on a URL")
    parser.add_argument("url", help="URL to scan")
    parser.add_argument("-l", "--log", dest="log_path", help="Path to log file")
    args = parser.parse_args()

    logger = FileLogger()
    if args.log_path:
        logger.log_path = args.log_path

    driver_util = WebDriverUtil()
    driver = driver_util.getDriver(logger)
    try:
        driver.get(args.url)
        screen = DummyScreen()
        curses_util = DummyCursesUtil(logger, screen)
        qd = QuickDetect(screen, driver, curses_util, logger)
        qd.run()
        for line in screen.lines:
            if line.strip() and "PRESS M" not in line and "WEBNUKE" not in line:
                print(line)
    finally:
        driver_util.quit_driver(driver)


if __name__ == "__main__":
    main()

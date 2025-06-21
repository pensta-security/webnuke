import argparse
import curses
import json
import sys
from libs.utils.WebDriverUtil import WebDriverUtil
from libs.utils.logger import FileLogger
from libs.quickdetect.QuickDetect import QuickDetect

_orig_color_pair = curses.color_pair

def _safe_color_pair(n: int) -> int:
    try:
        return _orig_color_pair(n)
    except curses.error:
        return 0

curses.color_pair = _safe_color_pair


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
    parser.add_argument("url", nargs="?", help="URL to scan")
    parser.add_argument(
        "-f",
        "--url-file",
        dest="url_file",
        help="Path to file containing URLs to scan, one per line",
    )
    parser.add_argument("-l", "--log", dest="log_path", help="Path to log file")
    parser.add_argument("-s", "--screenshot", dest="screenshot_path", help="Path to save page screenshot")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
    parser.add_argument(
        "--json",
        nargs="?",
        const="-",
        dest="json_path",
        help="Output results as JSON. Optionally specify a file path; defaults to stdout",
    )
    parser.add_argument(
        "--har",
        nargs="?",
        const="-",
        dest="har_path",
        help="Output HAR network data. Optionally specify a file path; defaults to stdout",
    )
    args = parser.parse_args()

    logger = FileLogger()
    if args.log_path:
        logger.log_path = args.log_path
    if hasattr(logger, 'clear'):
        logger.clear()

    urls = []
    if args.url:
        urls.append(args.url)
    if args.url_file:
        try:
            with open(args.url_file, "r", encoding="utf-8") as f:
                urls.extend([u.strip() for u in f if u.strip()])
        except OSError as exc:
            parser.error(f"Error reading URL file: {exc}")

    if not urls:
        parser.error("A URL or --url-file is required")

    driver_util = WebDriverUtil()
    driver = driver_util.getDriver(logger, headless=args.headless)
    results = []
    har_results = []
    try:
        for target in urls:
            driver.get(target)
            screen = DummyScreen()
            curses_util = DummyCursesUtil(logger, screen)
            qd = QuickDetect(screen, driver, curses_util, logger)
            qd.run(screenshot_path=args.screenshot_path)
            findings = [
                line.strip()
                for line in screen.lines
                if line.strip() and "PRESS M" not in line and "WEBNUKE" not in line
            ]
            results.append({"url": target, "findings": findings})
            if args.har_path is not None:
                har_results.append({"url": target, "har": qd.get_network_har()})

        if args.json_path is not None:
            if len(results) == 1 and args.har_path is None:
                data = json.dumps({"findings": results[0]["findings"]}, indent=2)
            else:
                data = json.dumps({"results": results}, indent=2)
            if args.json_path == "-":
                print(data)
            else:
                with open(args.json_path, "w", encoding="utf-8") as f:
                    f.write(data + "\n")
        else:
            for rec in results:
                for line in rec["findings"]:
                    print(line)

        if args.har_path is not None:
            har_output = har_results[0]["har"] if len(har_results) == 1 else har_results
            if args.har_path == "-":
                print(json.dumps(har_output, indent=2))
            else:
                with open(args.har_path, "w", encoding="utf-8") as f:
                    json.dump(har_output, f, indent=2)
                    f.write("\n")
    finally:
        driver_util.quit_driver(driver)


if __name__ == "__main__":
    main()

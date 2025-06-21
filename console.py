#!/usr/bin/env python3
# add owa to quickdetect - look for function IsOwaPremiumBrowser

import argparse
import traceback
from libs.utils.logger import FileLogger
from libs.mainmenu.mainframe import mainframe

def main():
        parser = argparse.ArgumentParser(description="Run Webnuke console")
        parser.add_argument("url", nargs="?", help="URL to open on startup")
        parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
        args = parser.parse_args()

        log_file = FileLogger()
        log_file.debug('Webnuke started.')

        try:
                mf = mainframe(log_file, headless=args.headless)
                if args.url:
                        mf.open_url(args.url)
                mf.show_main_screen()
        except Exception:
                log_file.error('ERROR RUNNING WEBNUKE.')
                log_file.error(traceback.format_exc())
                raise

        log_file.debug('Webnuke finished.')


if __name__ == '__main__':
        main()


		

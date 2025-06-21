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
        parser.add_argument(
            "--har",
            nargs="?",
            const="har_logs",
            default="har_logs",
            dest="har_path",
            help=(
                "Folder to save HAR network data when exiting the console. "
                "Defaults to ./har_logs"
            ),
        )
        parser.add_argument(
            "--import-har",
            dest="import_har",
            help="Path to HAR file to load for XSS tools",
        )
        parser.add_argument("--proxy-host", dest="proxy_host", help="Proxy server hostname or IP")
        parser.add_argument(
            "--proxy-port",
            dest="proxy_port",
            type=int,
            help="Proxy server port number",
        )
        args = parser.parse_args()

        log_file = FileLogger()
        if hasattr(log_file, 'clear'):
                log_file.clear()
        log_file.debug('Webnuke started.')

        try:
                mf = mainframe(
                    log_file,
                    headless=args.headless,
                    har_path=args.har_path,
                    proxy_host=args.proxy_host,
                    proxy_port=args.proxy_port,
                    import_har=args.import_har,
                )
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


		

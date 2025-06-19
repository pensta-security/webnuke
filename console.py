#!/usr/bin/env python3
# add owa to quickdetect - look for function IsOwaPremiumBrowser

from libs.utils.logger import *
from libs.mainmenu.mainframe import *
import sys
import traceback

if __name__ == '__main__':
        log_file = FileLogger()
        log_file.debug('Webnuke started.')

        try:
                mf = mainframe(log_file)
                if len(sys.argv) > 1:
                        mf.open_url(sys.argv[1])
                mf.show_main_screen()
        except Exception as e:
                log_file.error('ERROR RUNNING WEBNUKE.')
                log_file.error(traceback.format_exc())
                raise

        log_file.debug('Webnuke finished.')


		

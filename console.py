#!/usr/bin/env python3
# add owa to quickdetect - look for function IsOwaPremiumBrowser

from libs.utils.logger import *
from libs.mainmenu.mainframe import *
import sys

if __name__ == '__main__':
        log_file = FileLogger()
        log_file.log('Webnuke started.')

        try:
                mf = mainframe(log_file)
                if len(sys.argv) > 1:
                        mf.open_url(sys.argv[1])
                mf.show_main_screen()
        except:
                log_file.log('ERROR RUNNING WEBNUKE.')
                raise

        log_file.log('Webnuke finished.')


		

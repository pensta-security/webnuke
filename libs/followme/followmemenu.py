import time
from libs.followme.followmecommands import FollowmeCommands
from libs.utils import MenuHelper

class FollowmeScreen:
    def __init__(self, screen, webdriver, curses_util, debug, proxy_host, proxy_port, logger):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        
        self.curses_util = curses_util
        self.debug = debug
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.logger = logger
        self.commands = FollowmeCommands(self.driver, self.debug, self.proxy_host, self.proxy_port, self.logger)
        self.followme_count = 0
        
        
        
        
                

    def run(self):
        def build_items():
            paused = self.commands.get_paused()
            items = [
                ('1', "Start new follow me", self._start_new_instance),
            ]
            if not paused:
                items.append(('2', "PAUSE follow me", self.commands.pause_all))
            if paused:
                items.append(('3', "RESUME follow me", self.commands.resume_all))
            items.append(('4', "Kill all running instances", self._kill_all))
            return items

        def draw(screen):
            screen.addstr(11, 2, "Followme running instances: "+str(self.followme_count))
            return 4

        def footer(screen):
            if self.commands.get_paused():
                screen.addstr(23, 28, "| -  P A U S E D   - |")

        # Use MenuHelper with extra footer drawing
        def extra_draw(screen):
            line = draw(screen)
            footer(screen)
            return line

        MenuHelper.run(self.curses_util, "Follow Me", build_items, extra_draw=extra_draw)
        return

    def _start_new_instance(self):
        try:
            self.commands.start_new_instance()
            self.followme_count += 1
        except Exception:
            self.logger.error("ERROR")
            self.logger.log("EEE - error at start new followme instance")
            raise

    def _kill_all(self):
        self.commands.kill_all()
        self.followme_count = 0

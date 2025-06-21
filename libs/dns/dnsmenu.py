from libs.dns.dnscommands import DNSCommands
from libs.utils import MenuHelper


class DNSScreen:
    def __init__(self, screen, curses_util, driver, history, logger):
        self.screen = screen
        self.curses_util = curses_util
        self.driver = driver
        self.logger = logger
        self.history = history
        self.commands = DNSCommands(driver, curses_util, logger, history)

    def show(self):
        items = [
            ('1', 'Show DNS info', self.commands.show_dns_info),
            ('2', 'Domain history', self.commands.show_history),
        ]
        MenuHelper.run(self.curses_util, 'DNS', items)
        return

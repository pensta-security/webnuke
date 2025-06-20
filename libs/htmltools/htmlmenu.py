import curses
from selenium.common.exceptions import WebDriverException
from libs.htmltools.htmlcommands import *
from libs.htmltools.htmltoolsscript import *
from libs.utils import MenuHelper

class HTMLScreen:
    def __init__(self, screen, webdriver, curses_util, jsinjector):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        
        self.curses_util = curses_util
        self.jsinjector = jsinjector
        
        self.commands = HTMLCommands(self.driver, self.jsinjector)
        
        
        
    
        
    

    def show(self):
        items = [
            ('1', "Show hidden form elements", self.commands.show_hidden_form_elements),
            ('2', "Turn password fields into text", self.commands.show_password_fields_as_text),
            ('3', "Turn css visibility on for all HTML elements", self.commands.see_all_html_elements),
            ('4', "Click every element on the page", self.commands.click_everything),
            ('5', "Type 'test' into every text box", self.commands.type_into_everything),
            ('6', "Removes hidden & hide from classnames", self.commands.remove_hidden_from_classnames),
            ('7', "Show all modals  (modal fade -> modal fade show)", self.commands.show_modals),
        ]
        MenuHelper.run(self.curses_util, "HTML Tools", items)
        return

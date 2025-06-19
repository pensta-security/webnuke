import curses
from selenium.common.exceptions import WebDriverException
from libs.htmltools.htmlcommands import *
from libs.htmltools.htmltoolsscript import *

class HTMLScreen:
    def __init__(self, screen, webdriver, curses_util, jsinjector):
        self.version = 2.0
        self.screen = screen
        self.driver = webdriver
        
        self.curses_util = curses_util
        self.jsinjector = jsinjector
        
        self.commands = HTMLCommands(self.driver, self.jsinjector)
        
        
    def show(self):
        showscreen = True
        
        while showscreen:
            self.screen = self.curses_util.get_screen()
            self.screen.addstr(2, 2, "HTML Tools")
            self.screen.addstr(4, 5, "1) Show hidden form elements") # good demo url for this.... https://www.wufoo.com/html5/types/11-hidden.html
            self.screen.addstr(5, 5, "2) Turn password fields into text") 
            self.screen.addstr(6, 5, "3) Turn css visibility on for all HTML elements") 
            self.screen.addstr(7, 5, "4) Click every element on the page") 
            self.screen.addstr(8, 5, "5) Type 'test' into every text box")
            self.screen.addstr(9, 5, "6) Removes hidden & hide from classnames")
            self.screen.addstr(10, 5,"7) Show all modals  (modal fade -> modal fade show)")


            
            self.screen.addstr(22, 28, "PRESS M FOR MAIN MENU")
            self.screen.refresh()
            
            c = self.screen.getch()
            if c == ord('M') or c == ord('m'):
                showscreen=False
                
            if c == ord('1'):
                self.curses_util.close_screen()
                self.commands.show_hidden_form_elements()
                
            if c == ord('2'):
                self.curses_util.close_screen()
                self.commands.show_password_fields_as_text()
                
            if c == ord('3'):
                self.curses_util.close_screen()
                self.commands.see_all_html_elements()

            if c == ord('4'):
                self.curses_util.close_screen()
                self.commands.click_everything()

            if c == ord('5'):
                self.curses_util.close_screen()
                self.commands.type_into_everything()
            if c == ord('6'):
                self.curses_util.close_screen()
                self.commands.remove_hidden_from_classnames()
            if c == ord('7'):
                self.curses_util.close_screen()
                self.commands.show_modals()
                                
        return
        
    
        
    

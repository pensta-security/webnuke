from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from libs.utils.logger import FileLogger

class BruteLoginCommands:
    def __init__(self, webdriver, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.logger = logger or FileLogger()
        
    def start_brute_force(self):
        input("Enter nukeuser into username field amd nukepass into password field then press ENTER to continue")
        
        username_field_id = ''
        password_field_id = ''
        login_url = self.driver.current_url
        
        username_htmlfield = self.driver.find_elements(By.XPATH, "//input")
        for x in username_htmlfield:
            try:                
                if x.get_attribute('value') == 'nukeuser':
                    username_field_id = x.get_attribute('id')

                if x.get_attribute('value') == 'nukepass':
                    password_field_id = x.get_attribute('id')
            except Exception as e:
                self.logger.error(f'Error identifying login fields: {e}')
        self.logger.log('')
        self.logger.log("Username field is "+username_field_id)
        self.logger.log("Password field is "+password_field_id)
        
        runscan = True
        if username_field_id == '':
            runscan = False
            self.logger.log("No username field found!")
            
        if password_field_id == '':
            runscan = False
            self.logger.log("No password field found!")
        
        
        if runscan:
            self.try_logins(login_url, username_field_id, password_field_id)
        else:
            self.logger.log("Could not brute force login page! no username or password field found!")

        self.logger.log('')
        self.logger.log('')
        input("Press ENTER to return to menu.")
    
    def try_logins(self, loginurl, userfield, passfield):
        users=['bert', 'jimmyj']
        passwords = ['password1', 'password2']
        
        for current_user in users:
            for current_password in passwords:
                self.driver.get(loginurl)
                username_html_field = self.driver.find_element(By.ID, userfield)
                password_html_field = self.driver.find_element(By.ID, passfield)
                username_html_field.send_keys(current_user)
                password_html_field.send_keys(current_password)
                password_html_field.submit()
                
        
    

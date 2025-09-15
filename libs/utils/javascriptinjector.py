from selenium.common.exceptions import WebDriverException, UnexpectedAlertPresentException
from libs.utils.logger import FileLogger

class JavascriptInjector:
    def __init__(self, logger=None):
        self.version = 2.0
        self.logger = logger or FileLogger()
        self.jsfunctions = []
        self.javascript_block = ""
        self.help_block = []
        
    def inject_js(self, javascript):
        self.javascript_block+=javascript
        
    def add_help_topic(self, jsfunction, description):
        self.jsfunctions.append(jsfunction)
        self.help_block.append({'function': jsfunction, 'description': description})
        
    def get_js_block(self):
        wnhelp_block = """window.wn_help = function(){
    console.log('webnuke: HELP!!');
    console.log('-=-=-=-=-=-=-=-');"""
        for x in self.help_block:
            wnhelp_block+="console.log('"+x['function']+" - "+x['description']+"');"
        wnhelp_block+='};'
    
        return self.javascript_block+wnhelp_block
    
    def add_js_file(self, filepath):
        with open(filepath, 'r') as myfile:
            contents = myfile.read()
            self.inject_js(contents)

    def install_custom_javascript_functions(self, driver):      
        javascript = """window.console = {log: function(data){this.output.push(data);}, warn: function(data){this.output.push("WARN: "+data);}, error: function(data){this.output.push("ERROR: "+data);}, output: [], flushOutput: function(){var rtndata = this.output; this.output=[]; return rtndata;}};         
                        
                        """+self.get_js_block()
        try:
            driver.execute_script(javascript)
        except UnexpectedAlertPresentException as e:
            try:
                alert = driver.switch_to.alert
                alert.dismiss()
            except Exception:
                pass
            self.logger.error(f'Error injecting JavaScript: {e}')
            driver.execute_script(javascript)
        except Exception as e:
            self.logger.error(f'Error injecting JavaScript: {e}')
            raise
            
    def execute_javascript(self, driver, javascript):
        self.install_custom_javascript_functions(driver)
        try:
            amended_javascript="""window.wn_webnuke = function(){"""+javascript+""";}; wn_webnuke(); return window.console.flushOutput() """
            result = driver.execute_script(amended_javascript)
            if result is not None:
                for result_line in result:
                    self.logger.log(result_line)
        except WebDriverException as e:
            self.logger.error("ERROR with webdriver: %s" % str(e))
            self.logger.error(javascript)
            self.logger.log('')
        except Exception as e:
            self.logger.error(f'Error executing JavaScript: {e}')
            raise
            
        self.logger.log('')

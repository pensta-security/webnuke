from selenium.common.exceptions import WebDriverException
from libs.jsconsole.jsconsolescript import *
from libs.utils.logger import FileLogger
        

class JSConsole:
    def __init__(self, webdriver, jsinjector, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.jsinjector = jsinjector
        self.logger = logger or FileLogger()

        
    def run(self):
        self.logger.log("JSCONSOLE (type quit to exit) - dont forget to drop the bomb @@@")
        self.logger.log('')
        self.execute_javascript('wn_help()')
        
        
        sentinel = '@@@'  # drop the bomb!!! ends when this string is seen,
        fullline = ''
        for line in iter(input, sentinel):
            fullline += line
            pass
        
        while fullline.startswith('quit') is not True:
            self.execute_javascript(fullline)
            
            fullline = ''
            for line in iter(input, sentinel):
                fullline += line
                pass
                
    def install_custom_javascript_functions(self):
        javascript = """window.console = {log: function(data){this.output.push(data);}, warn: function(data){this.output.push("WARN: "+data);}, error: function(data){this.output.push("ERROR: "+data);}, output: [], flushOutput: function(){var rtndata = this.output; this.output=[]; return rtndata;}};
                        
                        """+self.jsinjector.get_js_block()
        
        try:
            self.driver.execute_script(javascript)
        except Exception as e:
            self.logger.error(f'Error injecting JavaScript: {e}')
            raise

    def execute_javascript(self, javascript):
        self.install_custom_javascript_functions()
        try:
            amended_javascript="""window.webnuke = function(){"""+javascript+""";}; webnuke(); return window.console.flushOutput() """
            result = self.driver.execute_script(amended_javascript)
            if result is not None:
                for result_line in result:
                    self.logger.log(result_line)
        except WebDriverException:
            # ignore any web driver errors
            ##print "ERROR with webdriver"
            #print javascript
            #print ''
            pass
        except Exception as e:
            self.logger.error(f'Error executing JavaScript: {e}')
            raise
            
        self.logger.log('')
    

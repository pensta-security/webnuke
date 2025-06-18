from selenium.common.exceptions import WebDriverException
from libs.jsconsole.jsconsolescript import *
        

class JSConsole:
    def __init__(self, webdriver, jsinjector):
        self.version = 0.1
        self.driver = webdriver
        self.jsinjector = jsinjector

        
    def run(self):
        print("JSCONSOLE (type quit to exit) - dont forget to drop the bomb @@@")
        print('')
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
        except:
            raise

    def execute_javascript(self, javascript):
        self.install_custom_javascript_functions()
        try:
            amended_javascript="""window.webnuke = function(){"""+javascript+""";}; webnuke(); return window.console.flushOutput() """
            result = self.driver.execute_script(amended_javascript)
            if result is not None:
                for result_line in result:
                    print(result_line)
        except WebDriverException:
            # ignore any web driver errors
            ##print "ERROR with webdriver"
            #print javascript
            #print ''
            pass
        except:
            raise
            
        print('')
    

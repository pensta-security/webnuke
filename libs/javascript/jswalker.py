from selenium.common.exceptions import WebDriverException
import sys
from libs.utils.logger import FileLogger


class JSWalker:
    def __init__(self, webdriver, jsinjector, logger=None):
        self.version = 2.0
        self.driver = webdriver
        self.jsinjector = jsinjector
        self.logger = logger or FileLogger()
        self.jsinjector.add_js_file('libs/javascript/js/walk_functions.js')
    
    def start_walk_tree(self):
        self.jsinjector.install_custom_javascript_functions(self.driver)
        self.walk_tree('this','this')
        self.logger.log('')
        self.logger.log('')
        input("Press ENTER to return to menu.")


    def walk_tree(self, rootnode, fullpath):
        javascript="return wn_walk_functions(%s, '%s');"%(rootnode, fullpath)       
        jsresults = self.executeJavascriptAndReturnArray(javascript)
        #print jsresults
        for record in jsresults:
            recordtype = record['type']
            fullpath = record['fullpath']
            if recordtype == 'function':
                confirmed = self.confirm("Do you want to run javascript function '"+fullpath+"'?")
                if confirmed:
                    self.logger.log("running function "+fullpath+"();")
                    self.jsinjector.execute_javascript(self.driver, fullpath+"();")
            if recordtype == 'object':
                confirmed = self.confirm("Do you want to walk '"+fullpath+"'?")
                if confirmed:
                    self.logger.log("walking object "+fullpath+"")
                    self.walk_tree(fullpath, fullpath)
            #print "%s [%s]"%(record['fullpath'], record['type'])
        
        
    def run_lone_javascript_functions(self):
        self.logger.log("getting global window object")
        globalitems=[]
        noargfunctions=[]
        properrors=0
        try:
            javascript="jsproberesults=[];for (name in this) {  try{jsproberesults.push( {'name':''+name, 'value': ''+this[name]})}catch(err){var anyerror='ignore'};};return jsproberesults"
            jsresults = self.executeJavascriptAndReturnArray(javascript)
            for logline in jsresults:
                if '[native code]' not in logline['value'] and 'jsproberesults' not in logline['name']:
                    globalitems.append(logline)
            
            self.logger.log(str(len(globalitems))+' global items found')
            for record in globalitems:
                if not record['name'].startswith('wn_'):
                    if record['value'].startswith('function '+record['name']+'()') or record['value'].startswith('function ()'):
                        noargfunctions.append(record['name'])
                    #print '\t'+record['name']+': '+record['value']
            
            
            self.logger.log("Found "+str(len(noargfunctions))+" lone Javascript functions")
            for record in noargfunctions:
                self.logger.log("\t"+record)
            self.logger.log("")
            
            if len(noargfunctions) > 0: 
                self.logger.log("Calling "+str(len(noargfunctions))+" lone Javascript functions")
                for record in noargfunctions:
                    if not record.startswith("wn_"):
                        self.logger.log("\tCalling %s()"%record)
                        javascript = record+"()"
                        try:
                            self.driver.execute_script(javascript)
                        except Exception as e:
                            self.logger.error(f'Error executing {javascript}: {e}')
            
                
        except WebDriverException as e:
            self.logger.error("Selenium Exception: Message: " + str(e))
        except Exception as e:
            self.logger.error(f'Unexpected error: {e}')
            self.logger.error('probe_window FAILED')
            self.logger.error(f"Unexpected error: {sys.exc_info()[0]}")
            raise

        self.logger.log('')
        input("Press ENTER to return to menu.")


            
    def executeJavascriptAndReturnArray(self, javascript):
        try:
            return self.driver.execute_script(javascript)
        except WebDriverException as e:
            self.logger.error("Selenium Exception: Message: " + str(e))
        except Exception as e:
            self.logger.error(f'Unexpected error: {e}')
            self.logger.error('probe_window FAILED')
            self.logger.error(f"Unexpected error: {sys.exc_info()[0]}")
            raise
    
    def confirm(self, message):
        bah = input(message+" (Y/n):")
        if bah == 'Y' or bah == 'y' or bah == '':
            return True
        if bah == 'N' or bah == 'n':    
            return False
        return self.confirm(message)

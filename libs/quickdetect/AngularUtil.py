from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from libs.utils.logger import FileLogger
class AngularUtilV2:
    def __init__(self, webdriver, start_url, logger=None):
        self.version = 2.0
        self.beta = True
        self.logger = logger or FileLogger()
        self.webdriver = webdriver
        self.start_url = start_url
        self.end_url = self.webdriver.current_url
        
    def isAngularApp(self):
        try:
            result = self.webdriver.execute_script("return (typeof window.angular != 'undefined')")
            #self.webdriver.execute_script('console.log(self.angular)')
            if result == None:
                return False
            return result
        except Exception as e:
            self.logger.error(f'Error checking for Angular app: {e}')
            raise
        return False
        
    def getVersionString(self):
        try:
            result = self.webdriver.execute_script('return self.angular.version.full')
            return result
        except Exception as e:
            self.logger.error(f'Error retrieving Angular version: {e}')
        return None
        
    def get_application_name(self):
        result = self.webdriver.find_element(By.XPATH, "//*[@ng-app]")
        return result.get_attribute("ng-app")
        
        
    def extract_dependencies(self, application_name, rtnData):
        record_exists = False
        for data_record in rtnData:
            if data_record['name'] == application_name:
                record_exists = True
                
        if record_exists == False:
            javascript = """var rtnData = [];
                            angular.forEach(angular.module('"""+application_name+"""').requires, function(m) {rtnData.push(m)});
                            return rtnData"""
            result = self.webdriver.execute_script(javascript)
            rtnData.append({'name': application_name, 'dependencies': result})
            for record in result:
                self.extract_dependencies(record, rtnData)
        return rtnData
        
    def get_dependencies(self, application_name):
        javascript = """var rtnData = [];
                        angular.forEach(angular.module('"""+application_name+"""').requires, function(m) {rtnData.push(m)});
                        return rtnData"""
        result = self.webdriver.execute_script(javascript)
        return result
        
    def get_components_from_dep_name(self, dep_name):
        javascript = """var rtnData = [];
                        angular.module('"""+dep_name+"""')['_invokeQueue'].forEach(function(value){ 
                            var sourcecode="not working...";
                            if(value[2].length == 2){
                                sourcecode = value[2][1].toString();
                            }
                            rtnData.push({'angular_type': value[1], 'name': value[2][0], 'sourcecode': sourcecode});
                        });
                        return rtnData"""
        result = self.webdriver.execute_script(javascript)
        return result
        
    def get_components_from_controller(self, controller_name):
        try:
            javascript = """var res = angular.element(document.body).injector().get('$controller');  
                            var controller = res('"""+controller_name+"""', {})
                            return controller.constructor.$inject"""
            result = self.webdriver.execute_script(javascript)
            return result
        except Exception as e:
            self.logger.error(f'Error getting controller components: {e}')
        
        return []
        
    def get_components_from_component_name(self, component_name):
        try:
            javascript = """var res = angular.element(document.body).injector().get('"""+component_name+"""'); 
                            var rtnData = []
                            for (prop in res) {
                                var mytype = typeof(res[prop]);
                                if(mytype=="string" || mytype == "number" || mytype == "boolean"){
                                    rtnData.push({'name': prop, 'value': res[prop], 'type': mytype});
                                }
                                if(mytype=="object"){
                                    rtnData.push({'name': prop, 'value': '', 'type': mytype});
                                }
                            }
                            return rtnData"""
                            
            result = self.webdriver.execute_script(javascript)
            return result
        except Exception as e:
            self.logger.error(f'Error getting component info: {e}')
        
        return []

class AngularUtil:
    def __init__(self, logger=None):
        self.version = 2.0
        self.beta = True
        self.debug = False
        self.logger = logger or FileLogger()
        
    def setDebug(self, newValue):
        self.debug = newValue
        
    def getAngularAppName(self, webdriver):
        result = webdriver.find_element(By.XPATH, "//*[@ng-app]")
        return result.get_attribute("ng-app")
        
    def isAngularApp(self, webdriver):
        result = []
        try:
            result = webdriver.execute_script('return self.angular')
            return len(result) > 0
        except Exception as e:
            self.logger.error(f'Error checking Angular app: {e}')
        
        return False
        
    def getApplicationParts(self, webdriver):
        rtnData = []
        app_name = self.getAngularAppName(webdriver)
        parts_javascript =  """var parts=[];
                                angular.module('"""+app_name+"""')['_invokeQueue'].forEach(function(value){
                                    var items = value[2][1];
                                    isarray = items instanceof Array;
                                    if(isarray){
                                        var newdic = items.slice(0, -1);
                                        var source = items[items.length-1];
                                        var record = {'parttype': value[1], 'name': value[2][0], 'components': newdic, 'sourcecode': source}
                                        parts.push(record);
                                    }
                                    else{
                                        var source = items;
                                        var components = source.$inject
                                        var record = {'parttype': value[1], 'name': value[2][0], 'sourcecode': source, 'components': components};
                                        parts.push(record);
                                    }
                                });
                                return parts"""
                                
        result = webdriver.execute_script(parts_javascript)
        self.logger.log("\tAngular Parts")
        for part in result:
            self.logger.log("\t\t%s : %s ( %s )" % (part['parttype'], part['name'], ', '.join(part['components'])))
            
        for part in result:
            urls_found = find_urls_from_source_code(part['sourcecode'])
            if len(urls_found) > 0:
                self.logger.log("%s ( %s )" % (part['name'], ', '.join(part['components'])))
                #print part['sourcecode']
                for potential_url_string in urls_found:
                    self.logger.log(potential_url_string)
                self.logger.log("-"*100)
                
        for part in result:
            for component in part['components']:
                rtnData.append(component)
                
        return rtnData
            
    def detect_routes_from_ui_router(self, webdriver):
        rtnData = []
        get_routes_javascript = """var rtnData = [];
                                    var state = angular.element(document.body).injector().get('$state')
                                    routes = state.get();
                                    routes.forEach(function(value){rtnData.push({'url': value.url, 'controller': value.controller})});
                                    return rtnData
                                    """
        result = webdriver.execute_script(get_routes_javascript)
        if len(result)>0:
            self.logger.log("Routes Found:")
            for url in result:
                rtnData.append(url)
                self.logger.log("\t#%s - %s" % (url['url'], url['controller']))
        self.logger.log('')
        return rtnData
        
    def get_application_classitem(self, webdriver, classname_to_load):
        rtnData = []
        #ignore any classes starting with a dollar sign...
        if classname_to_load.startswith('$'):
            return []
            
        if classname_to_load.endswith('Provider'):
            self.logger.log("oldCLASS "+classname_to_load)
            classname_to_load=classname_to_load[0:-8]
            self.logger.log("newCLASS "+classname_to_load)
            
        results = []
        
        try:
            javascript = """var res = angular.element(document.body).injector().get('"""+classname_to_load+"""');
                            var rtnData = []
                            for (prop in res) {
                                var mytype = typeof(res[prop]);
                                if(mytype=="string" || mytype == "number" || mytype == "boolean"){
                                    rtnData.push({'name': prop, 'value': res[prop], 'type': mytype});
                                }
                                if(mytype=="object"){
                                    rtnData.push({'name': prop, 'value': '', 'type': mytype});
                                }
                                
                            }
                            return rtnData"""               
            result = webdriver.execute_script(javascript)
            if len(result) >0:
                for result_item in result:
                    rtnData.append(result_item)
        except Exception as e:
            self.logger.error(f'error@get_application_classitem: {e}')
            
        return rtnData

    def get_controller_info(self, webdriver, controller_name):
        self.logger.log("GCI")
        self.logger.log(controller_name)
        javascript = """var res = angular.element(document.body).injector().get('$controller');  
                        var controller = res('"""+controller_name+"""', {})
                        var rtnData = []
                        for (prop in controller) {
                            var mytype = typeof(controller[prop]);
                            if(mytype=="string" || mytype == "number" || mytype == "boolean"){
                                rtnData.push({'name': prop, 'value': controller[prop], 'type': mytype});
                            }
                            if(mytype=="object"){
                                rtnData.push({'name': prop, 'value': '', 'type': mytype});
                            }
                        }
                        return rtnData"""
        
        try:
            result = webdriver.execute_script(javascript)
        except Exception as e:
            self.logger.error(f'error@get_controller_info: {e}')
            return []
            
        return result


def find_urls_from_source_code(source_code):
    urls = []
    for line in source_code.split():
        #print line
        if "'/" in line or '"/' in line:
            urls.append(line)
    return urls

